#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

import asyncio
import akshare as ak

async def debug_real_market_cap():
    """调试真实的总市值数据"""
    symbol = "SH600276"
    stock_code = "600276"
    
    print(f"=== 调试股票: {symbol} ===")
    
    # 获取股票基本信息
    try:
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        print("\n股票基本信息:")
        print(stock_info)
        
        # 获取总市值
        total_market_value = stock_info[stock_info['item'] == '总市值']['value'].values[0]
        print(f"\n总市值原始值: {total_market_value}")
        print(f"总市值类型: {type(total_market_value)}")
        
        # 获取流通市值
        float_market_value = stock_info[stock_info['item'] == '流通市值']['value'].values[0]
        print(f"流通市值原始值: {float_market_value}")
        
        # 获取总股本
        total_shares = stock_info[stock_info['item'] == '总股本']['value'].values[0]
        print(f"总股本原始值: {total_shares}")
        
        # 获取当前价格
        current_price = stock_info[stock_info['item'] == '最新价']['value'].values[0]
        print(f"当前价格原始值: {current_price}")
        
    except Exception as e:
        print(f"获取数据失败: {e}")

if __name__ == "__main__":
    asyncio.run(debug_real_market_cap())