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
        driver_paths = [
            "/usr/lib/libmsodbcsql-18.so",
            "/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.so"
        ]
        
        for path in driver_paths:
            if os.path.exists(path):
                logger.info(f"找到驅動文件: {path}")
            else:
                logger.warning(f"驅動文件不存在: {path}")

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

        # 嘗試不同的驅動程序名稱
        driver_names = [
            "ODBC Driver 18 for SQL Server",
            "{ODBC Driver 18 for SQL Server}",
            "msodbcsql18",
            "/usr/lib/libmsodbcsql-18.so"
        ]

        last_error = None
        for driver in driver_names:
            try:
                conn_str = (
                    f'DRIVER={driver};'
                    f'SERVER={server};'
                    f'DATABASE={database};'
                    f'UID={username};'
                    f'PWD={password};'
                    'Encrypt=yes;'
                    'TrustServerCertificate=yes;'
                )

                logger.info(f"嘗試使用驅動: {driver}")
                conn = pyodbc.connect(conn_str)
                logger.info(f"使用 {driver} 連接成功！")
                return conn

            except Exception as e:
                last_error = e
                logger.warning(f"使用 {driver} 連接失敗: {str(e)}")
                continue

        # 如果所有嘗試都失敗
        error_msg = (
            f"數據庫連接錯誤:\n"
            f"最後錯誤: {str(last_error)}\n"
            f"服務器: {server}\n"
            f"數據庫: {database}\n"
            f"用戶名: {username}\n"
            f"可用驅動程序: {drivers}\n"
            f"嘗試的驅動程序: {driver_names}"
        )
        logger.error(error_msg)
        raise Exception(error_msg)

    except Exception as e:
        logger.error(f"創建連接時發生錯誤: {str(e)}")
        raise