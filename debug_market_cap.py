import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from qtf_mcp import research

async def debug_market_cap():
    symbol = "SH600276"
    
    # 获取原始数据
    raw_data = await research.load_raw_data(symbol, "2024-08-01", "2024-08-28")
    
    print("数据字段:", list(raw_data.keys()))
    
    if "TCAP" in raw_data:
        print("TCAP字段:", raw_data["TCAP"])
        print("TCAP最后一个值:", raw_data["TCAP"][-1])
        print("TCAP类型:", type(raw_data["TCAP"][-1]))
    
    if "CLOSE2" in raw_data:
        print("CLOSE2字段:", raw_data["CLOSE2"])
        print("CLOSE2最后一个值:", raw_data["CLOSE2"][-1])
        print("CLOSE2类型:", type(raw_data["CLOSE2"][-1]))
    
    # 计算正确的市值
    if "TCAP" in raw_data and "CLOSE2" in raw_data:
        tcap = raw_data["TCAP"][-1]
        close2 = raw_data["CLOSE2"][-1]
        
        print(f"\n原始计算: {tcap} * {close2} = {tcap * close2}")
        print(f"除以1万: {(tcap * close2) / 10000}")
        print(f"除以1亿: {(tcap * close2) / 100000000}")

if __name__ == "__main__":
    asyncio.run(debug_market_cap())