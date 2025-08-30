#!/usr/bin/env python3
"""
Test the original issue: sector_stocks with 人工智能, main, 50
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

async def test_original_issue():
    """Test the exact parameters from the original issue"""
    
    print("=== 测试原始问题参数 ===")
    print("参数: sector_name='人工智能', board_type='main', limit=50")
    print("-" * 50)
    
    try:
        # Create mock context
        ctx = MockContext()
        
        # Call the sector_stocks function with original parameters
        result = await sector_stocks("人工智能", "main", 50, ctx)
        
        # Print the result
        print(result)
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_original_issue())