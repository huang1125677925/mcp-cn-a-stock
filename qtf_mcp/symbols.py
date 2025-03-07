import json
import logging
from typing import Dict, Iterable, Tuple

SYMBOLS_SHSZ: Dict[str, Tuple[str, int, int]] = {}


def load_markets(fname: str):
  try:
    with open(fname) as fp:
      m = json.load(fp)
      for o in m["items"]:
        SYMBOLS_SHSZ[o["code"]] = (o["name"], 2, 2)
  except:
    logging.warning("load markets failed", exc_info=True)


def load_symbols():
  """
  load symbols from confs/markets.json
  """
  load_markets("confs/markets.json")


def symbol_with_name(symbols: Iterable[str]) -> Iterable[Tuple[str, str]]:
  """
  return symbol with name
  """
  for s in symbols:
    if s in SYMBOLS_SHSZ:
      yield (s, SYMBOLS_SHSZ[s][0])
    else:
      yield (s, "")


def get_symbol_name(symbol: str) -> str:
  """
  get symbol name
  """
  if symbol in SYMBOLS_SHSZ:
    return SYMBOLS_SHSZ[symbol][0]
  else:
    return ""
