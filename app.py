import os
from dotenv import load_dotenv
from flask import Flask, jsonify, session, request, send_from_directory
from flask_cors import CORS

from dotenv import load_dotenv
import pymssql
import uuid
import bcrypt
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from database import create_connection

load_dotenv()

# 創建 Flask 應用程序實例
application = Flask(__name__)
app = application  # 添加這行，為了兼容性

app.secret_key = os.getenv('SECRET_KEY', '0877283719e292c601be9bdf87b99a21ca96d301d4be57c7480b92506566d53b')

CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": [
            "https://ferdinand-0510.github.io",
            "https://webtest-api.onrender.com",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

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

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# 確保這個在文件的最後
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)