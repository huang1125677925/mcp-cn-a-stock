#!/usr/bin/env python3
"""
测试板块股票获取功能
"""

import asyncio
from qtf_mcp.mcp_app import sector_stocks
from mcp.server.fastmcp import Context
from unittest.mock import Mock

class MockRequest:
    def __init__(self):
        self.client = Mock()
        self.client.host = "127.0.0.1"

class MockContext:
    def __init__(self):
        self.request_context = Mock()
        self.request_context.request = MockRequest()

async def test_sector_stocks():
    """测试获取板块股票功能"""
    
    # 测试用例
    test_cases = [
        {"sector_name": "人工智能", "board_type": "main", "limit": 10},
        {"sector_name": "新能源", "board_type": "all", "limit": 15},
        {"sector_name": "医药", "board_type": "main", "limit": 8},
        {"sector_name": "半导体", "board_type": "gem", "limit": 5},
    ]
    
    ctx = MockContext()
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"测试板块: {test_case['sector_name']} ({test_case['board_type']}板)")
        print(f"限制数量: {test_case['limit']}")
        print(f"{'='*60}")
        
        try:
            result = await sector_stocks(
                test_case["sector_name"], 
                test_case["board_type"], 
                test_case["limit"], 
                ctx
            )
            print(result)
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    asyncio.run(test_sector_stocks())