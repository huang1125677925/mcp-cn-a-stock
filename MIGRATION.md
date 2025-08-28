# 数据源迁移说明

## 概述
本项目已将数据源从MSD（Market Securities Data）迁移至AkShare，这是一个开源的金融数据接口库。

## 主要变更

### 1. 依赖项变更
- **移除**: qtf库依赖及本地.whl文件
- **新增**: akshare、pandas、numpy、ta-lib

### 2. 数据源变更
- **原数据源**: MSD专业金融数据服务
- **新数据源**: AkShare开源数据接口
- **数据覆盖**: A股股票、指数、ETF等

### 3. 功能变更
- **保持**: 所有原有接口不变
- **增强**: 支持更多股票代码格式
- **优化**: 数据获取速度提升

## 环境配置

### 创建虚拟环境
```bash
/opt/homebrew/bin/python3 -m venv venv
source venv/bin/activate
```

### 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

### 启动服务
```bash
source venv/bin/activate
python3 main.py --transport stdio
```

### 测试数据获取
```python
import asyncio
from qtf_mcp.datafeed import load_data_akshare

async def test():
    data = await load_data_akshare('000001', '2024-01-01', '2024-01-10')
    print(f"获取数据成功，包含字段: {list(data.keys())}")

asyncio.run(test())
```

## 数据质量说明

### 优势
1. **免费**: 无需付费API密钥
2. **开源**: 代码透明，可定制
3. **丰富**: 支持多种数据类型

### 限制
1. **实时性**: 数据延迟约15分钟
2. **稳定性**: 依赖网络连接质量
3. **完整性**: 部分历史数据可能不完整

## 故障排除

### 常见问题
1. **网络连接**: 确保能正常访问互联网
2. **日期格式**: 使用YYYY-MM-DD格式
3. **股票代码**: 支持000001、SH600000等格式

### 调试方法
```bash
# 查看详细日志
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from qtf_mcp.datafeed import load_data_akshare
import asyncio
asyncio.run(load_data_akshare('000001', '2024-01-01', '2024-01-10'))
"
```