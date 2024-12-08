import os
import pyodbc
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def create_connection():
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')

    logger.info(f"連接到 {server}/{database}")

    driver_attempts = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
    ]

    for driver in driver_attempts:
        try:
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                "Encrypt=yes;"
            )

            conn = pyodbc.connect(conn_str)
            logger.info(f"成功使用 {driver} 連接")
            return conn
        except Exception as e:
            logger.warning(f"使用 {driver} 連接失敗: {e}")

    raise Exception("無法建立資料庫連接")