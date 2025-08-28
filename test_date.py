import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from qtf_mcp import research

async def test_date_format():
    symbol = "SH600276"
    
    # 获取原始数据
    raw_data = await research.load_raw_data(symbol, "2024-08-01", "2024-08-28")
    
    print("时间戳数据类型:", type(raw_data["DATE"]))
    print("时间戳数组:", raw_data["DATE"])
    print("最后一个时间戳:", raw_data["DATE"][-1])
    print("时间戳值:", raw_data["DATE"][-1])
    
    # 尝试不同的转换方式
    import datetime
    ts = raw_data["DATE"][-1]
    
    # 方式1: 纳秒级时间戳
    try:
        date1 = datetime.datetime.fromtimestamp(ts / 1e9)
        print("纳秒级转换:", date1)
    except Exception as e:
        print("纳秒级转换失败:", e)
    
    # 方式2: 毫秒级时间戳
    try:
        date2 = datetime.datetime.fromtimestamp(ts / 1000)
        print("毫秒级转换:", date2)
    except Exception as e:
        print("毫秒级转换失败:", e)
    
    # 方式3: 直接作为秒级时间戳
    try:
        date3 = datetime.datetime.fromtimestamp(ts)
        print("秒级转换:", date3)
    except Exception as e:
        print("秒级转换失败:", e)

if __name__ == "__main__":
    asyncio.run(test_date_format())