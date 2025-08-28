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

# 初始化缓存
if not SYMBOLS_CACHE:
    SYMBOLS_CACHE.update(load_markets_data())