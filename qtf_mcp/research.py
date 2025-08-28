import datetime
from io import StringIO
from typing import Dict, TextIO

import numpy as np
import talib
from numpy import ndarray

from .datafeed import load_data_msd
from .symbols import symbol_with_name


async def load_raw_data(
  symbol: str, end_date=None, who: str = ""
) -> Dict[str, ndarray]:
  if end_date is None:
    end_date = datetime.datetime.now() + datetime.timedelta(days=1)
  if type(end_date) == str:
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

  start_date = end_date - datetime.timedelta(days=365 * 2)

  return await load_data_msd(
    symbol, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), 0, who
  )


def is_stock(symbol: str) -> bool:
  if symbol.startswith("SH6") or symbol.startswith("SZ00") or symbol.startswith("SZ30"):
    return True
  return False


def build_stock_data(symbol: str, raw_data: Dict[str, ndarray]) -> str:
  md = StringIO()
  build_basic_data(md, symbol, raw_data)
  build_trading_data(md, symbol, raw_data)
  build_technical_data(md, symbol, raw_data)
  build_financial_data(md, symbol, raw_data)

  return md.getvalue()


def filter_sector(sectors: list[str]) -> list[str]:
  keywords = ["MSCI", "标普", "同花顺", "融资融券", "沪股通"]
  # return sectors not including keywords
  return [s for s in sectors if not any(k in s for k in keywords)]


def est_fin_ratio(last_fin_date: datetime.datetime) -> float:
  if last_fin_date.month == 12:
    return 1
  elif last_fin_date.month == 9:
    return 0.75
  elif last_fin_date.month == 6:
    return 0.5
  elif last_fin_date.month == 3:
    return 0.25
  else:
    return 0


def yearly_fin_index(dates: ndarray) -> int:
  """
  Returns the index of the last December in the dates array.
  If no December is found, returns -1.
  """
  for i in range(len(dates) - 1, -1, -1):
    date = datetime.datetime.fromtimestamp(dates[i] / 1e9)
    if date.month == 12:
      return i
  return -1


def build_basic_data(fp: TextIO, symbol: str, data: Dict[str, ndarray]) -> None:
  print("# 基本数据", file=fp)
  print("", file=fp)
  symbol, name = list(symbol_with_name([symbol]))[0]
  sector = " ".join(filter_sector(data["SECTOR"]))  # type: ignore
  data_date = datetime.datetime.fromtimestamp(data["DATE"][-1])
  
  print(f"- 股票代码: {symbol}", file=fp)
  print(f"- 股票名称: {name}", file=fp)
  print(f"- 数据日期: {data_date.strftime('%Y-%m-%d')}", file=fp)
  print(f"- 行业概念: {sector}", file=fp)
  
  if is_stock(symbol):
    # 使用AkShare提供的财务数据
    total_market_cap = data.get("TCAP", [0])[-1]
    if total_market_cap > 0:
      # TCAP已经是总市值（单位：万元），转换为亿元
      print(f"- 总市值: {total_market_cap/10000:.2f}亿元", file=fp)
    
    # 检查是否有财务数据
    navps = data.get("NAVPS", [1.0])[-1]
    if navps != 1.0:
      print(f"- 市净率: {data['CLOSE2'][-1] / navps:.2f}", file=fp)
    
    roe = data.get("ROE", [0.0])[-1]
    if roe != 0.0:
      print(f"- 净资产收益率: {roe:.2f}%", file=fp)
  print("", file=fp)


def today_volume_est_ratio(data: Dict[str, ndarray], now: int = 0) -> float:
  data_dt = datetime.datetime.fromtimestamp(data["DATE"][-1])
  now_dt = (
    datetime.datetime.now() if now == 0 else datetime.datetime.fromtimestamp(now)
  )

  data_date = data_dt.strftime("%Y-%m-%d")
  now_date = now_dt.strftime("%Y-%m-%d")
  if data_date != now_date:
    return 1
  now_time = now_dt.strftime("%H:%M:%S")
  if now_time >= "09:30:00" and now_time < "11:30:00":
    start_dt = now_dt.replace(hour=9, minute=30, second=0)
    minutes = (now_dt - start_dt).seconds / 60
    return 240 / (minutes + 1)
  elif now_time >= "11:30:00" and now_time < "13:00:00":
    return 2
  elif now_time >= "13:00:00" and now_time < "15:00:00":
    start_dt = now_dt.replace(hour=13, minute=0, second=0)
    minutes = (now_dt - start_dt).seconds / 60
    return 240 / (120 + minutes + 1)
  else:
    return 1


FUND_FLOW_FIELDS = [
  ("主力", "A"),
  ("超大单", "XL"),
  ("大单", "L"),
  ("中单", "M"),
  ("小单", "S"),
]


def build_fund_flow(field: tuple[str, str], data: Dict[str, ndarray]) -> str:
  field_amount = field[1] + "_A"
  field_ratio = field[1] + "_R"
  value_amount = data.get(field_amount, None)
  value_ratio = data.get(field_ratio, None)
  if value_amount is None or value_ratio is None:
    return ""

  kind = field[0]
  amount = value_amount[-1] / 1e8  # Convert to billions
  ratio = abs(value_ratio[-1])
  in_out = "流入" if amount > 0 else "流出"
  amount = abs(amount)  # Use absolute value for display
  return f"- {kind} {in_out}: {amount:.2f}亿, 占比: {ratio:.2%}"


def build_trading_data(fp: TextIO, symbol: str, data: Dict[str, ndarray]) -> None:
  today_vol_est_ratio = today_volume_est_ratio(data)
  close = data["CLOSE"]
  volume = data["VOLUME"]
  volume[-1] = volume[-1] * today_vol_est_ratio  # Adjust today's volume
  amount = data["AMOUNT"] / 1e8
  amount[-1] = amount[-1] * today_vol_est_ratio  # Adjust today's amount
  high = data["HIGH"]
  low = data["LOW"]

  periods = list(filter(lambda n: n <= len(close), [5, 20, 60, 120, 240]))

  print("# 交易数据", file=fp)
  print("", file=fp)

  print("## 价格", file=fp)
  print(f"- 当日: {close[-1]:.3f} 最高: {high[-1]:.3f} 最低: {low[-1]:.3f}", file=fp)
  for p in periods:
    print(
      f"- {p}日均价: {close[-p:].mean():.3f} 最高: {high[-p:].max():.3f} 最低: {low[-p:].min():.3f}",
      file=fp,
    )
  print("", file=fp)

  print("## 振幅", file=fp)
  print(f"- 当日: {(high[-1] / low[-1] - 1):.2%}", file=fp)
  for p in periods:
    print(f"- {p}日振幅: {(high[-p:].max() / low[-p:].min() - 1):.2%}", file=fp)
  print("", file=fp)

  print("## 涨跌幅", file=fp)
  print(f"- 当日: {(close[-1] / close[-2] - 1):.2%}", file=fp)
  for p in periods:
    print(f"- {p}日累计: {(close[-1] / close[-p] - 1) * 100:.2f}%", file=fp)
  print("", file=fp)

  print("## 成交量(万手)", file=fp)
  print(f"- 当日: {volume[-1] / 1e6:.2f}", file=fp)
  for p in periods:
    print(f"- {p}日均量(万手): {volume[-p:].mean() / 1e6:.2f}", file=fp)
  print("", file=fp)

  print("## 成交额(亿)", file=fp)
  print(f"- 当日: {amount[-1]:.2f}", file=fp)
  for p in periods:
    print(f"- {p}日均额(亿): {amount[-p:].mean():.2f}", file=fp)
  print("", file=fp)

  print("## 资金流向", file=fp)
  for field in FUND_FLOW_FIELDS:
    value = build_fund_flow(field, data)
    if value:
      print(value, file=fp)
  print("", file=fp)

  if is_stock(symbol):
    tcap = data["TCAP"]
    print("## 换手率", file=fp)
    print(f"- 当日: {volume[-1] / tcap[-1]:.2%}", file=fp)
    for p in periods:
      print(f"- {p}日均换手: {volume[-p:].mean() / tcap[-1]:.2%}", file=fp)
      print(f"- {p}日总换手: {volume[-p:].sum() / tcap[-1]:.2%}", file=fp)
    print("", file=fp)


def calculate_kdj(close: ndarray, high: ndarray, low: ndarray, n: int = 9, k: int = 3, d: int = 3) -> tuple[ndarray, ndarray, ndarray]:
    """计算KDJ指标"""
    rsv = np.zeros_like(close)
    k_values = np.zeros_like(close)
    d_values = np.zeros_like(close)
    j_values = np.zeros_like(close)
    
    for i in range(n-1, len(close)):
        highest_high = np.max(high[i-n+1:i+1])
        lowest_low = np.min(low[i-n+1:i+1])
        
        if highest_high == lowest_low:
            rsv[i] = 50
        else:
            rsv[i] = 100 * (close[i] - lowest_low) / (highest_high - lowest_low)
    
    # 计算K值
    k_values[n-1] = 50
    for i in range(n, len(close)):
        k_values[i] = (k-1)/k * k_values[i-1] + 1/k * rsv[i]
    
    # 计算D值
    d_values[n-1] = 50
    for i in range(n, len(close)):
        d_values[i] = (d-1)/d * d_values[i-1] + 1/d * k_values[i]
    
    # 计算J值
    j_values = 3 * k_values - 2 * d_values
    
    return k_values, d_values, j_values


def calculate_macd(close: ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[ndarray, ndarray, ndarray]:
    """计算MACD指标"""
    ema_fast = talib.EMA(close, timeperiod=fast)
    ema_slow = talib.EMA(close, timeperiod=slow)
    macd_line = ema_fast - ema_slow
    signal_line = talib.EMA(macd_line, timeperiod=signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def build_technical_data(fp: TextIO, symbol: str, data: Dict[str, ndarray]) -> None:
  close = data["CLOSE"]
  high = data["HIGH"]
  low = data["LOW"]

  if len(close) < 30:
    return

  print("# 技术指标(最近30日)", file=fp)
  print("", file=fp)

  kdj_k, kdj_d, kdj_j = calculate_kdj(close, high, low, 9, 3)

  macd_diff, macd_dea, _ = calculate_macd(close, 12, 26, 9)

  rsi_6 = talib.RSI(close, timeperiod=6)
  rsi_12 = talib.RSI(close, timeperiod=12)
  rsi_24 = talib.RSI(close, timeperiod=24)

  bb_upper, bb_middle, bb_lower = talib.BBANDS(close, matype=talib.MA_Type.T3)  # type: ignore

  date = [
    datetime.datetime.fromtimestamp(d / 1e9).strftime("%Y-%m-%d") for d in data["DATE"]
  ]
  columns = [
    ("日期", date),
    ("KDJ.K", kdj_k),
    ("KDJ.D", kdj_d),
    ("KDJ.J", kdj_j),
    ("MACD DIF", macd_diff),
    ("MACD DEA", macd_dea),
    ("RSI(6)", rsi_6),
    ("RSI(12)", rsi_12),
    ("RSI(24)", rsi_24),
    ("BBands Upper", bb_upper),
    ("BBands Middle", bb_middle),
    ("BBands Lower", bb_lower),
  ]
  print("| " + " | ".join([c[0] for c in columns]) + " |", file=fp)
  print("| --- " * len(columns) + "|", file=fp)
  for i in range(-1, max(-len(date), -31), -1):
    print(
      "| " + date[i] + "|" + " | ".join([f"{c[1][i]:.2f}" for c in columns[1:]]) + " |",
      file=fp,
    )
  print("", file=fp)


def build_financial_data(fp: TextIO, symbol: str, data: Dict[str, ndarray]) -> None:
  if not is_stock(symbol):
    return
  
  print("# 财务数据", file=fp)
  print("", file=fp)
  
  # 检查是否有财务数据
  if "_DS_FINANCE" not in data:
    print("- 暂无财务数据", file=fp)
    print("", file=fp)
    return
    
  try:
    fin, _ = data["_DS_FINANCE"]
    dates = fin["DATE"]
    max_years = 5
    years = 0
    fields = [
      # name, id, div, show
      ("主营收入(亿元)", "MR", 10000, True),
      ("净利润(亿元)", "NP", 10000, True),
      ("每股收益", "EPS", 1, True),
      ("每股净资产", "NAVPS", 1, True),
      ("净资产收益率", "ROE", 1, True),
    ]

    rows = []
    for i in range(len(dates) - 1, 0, -1):
      date = datetime.datetime.fromtimestamp(dates[i] / 1e9)
      if date.month != 12 or years >= max_years:
        continue
      row = [date.strftime("%Y年度")]
      for _, field, div, show in fields:
        if show and field in fin:
          row.append(fin[field][i] / div)
        else:
          row.append(0.0)
      rows.append(row)
      years += 1

    if rows:
      print("| 指标 | " + " ".join([f"{r[0]} |" for r in rows]), file=fp)
      print("| --- " * (len(rows) + 1) + "|", file=fp)
      for i in range(1, len(rows[0])):
        print(
          f"| {fields[i - 1][0]} | " + " ".join([f"{r[i]:.2f} |" for r in rows]),
          file=fp,
        )
    else:
      print("- 暂无年度财务数据", file=fp)
  except Exception as e:
    print(f"- 财务数据获取失败: {str(e)}", file=fp)
  
  print("", file=fp)
