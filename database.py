import os
import pyodbc
import logging

# 配置 logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_connection():
    server = "carlweb-server.database.windows.net"
    database = "CarlWeb"
    username = "carluser"
    password = os.getenv('DB_PASSWORD')

    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password}"
    )

    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        logger.error(f"数据库连接错误: {e}")
        raise
