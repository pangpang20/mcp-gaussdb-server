# 操作GaussDB的MCP Server

## 概述

本用例用于演示如何操作GaussDB的MCP Server。
需要使用到连接GaussDB的纯python驱动，结合GaussDB提供的pq连接GaussDB数据库。
MCP Server的开发基于标准的MCP协议，因此可以使用任何支持MCP协议的客户端进行连接和操作。
MCP客户端可以使用Python、Java等语言编写。本用例使用CLINE工具进行演示。
LLM使用ModelArts提供的DeepSeek V3模型。

## 操作步骤

### 克隆项目

克隆github项目代码，大约需要1分钟

```bash
git clone https://github.com/pangpang20/mcp-gaussdb-server.git
cd mcp-gaussdb-server/gaussdb-server

# 安装python310,大约5分钟
# 开发者空间中的python版本为3.9.9，而mcp服务需要安装python310
sh install_python310.sh 

```

### 创建虚拟环境

创建虚拟环境，并激活

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python3 -V # 查看python版本, 确保是3.10.14
```

### 安装依赖并配置环境变量

安装mcp和gaussdb驱动

```bash
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


# 初始化pq连接,大约1分钟
sh init_pq.sh

# 检查
ip list | grep gaussdb

```

配置GaussDB数据库信息

```bash
cp .env.sample .env

# 配置数据库连接信息
# 需要GaussDB的EIP和端口，用户名密码等信息
vim .env
GAUSSDB_HOST=xxx
GAUSSDB_PORT=8000
GAUSSDB_USER=root
GAUSSDB_PASSWORD=xxx
GAUSSDB_DATABASE=postgres
GAUSSDB_MCP_LOG=/tmp/mcp.log
# 输入:wq 保存退出

```

### MCP Server开发

编写GaussDBMCP类，用于连接数据库并执行SQL查询。
现在实现了建库，建表，插入数据，查询数据等功能，如需实现其他的功能，可以参考已有的代码进行扩展。

```bash
cat gaussdb_mcp_server.py

```

### 启动server

启动封装的mcp server

```bash
sh start_mcp_server.sh
```

### 安装vscode

使用vscode连接mcp server，下载vscode需要大约10分钟

```bash
cd ~
wget https://vscode.download.prss.microsoft.com/dbazure/download/stable/7adae6a56e34cb64d08899664b814cf620465925/code-1.102.1-1752598762.el8.aarch64.rpm
rpm -ivh code-1.102.1-1752598762.el8.aarch64.rpm 

```

安装Cline插件
在 extensions marketplace搜索： Cline 并安装


