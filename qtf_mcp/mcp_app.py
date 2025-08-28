from io import StringIO

from mcp.server.fastmcp import Context, FastMCP

from . import research
from .symbols import get_available_sectors

# Create an MCP server
mcp_app = FastMCP(
  "CnStock",
  sse_path="/cnstock/sse",
  message_path="/cnstock/messages/",
  streamable_http_path="/cnstock/mcp",
)


@mcp_app.tool()
async def brief(symbol: str, ctx: Context) -> str:
  """Get brief information for a given stock symbol, including
  - basic data
  - trading data
  Args:
    symbol (str): Stock symbol, must be in the format of "SH000001" or "SZ000001", you should infer user inputs like stock name to stock symbol
  """
  who = ctx.request_context.request.client.host  # type: ignore
  raw_data = await research.load_raw_data(symbol, None, who)
  buf = StringIO()
  if len(raw_data) == 0:
    return "No data found for symbol: " + symbol
  research.build_basic_data(buf, symbol, raw_data)
  research.build_trading_data(buf, symbol, raw_data)
  """Get brief information for a given stock symbol"""
  return buf.getvalue()


@mcp_app.tool()
async def medium(symbol: str, ctx: Context) -> str:
  """Get medium information for a given stock symbol, including
  - basic data
  - trading data
  - financial data
  Args:
    symbol (str): Stock symbol, must be in the format of "SH000001" or "SZ000001", you infer convert user inputs like stock name to stock symbol
  """
  who = ctx.request_context.request.client.host  # type: ignore
  raw_data = await research.load_raw_data(symbol, None, who)
  buf = StringIO()
  if len(raw_data) == 0:
    return "No data found for symbol: " + symbol
  research.build_basic_data(buf, symbol, raw_data)
  research.build_trading_data(buf, symbol, raw_data)
  research.build_financial_data(buf, symbol, raw_data)
  return buf.getvalue()


@mcp_app.tool()
async def full(symbol: str, ctx: Context) -> str:
  """Get full information for a given stock symbol, including
  - basic data
  - trading data
  - financial data
  - technical analysis data
  Args:
    symbol (str): Stock symbol, must be in the format of "SH000001" or "SZ000001", you should infer user inputs like stock name to stock symbol
  """
  who = ctx.request_context.request.client.host  # type: ignore
  raw_data = await research.load_raw_data(symbol, None, who)
  buf = StringIO()
  if len(raw_data) == 0:
    return "No data found for symbol: " + symbol
  research.build_basic_data(buf, symbol, raw_data)
  research.build_trading_data(buf, symbol, raw_data)
  research.build_financial_data(buf, symbol, raw_data)
  research.build_technical_data(buf, symbol, raw_data)
  return buf.getvalue()


@mcp_app.tool()
async def sectors(ctx: Context) -> str:
  """Get all available sector names for A-share stocks
  
  Returns:
    A list of all available sector names that can be used with the sector_stocks function
  """
  available_sectors = get_available_sectors()
  
  buf = StringIO()
  print("# A股可用板块列表", file=buf)
  print("", file=buf)
  print(f"共有 {len(available_sectors)} 个板块:", file=buf)
  print("", file=buf)
  
  # 按字母顺序分组显示
  for i, sector in enumerate(available_sectors, 1):
    print(f"{i}. {sector}", file=buf)
    if i % 20 == 0:  # 每20个板块换行
      print("", file=buf)
  
  print("", file=buf)
  print("使用 sector_stocks 函数可以获取指定板块的股票数据", file=buf)
  
  return buf.getvalue()


@mcp_app.tool()
async def sector_stocks(sector_name: str, board_type: str = "all", limit: int = 50, ctx: Context = None) -> str:
  """Get basic data list for all stocks in a specific sector
  
  Args:
    sector_name (str): Sector name, use 'sectors' function to get available sector names
    board_type (str): Board type filter - "main" for main board (SH6*/SZ00*), "star" for STAR board (SH688*), "gem" for GEM board (SZ30*), "all" for all boards. Default is "all"
    limit (int): Maximum number of stocks to return, default is 50
    
  Returns:
    A formatted table with basic data for stocks in the specified sector, including:
    - Stock code and name
    - Latest price and change percentage  
    - Market capitalization and trading volume
    - Industry concepts
  """
  who = ctx.request_context.request.client.host if ctx else ""  # type: ignore
  
  return await research.load_sector_basic_data(sector_name, board_type, limit, who)
