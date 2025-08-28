"""
股票符号管理模块
从confs/markets.json加载股票代码到名称的映射
"""

import json
import os
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger("qtf_mcp")

# 股票符号映射缓存
SYMBOLS_CACHE: Dict[str, str] = {}
MARKETS_FILE = "confs/markets.json"

def load_markets_data() -> Dict[str, str]:
    """从markets.json加载股票代码到名称的映射"""
    symbols = {}
    
    try:
        if os.path.exists(MARKETS_FILE):
            with open(MARKETS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if 'items' in data:
                for item in data['items']:
                    code = item.get('code', '')
                    name = item.get('name', '')
                    if code and name:
                        symbols[code] = name
                        
            logger.info(f"从 {MARKETS_FILE} 加载了 {len(symbols)} 个股票符号")
        else:
            logger.warning(f"找不到文件: {MARKETS_FILE}")
            
    except Exception as e:
        logger.error(f"加载 {MARKETS_FILE} 失败: {e}")
    
    return symbols

def get_symbol_name(symbol: str) -> str:
    """获取股票代码对应的名称"""
    if not SYMBOLS_CACHE:
        SYMBOLS_CACHE.update(load_markets_data())
    
    # 先从缓存中查找
    if symbol in SYMBOLS_CACHE:
        return SYMBOLS_CACHE[symbol]
    
    # 如果缓存中没有，尝试从AkShare获取
    try:
        import akshare as ak
        stock_code = symbol[2:]  # 去掉SH/SZ前缀
        
        # 获取股票基本信息
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        if not stock_info.empty:
            name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]
            SYMBOLS_CACHE[symbol] = name
            return name
            
    except Exception as e:
        logger.error(f"从AkShare获取股票名称失败: {e}")
    
    # 如果都失败，返回代码本身
    return symbol

def symbol_with_name(symbols: List[str]) -> List[Tuple[str, str]]:
    """将股票代码列表转换为(代码, 名称)元组列表"""
    result = []
    for symbol in symbols:
        name = get_symbol_name(symbol)
        result.append((symbol, name))
    return result

def get_all_symbols() -> List[str]:
    """获取所有可用的股票代码"""
    if not SYMBOLS_CACHE:
        SYMBOLS_CACHE.update(load_markets_data())
    return list(SYMBOLS_CACHE.keys())

def get_symbols_by_sector(sector_name: str) -> List[str]:
    """根据板块名称获取该板块的所有股票代码"""
    from .datafeed import get_stock_sector
    
    sector_data = get_stock_sector()
    matching_symbols = []
    
    for symbol, sectors in sector_data.items():
        if sector_name in sectors:
            matching_symbols.append(symbol)
    
    return matching_symbols

def get_available_sectors() -> List[str]:
    """获取所有可用的板块名称"""
    from .datafeed import get_stock_sector
    
    sector_data = get_stock_sector()
    all_sectors = set()
    
    for sectors in sector_data.values():
        all_sectors.update(sectors)
    
    # 过滤掉一些不需要的板块
    filtered_sectors = []
    keywords_to_exclude = ["MSCI", "标普", "同花顺", "融资融券", "沪股通", "深股通"]
    
    for sector in sorted(all_sectors):
        if not any(keyword in sector for keyword in keywords_to_exclude):
            filtered_sectors.append(sector)
    
    return filtered_sectors

def filter_main_board_symbols(symbols: List[str]) -> List[str]:
    """过滤出主板股票（SH6开头和SZ00开头）"""
    return [s for s in symbols if s.startswith('SH6') or s.startswith('SZ00')]

def filter_star_board_symbols(symbols: List[str]) -> List[str]:
    """过滤出科创板股票（SH688开头）"""
    return [s for s in symbols if s.startswith('SH688')]

def filter_gem_board_symbols(symbols: List[str]) -> List[str]:
    """过滤出创业板股票（SZ30开头）"""
    return [s for s in symbols if s.startswith('SZ30')]

def load_symbols() -> None:
    """加载股票符号数据到缓存"""
    global SYMBOLS_CACHE
    if not SYMBOLS_CACHE:
        SYMBOLS_CACHE.update(load_markets_data())
        logger.info(f"已加载 {len(SYMBOLS_CACHE)} 个股票符号到缓存")

# 初始化缓存
if not SYMBOLS_CACHE:
    SYMBOLS_CACHE.update(load_markets_data())