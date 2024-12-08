import os
import pyodbc
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

def get_odbc_drivers():
    """列出所有可用的 ODBC 驱动"""
    try:
        drivers = pyodbc.drivers()
        logger.debug(f"可用的 ODBC 驱动: {drivers}")
        return drivers
    except Exception as e:
        logger.error(f"获取 ODBC 驱动时出错: {e}")
        return []

def create_connection():
    """创建与 Azure SQL Database 的连接"""
    server = "carlweb-server.database.windows.net"
    database = "CarlWeb"
    username = "carluser"
    password = os.getenv('DB_PASSWORD')

    # 先检查可用驱动
    available_drivers = get_odbc_drivers()
    logger.debug(f"可用驱动: {available_drivers}")

    try:
        # 尝试使用多个驱动名称
        driver_attempts = [
            "ODBC Driver 17 for SQL Server",
            "SQL Server",
            "FreeTDS"
        ]

        for driver in driver_attempts:
            try:
                conn_str = (
                    f'DRIVER={{{driver}}};'
                    f'SERVER={server};'
                    f'DATABASE={database};'
                    f'UID={username};'
                    f'PWD={password};'
                    'Encrypt=yes;'
                )

                logger.debug(f"尝试使用驱动 {driver}")
                conn = pyodbc.connect(conn_str)
                logger.info(f"成功使用 {driver} 连接到数据库")
                return conn

            except Exception as driver_error:
                logger.warning(f"使用 {driver} 连接失败: {driver_error}")

        # 如果所有尝试都失败
        raise Exception("无法建立数据库连接")

    except Exception as e:
        logger.error(f"数据库连接错误: {e}")
        raise