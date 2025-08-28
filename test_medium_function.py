#!/usr/bin/env python3

import asyncio
import sys
import os
from io import StringIO

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from qtf_mcp import research

class MockContext:
    """模拟MCP Context"""
    def __init__(self):
        class MockClient:
            host = "test_client"
        
        class MockRequest:
            client = MockClient()
        
        class MockRequestContext:
            request = MockRequest()
        
        self.request_context = MockRequestContext()

async def test_medium_function():
    """测试medium函数是否能正常处理SZ300711"""
    symbol = "SZ300711"
    
    print(f"=== 测试medium函数: {symbol} ===\n")
    
    try:
        # 模拟medium函数的逻辑
        who = "test_client"
        raw_data = await research.load_raw_data(symbol, None, who)
        
        if len(raw_data) == 0:
            print("❌ 未获取到数据")
            return False
            
        print(f"✅ 成功获取数据，字段数量: {len(raw_data)}")
        print(f"数据字段: {list(raw_data.keys())}")
        print(f"TCAP字段存在: {'TCAP' in raw_data}")
        
        # 测试各个构建函数
        buf = StringIO()
        
        print("\n测试build_basic_data...")
        research.build_basic_data(buf, symbol, raw_data)
        print("✅ build_basic_data 成功")
        
        print("测试build_trading_data...")
        research.build_trading_data(buf, symbol, raw_data)
        print("✅ build_trading_data 成功")
        
        print("测试build_financial_data...")
        research.build_financial_data(buf, symbol, raw_data)
        print("✅ build_financial_data 成功")
        
        result = buf.getvalue()
        print(f"\n✅ 完整报告生成成功，长度: {len(result)} 字符")
        
        # 显示报告的前500个字符
        print("\n=== 报告预览 ===")
        print(result[:500] + "..." if len(result) > 500 else result)
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试medium函数修复效果...\n")
    
    success = asyncio.run(test_medium_function())
    
    if success:
        print("\n🎉 medium函数测试通过 - 修复成功")
    else:
        print("\n❌ medium函数测试失败")
        sys.exit(1)