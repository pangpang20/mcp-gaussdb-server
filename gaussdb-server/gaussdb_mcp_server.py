import logging
from contextlib import asynccontextmanager
import gaussdb
import os
import json
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from gaussdb import AsyncConnection
from gaussdb.rows import dict_row
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Query


# 加载环境变量
load_dotenv()

# 设置环境变量
os.environ['GAUSSDB_IMPL'] = 'python'
host = os.getenv("GAUSSDB_HOST", "127.0.0.1")
port = int(os.getenv("GAUSSDB_PORT", "8000"))
user = os.getenv("GAUSSDB_USER", "root")
password = os.getenv("GAUSSDB_PASSWORD", "password")
database = os.getenv("GAUSSDB_DATABASE", "postgres")

# 日志配置
log_path = os.getenv("GAUSSDB_MCP_LOG", "mcp.log")

logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='[%(asctime)s] - %(levelname)s - %(lineno)d - %(message)s ',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger("GaussDBMCP")

# 初始化 FastMCP
mcp = FastMCP("GaussDBMCP")

# 自定义 JSON 序列化器，处理 datetime 和 date 类型
def custom_json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

class GaussDBMCP:
    """
    数据库连接管理
    """
    def __init__(
            self,
            host: str = host,
            port: int = port,
            user: str = user,
            password: str = password,
            database: str = database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn: Optional[AsyncConnection] = None
        logger.info(
            f"""
            Initialized GaussDBMCP with
            host={host},
            port={port},
            database={database}
        """)

    @asynccontextmanager
    async def get_connection(self) -> AsyncConnection:
        conn = await gaussdb.AsyncConnection.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.database,
            row_factory=dict_row
        )
        try:
            yield conn
        finally:
            await conn.close()


    async def close(self):
        """关闭数据库连接"""
        if self.conn and not self.conn.closed:
            logger.info("Closing database connection")
            await self.conn.close()
            logger.info("Connection closed")
        else:
            logger.info("No open connection to close")

# 实例化
tool_instance = GaussDBMCP()

@mcp.tool(description="""
创建数据库（非事务方式）

Args:
    db_name (str): 数据库名称，例如 "my_database"。

Returns:
    str: 确认消息，例如 "Successfully created database: <db_name>"

""")
async def create_database(db_name: Annotated[str, Query(description="""数据库名称，例如 "my_database"。应符合 GaussDB 命名规范（如不以数字开头，不能包含特殊字符等）""")]
) -> str:
    try:
        conn = await gaussdb.AsyncConnection.connect(
            host=tool_instance.host,
            port=tool_instance.port,
            user=tool_instance.user,
            password=tool_instance.password,
            dbname='postgres',
            autocommit=True
        )
        await conn.execute(f"CREATE DATABASE {db_name}")
        await conn.close()
        suc_msg = f"Successfully created database: {db_name}"
        logger.info(suc_msg)
        return suc_msg
    except Exception as e:
        err_msg = f"""
            Failed to create database {db_name}.
            Error messages: {str(e)}
        """
        logger.error(err_msg)
        raise Exception(err_msg)


@mcp.tool(description="""
创建表
Args:
    table_name (str): 表名称，例如 "my_table"。
    schema (str): 表结构定义，例如 "id INT PRIMARY KEY, name VARCHAR(255)"。

Returns:
    str: 确认消息，例如 "Successfully created table: <table_name>

""")
async def create_table(
    table_name: Annotated[
        str, 
        Query(description="""表名称，例如 "my_table"。必须是有效的 GaussDB 表名称，遵循命名规则（如不以数字开头，不能包含特殊字符等）""")
    ], 
    schema: Annotated[
        str, 
        Query(description="表结构定义，例如 'id INT PRIMARY KEY, name VARCHAR(255)'。必须是一个合法的 SQL 语句，用于定义表的列和约束， 关键字符合GaussDB要求")
    ]) -> str:
    if not schema.strip():
        err_msg = f"Cannot create table {table_name}: schema is empty."
        logger.error(err_msg)
        raise ValueError(err_msg)

    try:
        async with tool_instance.get_connection() as conn:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} ({schema})
            """)
            await conn.commit()
            suc_msg = f"Successfully created table: {table_name}"
            logger.info(suc_msg)
            return suc_msg
    except Exception as e:
        err_msg = f"Failed to create table {table_name}: {str(e)}"
        logger.error(err_msg)
        raise Exception(err_msg)

@mcp.tool(description="""
删除表

Args:
    table_name (str): 表名称，例如 "my_table"。

Returns:
    str: 确认消息，例如 "Successfully drop table: <table_name>

""")
async def drop_table(table_name: Annotated[
    str,
    Query(description="""表名称，例如 "my_table"。必须是有效的 GaussDB 表名称，遵循命名规则（如不以数字开头，不能包含特殊字符等）""")
    ]) -> str:
    try:
        async with tool_instance.get_connection() as conn:
            await conn.execute(f"""
                DROP TABLE IF EXISTS {table_name}
            """)
            await conn.commit()
            suc_msg = f"Successfully drop table: {table_name}"
            logger.info(suc_msg)
            return suc_msg
    except Exception as e:
        err_msg = f"Failed to drop table {table_name}: {str(e)}"
        logger.error(err_msg)
        raise Exception(err_msg)

@mcp.tool(description="""
获取建表语句

Args:
    table_name (str): 表名称，例如 "my_table"。

Returns:
    str: 返回建表语句

""")
async def get_create_table_sql(
    table_name: Annotated[
        str,
        Query(description="""表名称，例如 "my_table"。必须是有效的 GaussDB 表名称，遵循命名规则（如不以数字开头，不能包含特殊字符等）""")
    ]
) -> str:
    query = """
        SELECT 
            'CREATE TABLE ' || relname || E'\n(\n' ||
            string_agg(
                '    ' || column_name || ' ' || data_type ||
                CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END,
                E',\n'
            ) || E'\n);' AS create_table_sql
        FROM (
            SELECT 
                c.relname,
                a.attname AS column_name,
                pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
                col.is_nullable
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_attribute a ON a.attrelid = c.oid
            JOIN information_schema.columns col 
                ON col.table_name = c.relname AND col.column_name = a.attname
            WHERE c.relkind = 'r'
                AND a.attnum > 0
                AND NOT a.attisdropped
                AND c.relname = %s
            ORDER BY a.attnum
        ) AS table_info
        GROUP BY relname
    """
    try:
        async with tool_instance.get_connection() as conn:
            cursor = await conn.execute(query, (table_name,))
            results = await cursor.fetchall()
            if results:
                logger.info(f"Successfully generated create SQL for {table_name}")
                return results[0]["create_table_sql"]
            else:
                raise Exception(f"Table '{table_name}' not found.")
    except Exception as e:
        err_msg = f"Failed to get create table SQL for '{table_name}': {e}"
        logger.error(err_msg)
        raise Exception(err_msg)

@mcp.tool(description="""
插入数据

Args:
    table_name (str): 表名称，例如 "my_table"。
    data: 要插入的数据字典，例如 {"id": 1, "name": "John"}

Returns:
    str: 确认消息，例如 "Successfully inserted data into <table_name>"

""")
async def insert(table_name:  Annotated[
    str,
    Query(description="""表名称，例如 "my_table"。必须是有效的 GaussDB 表名称，遵循命名规则（如不以数字开头，不能包含特殊字符等）""")
    ], data: Annotated[
    Dict[str, Any],
    Query(description="""要插入的数据字典，例如 {"id": 1, "name": "John"}""")
    ]) -> str:
    if not data:
        err_msg = f"Insert data cannot be empty"
        logger.error(err_msg)
        raise ValueError(err_msg)

    async with tool_instance.get_connection() as conn:
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"""
            INSERT INTO {table_name} ({columns}) VALUES ({placeholders})
            """
            await conn.execute(query, list(data.values()))
            await conn.commit()
            suc_msg = f"""
            Successfully inserted data into {table_name}: {data}
            """
            logger.info(suc_msg)
            return suc_msg
        except Exception as e:
            await conn.rollback()
            err_msg = f"Failed to insert data into {table_name}: {str(e)}"
            logger.error(err_msg)
            raise Exception(err_msg)

@mcp.tool(description="""
查询数据

Args:
    table_name (str): 表名称，例如 "my_table"。
    condition: 查询条件字典（可选），查询表中所有数据时不需要条件，例如 {"id": 1}

Returns:
    str: 查询结果列表

""")
async def select(table_name: Annotated[
    str, Query(description="""表名称，例如 "my_table"。必须是有效的 GaussDB 表名称，遵循命名规则（如不以数字开头，不能包含特殊字符等）""")],
    condition: Annotated[Optional[Dict[str, Any]], Query(description="""查询条件字典（可选），查询表中所有数据时不需要条件，例如 {"id": 1}""")]) -> str:
    async with tool_instance.get_connection() as conn:
        try:
            query = f"SELECT * FROM {table_name}"
            params = []
            if condition:
                where_clause = ' AND '.join(
                    f"{k} = %s" for k in condition.keys())
                query += f" WHERE {where_clause}"
                params = list(condition.values())

            cursor = await conn.execute(query, params)
            results = await cursor.fetchall()
            logger.info(f"""
                Successfully selected {len(results)} rows from {table_name}
            """)
            return json.dumps(results, default=custom_json_serializer, ensure_ascii=False)
        except Exception as e:
            err_msg = f"Failed to select from {table_name}: {str(e)}"
            logger.error(err_msg)
            raise Exception(err_msg)

@mcp.tool(description="""
更新数据

Args:
    table_name (str): 表名称，例如 "my_table"
    data: 要更新的数据字典，例如 {"name": "John"}
    condition: 更新条件字典（可选），例如 {"id": 1}

Returns:
    str: 确认消息，例如 "Successfully updated <table_name>"

""")
async def update(table_name: Annotated[
    str, Query(description="""表名称，例如 "my_table"。必须是有效的 GaussDB 表名称，遵循命名规则（如不以数字开头，不能包含特殊字符等）""")],
    data: Annotated[Dict[str, Any], Query(description="""要更新的数据字典，例如 {"name": "John"}""")],
    condition: Annotated[Optional[Dict[str, Any]], Query(description="""更新条件字典（可选），例如 {"id": 1""")]) -> str:
    async with tool_instance.get_connection() as conn:
        try:
            set_clause = ', '.join(f"{k} = %s" for k in data.keys())
            where_clause = ' AND '.join(
                f"{k} = %s" for k in condition.keys())
            query = f"""
            UPDATE {table_name} SET {set_clause} WHERE {where_clause}
            """
            params = list(data.values()) + list(condition.values())

            await conn.execute(query, params)
            await conn.commit()
            suc_msg = f"""
            Successfully updated {table_name} with data: {data}
            """
            logger.info(suc_msg)
            return suc_msg
        except Exception as e:
            await conn.rollback()
            err_msg = f"Failed to update {table_name}: {str(e)}"
            logger.error(err_msg)
            raise Exception(err_msg)

@mcp.tool(description="""
删除数据

Args:
    table_name (str): 表名称，例如 "my_table"
    condition: 删除条件字典（可选），例如 {"id": 1}

Returns:
    str: 确认消息，例如 "Successfully deleted from <table_name>"

""")
async def delete(table_name: Annotated[
    str, Query(description="""表名称，例如 "my_table"。必须是有效的 GaussDB 表名称，遵循命名规则（如不以数字开头，不能包含特殊字符等）""")],
    condition: Annotated[Optional[Dict[str, Any]], Query(description="""删除条件字典（可选），删除表中所有数据时不需要条件，例如 {"id": 1}""")]) -> str:
    async with tool_instance.get_connection() as conn:
        try:
            query = f"DELETE FROM {table_name}"
            params = []
            if condition:
                where_clause = ' AND '.join(f"{k} = %s" for k in condition.keys())
                query += f" WHERE {where_clause}"
                params = list(condition.values())

            await conn.execute(query, params)
            await conn.commit()
            success_message = (
                f"Successfully deleted from {table_name} "
                f"with condition: {condition if condition else 'None'}"
            )
            logger.info(success_message)
            return success_message
        except Exception as e:
            await conn.rollback()
            err_msg = f"Failed to delete from {table_name}: {str(e)}"
            logger.error(err_msg)
            raise Exception(err_msg)



if __name__ == "__main__":
    mcp.run(transport="stdio")
