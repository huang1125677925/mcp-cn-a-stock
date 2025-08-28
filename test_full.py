#!/usr/bin/env python3
"""
测试full工具功能
"""
import asyncio
import sys
import os
from io import StringIO

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qtf_mcp import research

async def test_full():
    """测试full工具"""
    try:
        symbol = "SH600276"
        print(f"正在测试股票 {symbol} 的full报告...")
        
        # 直接调用research模块的函数，使用更近的日期
        raw_data = await research.load_raw_data(symbol, "2024-08-01", "2024-08-28")
        
        if len(raw_data) == 0:
            print("✗ 没有找到数据")
            return False
            
        buf = StringIO()
        research.build_basic_data(buf, symbol, raw_data)
        research.build_trading_data(buf, symbol, raw_data)
        research.build_financial_data(buf, symbol, raw_data)
        research.build_technical_data(buf, symbol, raw_data)
        
        content = buf.getvalue()
        print("✓ full工具执行成功")
        print("报告内容预览:")
        print("=" * 50)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("=" * 50)
        return True
            
    except Exception as e:
        print(f"✗ full工具执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_full())