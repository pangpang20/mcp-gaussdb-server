#!/bin/bash
# 启动 MCP 服务前自动激活虚拟环境，并设置动态库路径

cd /opt/mcp/mcp-gaussdb-server/gaussdb-server

# 激活 venv
source .venv/bin/activate

# 设置环境变量
export LD_LIBRARY_PATH=/tmp/lib:$LD_LIBRARY_PATH
export LD_PRELOAD=/tmp/lib/libssl.so.3:/tmp/lib/libcrypto.so.3

# 启动 MCP 逻辑
exec uv run gaussdb_mcp_server.py
