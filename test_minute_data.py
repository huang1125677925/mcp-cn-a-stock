#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分钟级数据获取功能
"""

import sys
import os
from datetime import datetime, timedelta
import akshare as ak

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'qtf_mcp'))

from qtf_mcp.datafeed import fetch_minute_data

def test_minute_data():
    """测试分钟级数据获取"""
    print("开始测试分钟级数据获取功能...")
    
    # 测试参数 - 使用一个确定的交易日期
    symbols = ["SZ000001", "SH600000"]  # 测试股票和指数
    start_datetime = "2025-08-12 09:30:00"  # 交易日的开盘时间
    end_datetime = "2025-08-12 15:00:00"    # 交易日的收盘时间
    
    print(f"时间范围: {start_datetime} 到 {end_datetime}")
    
    # 测试不同的股票代码和时间间隔
    periods = ["5"]
    
    for symbol in symbols:
        print(f"\n=== 测试股票: {symbol} ===")
        
        for period in periods:
            print(f"\n--- 测试 {period} 分钟级数据 ---")
            try:
                data = fetch_minute_data(symbol, start_datetime, end_datetime, period)
                
                if data is not None and not data.empty:
                    print(f"✓ 成功获取 {len(data)} 条 {period} 分钟级数据")
                    print(f"数据列: {list(data.columns)}")
                    print(f"时间范围: {data['datetime'].min()} 到 {data['datetime'].max()}")
                    print(f"价格范围: {data['close'].min():.2f} - {data['close'].max():.2f}")
                    
                    # 显示前3条数据
                    print("前3条数据:")
                    for i in range(min(3, len(data))):
                        row = data.iloc[i]
                        print(f"  {row['datetime']}: 开{row['open']:.2f} 高{row['high']:.2f} 低{row['low']:.2f} 收{row['close']:.2f} 量{row['volume']:.0f}")
                    break  # 如果成功获取数据，跳出period循环
                else:
                    print(f"✗ 未获取到 {period} 分钟级数据")
                    
            except Exception as e:
                print(f"✗ 获取 {period} 分钟级数据时出错: {e}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    # test_minute_data()
    stock_zh_a_hist_min_em_df = ak.stock_zh_a_hist_min_em(
        symbol="600276",
        start_date="2025-08-13 09:30:00",
        end_date="2025-08-13 15:00:00",
        period="5",
    )
    print(stock_zh_a_hist_min_em_df)