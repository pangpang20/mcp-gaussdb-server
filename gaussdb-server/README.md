# 操作GaussDB的MCP Server

## 概述

本用例用于演示如何操作GaussDB的MCP Server。
需要使用到连接GaussDB的纯python驱动，结合GaussDB提供的pq连接GaussDB数据库。
MCP Server的开发基于标准的MCP协议，因此可以使用任何支持MCP协议的客户端进行连接和操作。
MCP客户端可以使用Python、Java等语言编写。本用例使用CLINE工具进行演示。
LLM使用ModelArts提供的DeepSeek V3模型。

## 前提条件

克隆项目

```bash
git clone https://github.com/pangpang20/mcp-gaussdb-server.git

```

安装依赖

```bash

pip install -r requirements.txt

```

## 操作步骤

