# SSE接口使用说明

## 快速开始

### 启动SSE服务
```bash
# 激活虚拟环境
source venv/bin/activate

# 启动SSE接口（端口8080）
python3 main.py --transport sse --port 8080
```

### 支持的传输方式
- **stdio**: 标准输入输出（命令行模式）
- **sse**: Server-Sent Events（推荐用于Web应用）
- **http**: HTTP流式传输

## SSE接口详情

### 基础信息
- **端口**: 8080（可配置）
- **协议**: Server-Sent Events
- **内容类型**: text/event-stream
- **编码**: UTF-8

### 启动服务
```bash
# 基本启动
python3 main.py --transport sse

# 指定端口
python3 main.py --transport sse --port 8080

# 后台运行
nohup python3 main.py --transport sse --port 8080 > mcp.log 2>&1 &
```

### 客户端连接示例

#### JavaScript客户端
```javascript
const eventSource = new EventSource('http://localhost:8080/sse');

eventSource.onmessage = function(event) {
    console.log('收到消息:', event.data);
};

eventSource.onerror = function(error) {
    console.error('连接错误:', error);
};
```

#### Python客户端
```python
import requests
import json

response = requests.get('http://localhost:8080/sse', stream=True)
for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8').replace('data: ', ''))
        print('收到数据:', data)
```

#### curl测试
```bash
curl -N http://localhost:8080/sse
```

### 可用的MCP工具

通过SSE接口，你可以访问以下股票分析工具：

1. **brief**: 简要股票分析
   - 输入: 股票代码（如：000001）
   - 输出: 基本信息和当前价格

2. **medium**: 中等详细分析
   - 输入: 股票代码
   - 输出: 价格、成交量、技术指标

3. **full**: 完整分析报告
   - 输入: 股票代码
   - 输出: 全面技术分析、财务数据、资金流向

### 集成示例

#### 与CherryStudio集成
```json
{
  "mcpServers": {
    "a-stock": {
      "command": "/path/to/venv/bin/python3",
      "args": ["/path/to/main.py", "--transport", "sse", "--port", "8080"],
      "env": {}
    }
  }
}
```

#### 与DeepChat集成
```json
{
  "server_name": "A股数据服务",
  "server_type": "sse",
  "server_url": "http://localhost:8080"
}
```

### 故障排除

#### 端口占用
```bash
# 检查端口占用
lsof -i :8080

# 更换端口
python3 main.py --transport sse --port 8081
```

#### 防火墙设置
```bash
# macOS允许端口
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/venv/bin/python3
```

#### 网络访问
如需局域网访问：
```bash
# 绑定到所有接口
python3 main.py --transport sse --port 8080 --host 0.0.0.0
```

### 性能优化

#### 生产环境部署
```bash
# 使用进程管理器
pip install supervisor

# 或使用systemd服务
# 创建 /etc/systemd/system/qtf-mcp.service
```

#### 日志配置
```bash
# 设置日志级别
export LOG_LEVEL=INFO
python3 main.py --transport sse --port 8080
```

### 监控检查

#### 健康检查
```bash
# 检查服务状态
curl -f http://localhost:8080/health || echo "服务异常"

# 测试工具调用
curl -X POST http://localhost:8080/tools/brief \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"symbol": "000001"}}'
```

## 注意事项

1. **数据延迟**: AkShare数据有约15分钟延迟
2. **网络要求**: 需要稳定的互联网连接
3. **频率限制**: 建议合理控制请求频率
4. **错误处理**: 实现重试机制以应对网络波动