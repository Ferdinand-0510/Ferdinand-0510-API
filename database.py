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
    try:
        # 檢查環境變量
        logger.info(f"檢查環境變量: LD_LIBRARY_PATH={os.getenv('LD_LIBRARY_PATH')}")
        
        # 檢查驅動文件
        driver_path = "/usr/lib/libmsodbcsql-18.so"
        if os.path.exists(driver_path):
            logger.info(f"驅動文件存在: {driver_path}")
        else:
            logger.error(f"驅動文件不存在: {driver_path}")

        # 檢查 ODBC 配置
        try:
            with open('/etc/odbcinst.ini', 'r') as f:
                logger.info("ODBC 配置內容:")
                logger.info(f.read())
        except Exception as e:
            logger.error(f"無法讀取 ODBC 配置: {e}")

        server = "carlweb-server.database.windows.net"
        database = "CarlWeb"
        username = "carluser"
        password = os.getenv('DB_PASSWORD')

        # 獲取可用的驅動程序
        drivers = pyodbc.drivers()
        logger.info(f"可用的 ODBC 驅動: {drivers}")

        # 嘗試連接
        conn_str = (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
            'Encrypt=yes;'
            'TrustServerCertificate=yes;'
        )

        logger.info("嘗試建立連接...")
        conn = pyodbc.connect(conn_str)
        logger.info("數據庫連接成功！")
        return conn

    except Exception as e:
        logger.error(f"數據庫連接錯誤: {str(e)}")
        logger.error(f"連接字符串: {conn_str}")
        raise