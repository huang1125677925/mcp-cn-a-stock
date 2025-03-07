from io import StringIO

from mcp.server.fastmcp import FastMCP

from . import research

# Create an MCP server
mcp_app = FastMCP("CnStock", sse_path="/cnstock/sse", message_path="/cnstock/messages/")


@mcp_app.tool()
async def brief(symbol: str) -> str:
  """Get brief information for a given stock symbol, including
  - basic data
  - trading data
  Args:
    symbol (str): Stock symbol, must be in the format of "SH000001" or "SZ000001", you should infer user inputs like stock name to stock symbol
  """
  raw_data = await research.load_raw_data(symbol)
  buf = StringIO()
  research.build_basic_data(buf, symbol, raw_data)
  research.build_trading_data(buf, symbol, raw_data)
  """Get brief information for a given stock symbol"""
  return buf.getvalue()


@mcp_app.tool()
async def medium(symbol: str) -> str:
  """Get medium information for a given stock symbol, including
  - basic data
  - trading data
  - financial data
  Args:
    symbol (str): Stock symbol, must be in the format of "SH000001" or "SZ000001", you infer convert user inputs like stock name to stock symbol
  """
  raw_data = await research.load_raw_data(symbol)
  buf = StringIO()
  research.build_basic_data(buf, symbol, raw_data)
  research.build_trading_data(buf, symbol, raw_data)
  research.build_financial_data(buf, symbol, raw_data)
  return buf.getvalue()


@mcp_app.tool()
async def full(symbol: str) -> str:
  """Get full information for a given stock symbol, including
  - basic data
  - trading data
  - financial data
  - technical analysis data
  Args:
    symbol (str): Stock symbol, must be in the format of "SH000001" or "SZ000001", you should infer user inputs like stock name to stock symbol
  """
  raw_data = await research.load_raw_data(symbol)
  buf = StringIO()
  research.build_basic_data(buf, symbol, raw_data)
  research.build_trading_data(buf, symbol, raw_data)
  research.build_financial_data(buf, symbol, raw_data)
  research.build_technical_data(buf, symbol, raw_data)
  return buf.getvalue()
