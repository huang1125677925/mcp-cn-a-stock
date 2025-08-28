#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试板块股票数据获取功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qtf_mcp.symbols import get_available_sectors, get_symbols_by_sector, filter_main_board_symbols
from qtf_mcp.research import load_sector_basic_data


async def test_sector_functions():
    """测试板块相关函数"""
    print("=== 测试板块功能 ===")
    
    # 测试获取可用板块
    print("\n1. 测试获取可用板块列表...")
    sectors = get_available_sectors()
    print(f"共找到 {len(sectors)} 个板块")
    print(f"前10个板块: {sectors[:10]}")
    
    # 测试获取指定板块的股票
    if sectors:
        test_sector = "新能源汽车"  # 选择一个常见的板块
        if test_sector in sectors:
            print(f"\n2. 测试获取 '{test_sector}' 板块股票...")
            sector_symbols = get_symbols_by_sector(test_sector)
            print(f"'{test_sector}' 板块共有 {len(sector_symbols)} 只股票")
            print(f"前5只股票: {sector_symbols[:5]}")
            
            # 测试主板过滤
            main_board_symbols = filter_main_board_symbols(sector_symbols)
            print(f"其中主板股票: {len(main_board_symbols)} 只")
            
            # 测试获取板块基础数据（限制为5只股票以加快测试）
            print(f"\n3. 测试获取 '{test_sector}' 板块基础数据...")
            try:
                result = await load_sector_basic_data(test_sector, "main", 5, "test")
                print("数据获取成功！")
                print("结果预览:")
                lines = result.split('\n')
                for line in lines[:15]:  # 只显示前15行
                    print(line)
                if len(lines) > 15:
                    print("...")
            except Exception as e:
                print(f"数据获取失败: {e}")
        else:
            print(f"\n2. 板块 '{test_sector}' 不存在，使用第一个板块进行测试")
            test_sector = sectors[0]
            sector_symbols = get_symbols_by_sector(test_sector)
            print(f"'{test_sector}' 板块共有 {len(sector_symbols)} 只股票")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    asyncio.run(test_sector_functions())