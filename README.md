# 简介

这是一个为大模型提供 A 股数据的的 MCP(Model Content Protocol) 服务。

# MCP Tools

目前提供一下的若干工具：

- brief: 给定股票的基本信息，行情数据
- medium: 提供所有基本数据和一些财务数据
- full: 提供所有中等数据和技术指标

# 使用方法

由于股票的数据比较庞大，所以我们提供了一个公开的服务地址, 查看 [tests/test.sh](tests/test.sh) 文件，里面有一些测试用例以及相关的使用方法。
