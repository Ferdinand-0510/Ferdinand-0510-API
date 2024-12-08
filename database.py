import os
import pyodbc
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def create_connection():
    """
    创建与 Azure SQL Database 的连接
    """
    server = "carlweb-server.database.windows.net"
    database = "CarlWeb"
    username = "carluser"
    password = os.getenv('DB_PASSWORD')

    try:
        # 打印详细的连接信息（不包含密码）
        logger.info(f"尝试连接到服务器: {server}, 数据库: {database}, 用户: {username}")

        # 检查环境变量
        if not password:
            logger.error("数据库密码未设置")
            raise ValueError("数据库密码未设置")

        # 使用 pyodbc 连接
        conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
            'Encrypt=yes;'
            'TrustServerCertificate=no;'
        )

        # 打印连接字符串（不包含密码）
        logger.info(f"连接字符串: {conn_str.replace(password, '****')}")

        conn = pyodbc.connect(conn_str)
        logger.info(f"成功连接到数据库: {database}")
        return conn

    except Exception as e:
        # 更详细的错误日志
        logger.error(f"数据库连接错误: {e}")
        raise