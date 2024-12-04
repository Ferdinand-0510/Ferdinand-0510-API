import os
import pymssql
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    """
    創建與 Azure SQL Database 的連接
    """
    try:
        # 從環境變數獲取連接資訊
        server = "carlweb-server.database.windows.net"
        database = "CarlWeb"
        username = "carl"
        password = os.getenv('DB_PASSWORD')
        
        # 建立連接
        conn = pymssql.connect(
            server=server, 
            user=username,
            password=password, 
            database=database,
            port='1433',
            as_dict=True,
            charset='utf8',
            tds_version='7.4'  # 使用較新的 TDS 版本
        )
        
        print(f"成功連接到資料庫: {database}")
        return conn
        
    except Exception as e:
        print(f"資料庫連接錯誤: {str(e)}")
        print(f"連接詳情: server={server}, user={username}, database={database}")
        raise

def test_connection():
    """
    測試資料庫連接是否成功
    """
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        print("資料庫連接成功！")
        conn.close()
        return True
    except Exception as e:
        print(f"連接測試失敗: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()