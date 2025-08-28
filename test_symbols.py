#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from qtf_mcp.symbols import symbol_with_name, get_symbol_name, get_all_symbols

async def test_symbols():
    """测试符号管理模块"""
    
    print("=== 测试股票符号管理 ===")
    
    # 测试单个股票名称获取
    symbol = "SH600276"
    name = get_symbol_name(symbol)
    print(f"股票 {symbol} 的名称: {name}")
    
    # 测试多个股票
    symbols = ["SH600276", "SZ000001", "SH000001"]
    symbol_names = symbol_with_name(symbols)
    print(f"\n多个股票测试:")
    for sym, name in symbol_names:
        print(f"  {sym}: {name}")
    
    # 测试从markets.json加载的数据
    all_symbols = get_all_symbols()
    print(f"\n从markets.json加载的股票总数: {len(all_symbols)}")
    
    # 显示前10个作为示例
    print("\n前10个股票示例:")
    for i, sym in enumerate(all_symbols[:10]):
        name = get_symbol_name(sym)
        print(f"  {i+1}. {sym}: {name}")

if __name__ == "__main__":
    asyncio.run(test_symbols())