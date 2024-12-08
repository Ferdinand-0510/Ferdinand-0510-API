import os
import pymssql
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def create_connection():
    """
    創建與 Azure SQL Database 的連接
    """
    try:
        server = "carlweb-server.database.windows.net"
        database = "CarlWeb"
        username = "carluser"
        password = os.getenv('DB_PASSWORD', 'Golen3857.')  # 提供默認值
        
        logger.info(f"嘗試連接到服務器: {server}, 數據庫: {database}, 用戶: {username}")
        
        # 使用 pymssql 連接
        conn = pymssql.connect(
            server=server, 
            user=username,
            password=password, 
            database=database,
            as_dict=True,
            charset='utf8'
        )
        
        logger.info(f"成功連接到資料庫: {database}")
        return conn
        
    except Exception as e:
        logger.error(f"資料庫連接錯誤: {str(e)}")
        logger.error(f"連接詳情: server={server}, user={username}, database={database}")
        raise