#!/usr/bin/env python3

import sys
import os
from io import StringIO
import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from qtf_mcp import research

def test_tcap_fix():
    """测试TCAP字段缺失时的处理"""
    symbol = "SZ300711"
    
    print(f"=== 测试股票: {symbol} ===\n")
    
    # 模拟没有TCAP字段的数据
    mock_data = {
        'DATE': np.array([1640995200, 1641081600, 1641168000]),  # 3天的时间戳
        'OPEN': np.array([10.0, 10.5, 11.0]),
        'HIGH': np.array([10.5, 11.0, 11.5]),
        'LOW': np.array([9.5, 10.0, 10.5]),
        'CLOSE': np.array([10.2, 10.8, 11.2]),
        'VOLUME': np.array([1000000, 1200000, 1100000]),
        'AMOUNT': np.array([10200000, 12960000, 12320000]),
        'CLOSE2': np.array([10.2, 10.8, 11.2]),
        'PRICE': np.array([10.2, 10.8, 11.2]),
        'GCASH': np.array([0.0, 0.0, 0.0]),
        'GSHARE': np.array([0.0, 0.0, 0.0]),
        'SECTOR': ['新能源汽车', '锂电池']
        # 注意：这里故意不包含TCAP字段
    }
    
    try:
        # 测试build_trading_data函数
        buf = StringIO()
        research.build_trading_data(buf, symbol, mock_data)
        result = buf.getvalue()
        
        print("=== 交易数据构建成功 ===")
        print("输出长度:", len(result))
        print("\n输出内容:")
        print(result)
        
        # 检查是否包含换手率信息
        if "换手率" in result:
            print("❌ 错误：仍然包含换手率信息（应该被跳过）")
            return False
        else:
            print("✅ 正确：未包含换手率信息（因为TCAP字段缺失）")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tcap_present():
    """测试TCAP字段存在时的处理"""
    symbol = "SZ300711"
    
    print(f"\n=== 测试TCAP字段存在的情况 ===\n")
    
    # 模拟有TCAP字段的数据
    mock_data = {
        'DATE': np.array([1640995200, 1641081600, 1641168000]),
        'OPEN': np.array([10.0, 10.5, 11.0]),
        'HIGH': np.array([10.5, 11.0, 11.5]),
        'LOW': np.array([9.5, 10.0, 10.5]),
        'CLOSE': np.array([10.2, 10.8, 11.2]),
        'VOLUME': np.array([1000000, 1200000, 1100000]),
        'AMOUNT': np.array([10200000, 12960000, 12320000]),
        'CLOSE2': np.array([10.2, 10.8, 11.2]),
        'PRICE': np.array([10.2, 10.8, 11.2]),
        'GCASH': np.array([0.0, 0.0, 0.0]),
        'GSHARE': np.array([0.0, 0.0, 0.0]),
        'TCAP': np.array([500000, 520000, 540000]),  # 包含TCAP字段
        'SECTOR': ['新能源汽车', '锂电池']
    }
    
    try:
        # 测试build_trading_data函数
        buf = StringIO()
        research.build_trading_data(buf, symbol, mock_data)
        result = buf.getvalue()
        
        print("=== 交易数据构建成功 ===")
        print("输出长度:", len(result))
        
        # 检查是否包含换手率信息
        if "换手率" in result:
            print("✅ 正确：包含换手率信息（因为TCAP字段存在）")
            return True
        else:
            print("❌ 错误：未包含换手率信息（应该包含）")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试TCAP字段处理修复...\n")
    
    test1 = test_tcap_fix()
    test2 = test_tcap_present()
    
    if test1 and test2:
        print("\n🎉 所有测试通过 - TCAP字段处理修复成功")
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)