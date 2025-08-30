#!/usr/bin/env python3
"""
Test script for improved sector_stocks tool
"""

import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock

# Add the project root to path
sys.path.insert(0, '/Users/huangchuang/mcp-cn-a-stock')

# Import the mcp_app
from qtf_mcp.mcp_app import sector_stocks

class MockContext:
    def __init__(self):
        self.request_context = MagicMock()
        self.request_context.request.client.host = "test_client"

async def test_sector_stocks():
    """Test the improved sector_stocks function"""
    
    test_cases = [
        ("人工智能", "main", 10),
        ("新能源", "all", 15),
        ("医药", "main", 8),
        ("半导体", "gem", 5),
        ("电池", "main", 12),
    ]
    
    print("=== 测试改进后的sector_stocks工具 ===\n")
    
    for sector_name, board_type, limit in test_cases:
        print(f"测试板块: {sector_name}, 类型: {board_type}, 限制: {limit}")
        print("-" * 50)
        
        try:
            # Create mock context
            ctx = MockContext()
            
            # Call the sector_stocks function
            result = await sector_stocks(sector_name, board_type, limit, ctx)
            
            # Print the result
            print(result)
            print("\n")
            
        except Exception as e:
            print(f"错误: {str(e)}")
            print("\n")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_sector_stocks())