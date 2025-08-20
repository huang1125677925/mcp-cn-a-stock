import json
import logging
import os
import time
from typing import Dict, List

import numpy as np
from qtf import msd_fetch_once, pre_adjustment

logger = logging.getLogger("qtf_mcp")

msd_host = os.environ.get("MSD_HOST", "")
stock_sector_data = os.environ.get("STOCK_TO_SECTOR_DATA", "confs/stock_sector.json")

if msd_host == "":
  logger.error("MSD_HOST is not set")
  raise ValueError("MSD_HOST is not set")


STOCK_SECTOR: Dict[str, List[str]] | None = None


def get_stock_sector() -> Dict[str, List[str]]:
  global STOCK_SECTOR
  if STOCK_SECTOR is None:
    with open(stock_sector_data, "r", encoding="utf-8") as f:
      STOCK_SECTOR = json.load(f)
  return STOCK_SECTOR if STOCK_SECTOR is not None else {}


async def load_data_msd(
  symbol: str, start_date: str, end_date: str, n: int = 0, who: str = ""
) -> Dict[str, np.ndarray]:
  # logger.info(f"align data {symbol} cost {t3 - t2} seconds")
  datas = load_data_msd_batch([symbol], start_date, end_date, n, who)

  return datas.get(symbol, {})


def align_date_fill(base: np.ndarray, target: np.ndarray) -> np.ndarray:
  """
  return index of target that target[index] >= base[i]
  """
  index = np.searchsorted(target, base, side="right")
  index = index - 1
  index[index < 0] = 0
  return index


def symbol_sqls(sqls: Dict[str, str], symbol: str, start_date: str, end_date: str):
  sql1 = f"SELECT * FROM kline1d.{symbol} WHERE __date__ BETWEEN '{start_date}' AND '{end_date}'"
  sql2 = f"SELECT * FROM finance.{symbol}"
  sql3 = f"SELECT DATE,BS,DS,SD FROM divid.{symbol}"
  sql4 = f"SELECT * FROM fundflow.{symbol} WHERE __date__ BETWEEN '{start_date}' AND '{end_date}'"

  if symbol.startswith("SH6") or symbol.startswith("SZ00") or symbol.startswith("SZ30"):
    sqls[f"{symbol}.KLINE"] = sql1
    sqls[f"{symbol}.FINANCE"] = sql2
    sqls[f"{symbol}.DIVID"] = sql3
    sqls[f"{symbol}.FUNDFLOW"] = sql4
  else:
    sqls[f"{symbol}.KLINE"] = sql1


def load_data_msd_batch(
  symbols: List[str], start_date: str, end_date: str, n: int = 0, who: str = ""
) -> Dict[str, Dict[str, np.ndarray]]:
  sqls = {}
  for symbol in symbols:
    symbol_sqls(sqls, symbol, start_date, end_date)

  # fetch all data
  t1 = time.time()
  raw_datas = msd_fetch_once("msd://" + msd_host, sqls)
  t2 = time.time()
  logger.info(f"{who} fetch data cost {t2 - t1} seconds, symbols: {','.join(symbols)}")

  # group by symbol -> kind -> field
  grouped = {}
  for k, v in raw_datas.items():
    symbol, kind, field = k.split(".")
    if symbol not in grouped:
      grouped[symbol] = {}
    if kind not in grouped[symbol]:
      grouped[symbol][kind] = {}
    grouped[symbol][kind][field] = v

  datas = {}

  for k, g in grouped.items():
    symbol_data = {}

    kline = g.get("KLINE", None)
    if kline is None:
      continue

    date_base = kline.get("DATE", None)
    if date_base is None:
      continue

    # fill kline data
    for field, arr in kline.items():
      symbol_data[field] = arr  # NDArrayWithDate(arr, date_base)
    symbol_data["_DS_KLINE"] = (kline, "1d")

    # fill finance data
    finance = g.get("FINANCE", None)
    if finance is not None:
      dates2 = finance["DATE"]
      for field, arr in finance.items():
        if field == "DATE":
          continue
        arr = np.nan_to_num(arr)
        if field in ["TCAP", "AS", "BS", "GOS", "FIS", "FCS"]:
          arr = arr * 10000.0
        symbol_data[field] = arr  # NDArrayWithDate(arr, dates2)
      symbol_data["_DS_FINANCE"] = (finance, "1q")

    # fill divid data
    divid = g.get("DIVID", None)
    if divid is not None:
      dates3 = divid["DATE"]
      aligned = align_date_fill(date_base, dates3)
      c = np.intersect1d(date_base, dates3)
      ai = np.nonzero(np.isin(date_base, c))
      bi = np.nonzero(np.isin(dates3, c))
      if len(aligned) > 0:
        BS = np.nan_to_num(divid["BS"])
        DS = np.nan_to_num(divid["DS"])
        SD = np.nan_to_num(divid["SD"])

        GIVEN_SHARE = np.zeros_like(date_base, dtype=np.float64)
        GIVEN_CASH = np.zeros_like(date_base, dtype=np.float64)
        GIVEN_SHARE[ai] = (BS[bi] + DS[bi]) / 10.0
        GIVEN_CASH[ai] = SD[bi] / 10.0
        GIVEN_CASH = np.nan_to_num(GIVEN_CASH)
        GIVEN_SHARE = np.nan_to_num(GIVEN_SHARE)
        symbol_data["GCASH"] = GIVEN_CASH  # NDArrayWithDate(GIVEN_CASH, date_base)
        symbol_data["GSHARE"] = np.nan_to_num(GIVEN_SHARE)
        divid["GCASH"] = GIVEN_CASH
        divid["GSHARE"] = GIVEN_SHARE
      else:
        GIVEN_CASH = np.zeros_like(date_base, dtype=np.float64)
        GIVEN_SHARE = np.zeros_like(date_base, dtype=np.float64)
        symbol_data["GCASH"] = np.zeros_like(date_base, dtype=np.float64)
        symbol_data["GSHARE"] = np.zeros_like(date_base, dtype=np.float64)
        divid["GCASH"] = GIVEN_CASH
        divid["GSHARE"] = GIVEN_SHARE

      CLOSE = np.array(symbol_data["CLOSE"], copy=True)
      CLOSE2 = pre_adjustment(CLOSE, symbol_data["GCASH"], symbol_data["GSHARE"])

      divid["DATE"] = date_base

      ratio = CLOSE2 / CLOSE

      symbol_data["OPEN"] *= ratio
      symbol_data["HIGH"] *= ratio
      symbol_data["LOW"] *= ratio
      symbol_data["CLOSE"] *= ratio
      symbol_data["CLOSE2"] = CLOSE
      symbol_data["PRICE"] = CLOSE
      symbol_data["_DS_DIVID"] = (divid, "1d")
    else:
      symbol_data["GCASH"] = np.zeros_like(date_base, dtype=np.float64)
      symbol_data["GSHARE"] = np.zeros_like(date_base, dtype=np.float64)
      symbol_data["CLOSE2"] = symbol_data["CLOSE"]
      symbol_data["PRICE"] = symbol_data["CLOSE"]

    symbol_data["SECTOR"] = get_stock_sector().get(k, [])

    fund_flow = g.get("FUNDFLOW", None)
    if fund_flow is not None:
      for field, arr in fund_flow.items():
        if field == "DATE":
          continue
        symbol_data[field] = arr
      symbol_data["_DS_FUNDFLOW"] = (fund_flow, "1d")

    datas[k] = symbol_data

  return datas
