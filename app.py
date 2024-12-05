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

This_customer='測試'
def get_This_Key():
    try:
        with create_connection() as conn_sql_server:
            with conn_sql_server.cursor() as cursor:
                cursor.execute("SELECT Uuid FROM WebLoginKey WHERE Name = ?",(This_customer,))
                row = cursor.fetchone()
                if row:
                    return row[0]
    except Exception as e:
        return print(str(e))
This_key = get_This_Key()
print("This_key:",This_key)



#--------------------------------------------------------取得最新資料--------------------------------------------------------
@app.route('/api/get_HomeNews', methods=['GET'])
def get_HomeNews():
    try:
        news = get_HomeNews_logic()
        return jsonify({"news": news}), 200  # 包裝在 news 鍵中
    except Exception as e:
        print(f"獲取新聞錯誤: {str(e)}")
        return jsonify({"error": str(e)}), 500

def get_HomeNews_logic():
    try:
        with create_connection() as conn_sql_server:
            with conn_sql_server.cursor() as cursor:
                cursor.execute("SELECT * FROM News WHERE Customer_Uuid = ? AND Deleted_At IS NULL ORDER BY Created_At DESC", (This_key,))
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                result = []
                for row in rows:
                    row_dict = {}
                    for i, column in enumerate(columns):
                        value = row[i]
                        # 處理不同類型的數據
                        if isinstance(value, bytes):
                            row_dict[column] = value.decode('utf-8', errors='ignore')
                        elif isinstance(value, datetime):
                            row_dict[column] = value.isoformat()
                        elif column == 'Publish_Date' and value:
                            # 特別處理 Publish_Date
                            try:
                                if isinstance(value, str) and '\x00' in value:
                                    # 處理特殊格式的日期
                                    row_dict[column] = datetime.now().isoformat()
                                else:
                                    row_dict[column] = value.isoformat() if isinstance(value, datetime) else str(value)
                            except Exception as e:
                                print(f"日期處理錯誤: {str(e)}")
                                row_dict[column] = None
                        else:
                            row_dict[column] = value
                    result.append(row_dict)
                
                print("處理後的結果:", result)
                return result
    except Exception as e:
        print(f"獲取新聞邏輯錯誤: {str(e)}")
        raise
with app.app_context():
    Now_HomeNews = get_HomeNews_logic()

@app.route('/api/add_news', methods=['POST'])
def add_news():
    try:
        data = request.json
        print("接收到的新聞數據:", data)  # 調試用
        
        # 驗證必要欄位
        if not data.get('title') or not data.get('content'):
            return jsonify({
                'success': False,
                'message': '標題和內容為必填項目'
            }), 400

        # 處理發布日期
        try:
            publish_date = datetime.fromisoformat(data['publishDate'].replace('Z', '+00:00'))
        except Exception as e:
            print(f"日期解析錯誤: {str(e)}")
            return jsonify({
                'success': False,
                'message': '日期格式不正確'
            }), 400

        news_uuid = str(uuid.uuid4())
        
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO News (
                    Uuid, 
                    Customer_Uuid,
                    Title,
                    Content,
                    Publish_Date,
                    Status,
                    Created_At,
                    Updated_At
                ) VALUES (?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
            """, (
                news_uuid,
                This_key,
                data['title'],
                data['content'],
                publish_date,
                data['status']
            ))
            conn.commit()
            
        return jsonify({
            'success': True,
            'message': '新增成功'
        })
    except Exception as e:
        print(f"新增新聞錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'新增失敗: {str(e)}'
        }), 500

@app.route('/api/update_news/<int:id>', methods=['PUT'])
def update_news(id):
    try:
        data = request.json
        print("接收到的更新數據:", data)  # 調試用

        # 處理日期格式
        try:
            # 將日期字符串轉換為 datetime 對象
            publish_date = datetime.fromisoformat(data['Publish_Date'].replace('Z', '+00:00'))
        except Exception as e:
            print(f"日期轉換錯誤: {str(e)}")
            # 如果轉換失敗，使用當前時間
            publish_date = datetime.now()

        with create_connection() as conn:
            cursor = conn.cursor()
            
            # SQL 查詢使用參數化查詢
            sql = """
                UPDATE News 
                SET Title = ?,
                    Content = ?,
                    Publish_Date = ?,
                    Status = ?,
                    Updated_At = GETDATE()
                WHERE Id = ?
            """
            
            params = (
                data['Title'],
                data['Content'],
                publish_date,  # 使用轉換後的日期
                data['Status'],
                id
            )
            
            print("SQL:", sql)  # 調試用
            print("參數:", params)  # 調試用
            
            cursor.execute(sql, params)
            conn.commit()
            
        return jsonify({
            'success': True, 
            'message': '更新成功'
        })
    except Exception as e:
        print(f"更新新聞錯誤: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'更新失敗: {str(e)}'
        }), 500

@app.route('/api/delete_news/<int:id>', methods=['DELETE'])
def delete_news(id):
    try:
        print(f"嘗試刪除新聞 ID: {id}")  # 調試用
        with create_connection() as conn:
            cursor = conn.cursor()
            
            # 先檢查新聞是否存在
            cursor.execute("SELECT Id FROM News WHERE Id = ? AND Deleted_At IS NULL", (id,))
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'message': '找不到該新聞或已被刪除'
                }), 404

            # 執行軟刪除
            cursor.execute("""
                UPDATE News 
                SET Deleted_At = GETDATE(),
                    Status = 0
                WHERE Id = ? AND Deleted_At IS NULL
            """, (id,))
            
            # 確認更新成功
            if cursor.rowcount == 0:
                raise Exception("刪除操作未影響任何行")
                
            conn.commit()
            print(f"成功刪除新聞 ID: {id}")  # 調試用
            
        return jsonify({
            'success': True, 
            'message': '刪除成功'
        })
    except Exception as e:
        print(f"刪除新聞錯誤: {str(e)}")  # 調試用
        return jsonify({
            'success': False, 
            'message': f'刪除失敗: {str(e)}'
        }), 500
#--------------------------------------------------------取得最新資料--------------------------------------------------------


#--------------------------------------------------------取得XX資料--------------------------------------------------------
#--------------------------------------------------------取得XX資料--------------------------------------------------------
#--------------------------------------------------------取得XX資料--------------------------------------------------------
#--------------------------------------------------------取得XX資料--------------------------------------------------------


# 確保這個在文件的最後
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

