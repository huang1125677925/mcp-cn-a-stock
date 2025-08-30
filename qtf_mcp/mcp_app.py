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
  """Get stocks by sector classification for A-share market, including
  - sector classification and filtering
  - board type filtering (main, gem, star)
  - stock list with names and codes
  - sector overview information
  Args:
    sector_name (str): Sector name like "人工智能", "新能源", "医药" etc. Use 'sectors' function to get available sector names
    board_type (str): Board type - "main" for main board (SH6*/SZ00*), "gem" for创业板, "star" for 科创板, "all" for all boards. Default is "all"
    limit (int): Maximum number of stocks to return, default is 50
  """
  from .symbols import (
      get_symbols_by_sector, get_symbol_name, filter_main_board_symbols,
      filter_gem_board_symbols, filter_star_board_symbols, get_available_sectors
  )
  
  who = ctx.request_context.request.client.host if ctx else ""  # type: ignore
  
  try:
    # 获取所有板块
    available_sectors = get_available_sectors()
    
    # 板块名称映射表
    sector_mapping = {
        "人工智能": ["人工智能", "AIGC概念", "AI智能体", "AI语料", "多模态AI"],
        "新能源": ["新能源汽车", "光伏概念", "固态电池", "燃料电池", "动力电池回收"],
        "医药": ["生物医药", "医疗器械概念", "医药电商", "合成生物", "生物疫苗"],
        "半导体": ["芯片概念", "集成电路概念", "第三代半导体", "存储芯片", "汽车芯片"],
        "电池": ["固态电池", "锂电池", "钠离子电池", "电池", "储能"],
        "光伏": ["光伏概念", "HJT电池", "TOPCON电池", "BC电池"],
        "汽车": ["新能源汽车", "汽车零部件", "无人驾驶", "汽车芯片"],
        "医疗": ["医疗器械概念", "互联网医疗", "牙科医疗", "毛发医疗"],
        "5G": ["5G", "6G概念", "通信设备"],
        "云计算": ["云计算", "边缘计算", "数据中心"],
        "区块链": ["区块链", "NFT概念", "数字货币"],
    }
    
    # 确定要搜索的板块
    search_sectors = []
    sector_name_lower = sector_name.lower()
    
    # 先检查是否有精确匹配
    for sector in available_sectors:
      if sector_name in sector:
        search_sectors.append(sector)
    
    # 如果没有精确匹配，使用映射表
    if not search_sectors:
      for key, mapped_sectors in sector_mapping.items():
        if key.lower() in sector_name_lower or sector_name_lower in key.lower():
          search_sectors.extend(mapped_sectors)
          break
    
    # 如果仍然没有匹配，尝试模糊搜索
    if not search_sectors:
      keywords = ["概念", "板块"]
      for sector in available_sectors:
        if any(keyword in sector for keyword in keywords) and sector_name in sector:
          search_sectors.append(sector)
    
    # 如果还是找不到，返回建议
    if not search_sectors:
      suggestions = []
      for key in sector_mapping.keys():
        if any(keyword in sector_name_lower for keyword in key.lower().split()):
          suggestions.append(key)
      
      if not suggestions:
        suggestions = list(sector_mapping.keys())[:10]
      
      return f"未找到'{sector_name}'相关的板块。建议尝试以下板块：{', '.join(suggestions)}"
    
    # 获取所有匹配板块的股票
    all_stocks = set()
    for sector in search_sectors:
      if sector in available_sectors:
        stocks = get_symbols_by_sector(sector)
        all_stocks.update(stocks)
    
    # 转换为列表并排序
    all_stocks = sorted(list(all_stocks))
    
    # 按板块类型过滤
    if board_type == "main":
      filtered_stocks = filter_main_board_symbols(all_stocks)
    elif board_type == "gem":
      filtered_stocks = filter_gem_board_symbols(all_stocks)
    elif board_type == "star":
      filtered_stocks = filter_star_board_symbols(all_stocks)
    else:  # all
      filtered_stocks = all_stocks
    
    if not filtered_stocks:
      return f"在{board_type}板块中未找到'{sector_name}'相关的股票"
    
    # 限制返回数量
    limited_stocks = filtered_stocks[:limit]
    
    # 获取股票名称
    stock_info = []
    for symbol in limited_stocks:
      name = get_symbol_name(symbol)
      stock_info.append(f"- {symbol}: {name}")
    
    # 确定实际使用的板块
    actual_sectors = [s for s in search_sectors if s in available_sectors]
    matched_sectors_str = "、".join(actual_sectors) if actual_sectors else sector_name
    
    # 构建报告
    report = f"""# {sector_name}板块股票列表 ({board_type}板)

## 板块信息
- **搜索板块**: {matched_sectors_str}
- **板块类型**: {board_type}
- **总股票数**: {len(filtered_stocks)}
- **返回数量**: {len(limited_stocks)}

## 股票列表
{chr(10).join(stock_info)}

## 使用说明
- **主板股票**: 以SH6开头或SZ00开头
- **创业板**: 以SZ30开头
- **科创板**: 以SH688开头

## 常用板块关键词
人工智能、新能源、医药、半导体、电池、光伏、汽车、医疗、5G、云计算、区块链

如需查看更多股票，请调整limit参数
"""
    
    return report
    
  except Exception as e:
    return f"获取{sector_name}板块股票时发生错误: {str(e)}"


@mcp_app.tool()
async def latest_trading(symbol: str, ctx: Context) -> str:
  """Get the latest trading data for A-share main board stocks, including
  - real-time price
  - daily change and percentage
  - trading volume and amount
  - market status
  Args:
    symbol (str): Stock symbol, must be in the format of "SH000001" or "SZ000001" for main board stocks
  """
  from datetime import datetime, timedelta
  from .datafeed import fetch_kline_data
  from .symbols import get_symbol_name
  
  who = ctx.request_context.request.client.host  # type: ignore
  
  try:
    # 获取股票名称
    stock_name = get_symbol_name(symbol)
    
    # 获取最近2个交易日的数据用于计算涨跌幅
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
    
    # 获取K线数据
    kline_data = fetch_kline_data(symbol, start_date, end_date)
    
    if kline_data is None or kline_data.empty:
      return f"无法获取股票 {symbol} ({stock_name}) 的最新交易数据"
    
    # 获取最新交易数据
    latest = kline_data.iloc[-1]
    prev_close = kline_data.iloc[-2]['close'] if len(kline_data) > 1 else latest['close']
    
    # 计算涨跌幅
    change = latest['close'] - prev_close
    change_pct = (change / prev_close) * 100 if prev_close > 0 else 0
    
    # 处理成交额可能不存在的情况
    amount = latest.get('amount', latest['volume'] * latest['close'])
    
    # 判断是否为指数
    is_index = symbol.startswith("SH000") or symbol.startswith("SZ399")
    unit = "点" if is_index else "元"
    
    # 构建交易数据报告
    report = f"""# {stock_name}({symbol}) 最新交易数据

## 基本信息
- **股票名称**: {stock_name}
- **股票代码**: {symbol}
- **数据时间**: {latest['date'].strftime('%Y-%m-%d') if hasattr(latest['date'], 'strftime') else str(latest['date'])[:10]}

## 最新交易数据
- **最新价格**: {latest['close']:.2f}{unit}
- **开盘价**: {latest['open']:.2f}{unit}
- **最高价**: {latest['high']:.2f}{unit}
- **最低价**: {latest['low']:.2f}{unit}
- **昨收价**: {prev_close:.2f}{unit}
- **涨跌额**: {change:+.2f}{unit}
- **涨跌幅**: {change_pct:+.2f}%

## 成交数据
- **成交量**: {latest['volume']:,.0f}{"手" if is_index else "股"}
- **成交额**: ¥{amount:,.2f}元

## 市场状态
- **交易状态**: {"正常交易" if latest['volume'] > 0 else "停牌"}
- **振幅**: {((latest['high'] - latest['low']) / prev_close * 100):.2f}%
"""
    
    return report
    
  except Exception as e:
    return f"获取 {symbol} 最新交易数据时发生错误: {str(e)}"
