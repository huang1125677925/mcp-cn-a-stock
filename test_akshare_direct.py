#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试akshare API
"""

import akshare as ak
from datetime import datetime, timedelta

def test_akshare_direct():
    """直接测试akshare分钟级数据API"""
    print("直接测试akshare分钟级数据API...")
    
    # 测试参数 - 尝试最近的交易日
    symbols = ["000001", "600000"]  # 不带前缀的代码
    # 不指定具体日期，看看能否获取到最新数据
    period = "1"
    
    print(f"时间间隔: {period} 分钟")
    print("不指定日期范围，获取默认数据")
    
    for symbol in symbols:
        print(f"\n=== 测试代码: {symbol} ===")
        
        # 测试指数分钟级数据
        print("\n--- 测试 index_zh_a_hist_min_em ---")
        try:
            df = ak.index_zh_a_hist_min_em(
                symbol=symbol,
                period=period
            )
            print(f"返回类型: {type(df)}")
            if df is not None:
                print(f"数据形状: {df.shape}")
                if not df.empty:
                    print(f"列名: {list(df.columns)}")
                    print(f"前3行数据:")
                    print(df.head(3))
                else:
                    print("返回空数据框")
            else:
                print("返回None")
        except Exception as e:
            print(f"index_zh_a_hist_min_em 出错: {e}")
        
        # 测试股票分钟级数据
        print("\n--- 测试 stock_zh_a_hist_min_em ---")
        try:
            df = ak.stock_zh_a_hist_min_em(
                symbol=symbol,
                period=period
            )
            print(f"返回类型: {type(df)}")
            if df is not None:
                print(f"数据形状: {df.shape}")
                if not df.empty:
                    print(f"列名: {list(df.columns)}")
                    print(f"前3行数据:")
                    print(df.head(3))
                else:
                    print("返回空数据框")
            else:
                print("返回None")
        except Exception as e:
            print(f"stock_zh_a_hist_min_em 出错: {e}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_akshare_direct()