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
    """創建與 Azure SQL Database 的連接"""
    server = "carlweb-server.database.windows.net"
    database = "CarlWeb"
    username = "carluser"
    password = os.getenv('DB_PASSWORD')

    # 獲取可用的驅動程序
    drivers = pyodbc.drivers()
    logger.info(f"可用的 ODBC 驅動: {drivers}")

    # 嘗試不同的驅動程序
    driver_attempts = [
        "ODBC Driver 18 for SQL Server",  # 首選 18 版本
        "ODBC Driver 17 for SQL Server",
        "msodbcsql18",
        "msodbcsql17"
    ]

    last_error = None
    for driver in driver_attempts:
        try:
            conn_str = (
                f'DRIVER={{{driver}}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password};'
                'Encrypt=yes;'
                'TrustServerCertificate=yes;'  # 添加此行以處理 SSL 問題
            )

            logger.info(f"嘗試使用驅動: {driver}")
            conn = pyodbc.connect(conn_str)
            logger.info(f"成功使用 {driver} 連接到數據庫")
            return conn

        except Exception as e:
            last_error = e
            logger.warning(f"使用 {driver} 連接失敗: {str(e)}")
            continue

    # 如果所有嘗試都失敗
    error_msg = f"""
    數據庫連接失敗:
    最後錯誤: {str(last_error)}
    可用驅動: {drivers}
    服務器: {server}
    數據庫: {database}
    用戶名: {username}
    """
    logger.error(error_msg)
    raise Exception(error_msg)