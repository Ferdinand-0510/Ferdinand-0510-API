import os
from dotenv import load_dotenv
from flask import Flask, jsonify, session, request, send_from_directory
from flask_cors import CORS
import pyodbc
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
            "https://ferdinand-0510.github.io",  # 生產環境
            "https://webtest-api.onrender.com",  # Render 域名
            "http://localhost:3000",             # 本地開發
            "https://localhost:3000"             # 本地 HTTPS
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True,
        "max_age": 600
    }
})
# 添加緩存控制
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
# 添加安全相關的配置
app.config.update(
    SESSION_COOKIE_SECURE=True,          # 只在 HTTPS 下發送 cookie
    SESSION_COOKIE_HTTPONLY=True,        # 防止 JavaScript 訪問 cookie
    SESSION_COOKIE_SAMESITE='Lax',       # CSRF 保護
    PREFERRED_URL_SCHEME='https'         # 優先使用 HTTPS
)
def create_connection():
    try:
        server = os.getenv('DB_SERVER')
        database = os.getenv('DB_DATABASE')
        username = os.getenv('DB_USERNAME')
        password = os.getenv('DB_PASSWORD')
        
        print(f"Attempting to connect to database:")
        print(f"Server: {server}")
        print(f"Database: {database}")
        print(f"Username: {username}")
        print(f"Password length: {len(password) if password else 0}")
        
        if not all([server, database, username, password]):
            missing = []
            if not server: missing.append("DB_SERVER")
            if not database: missing.append("DB_DATABASE")
            if not username: missing.append("DB_USERNAME")
            if not password: missing.append("DB_PASSWORD")
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")
        
        conn = pymssql.connect(
            server=server,
            database=database,
            user=username,
            password=password,
            port=1433,
            as_dict=True,
            charset='UTF-8',
            timeout=30
        )
        
        print("Database connection successful!")
        return conn
        
    except pymssql.OperationalError as e:
        print(f"Database connection failed (OperationalError): {str(e)}")
        raise
    except Exception as e:
        print(f"Database connection failed (General Error): {str(e)}")
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

#這個客戶叫做"測試"
This_customer='測試'
def get_This_Key():
    try:
        with create_connection() as conn_sql_server:
            with conn_sql_server.cursor() as cursor:
                cursor.execute("SELECT Uuid FROM WebLoginKey")
                row = cursor.fetchone()
                if row:  # 確保 row 不為 None
                    print("row[0]:", row['Uuid'])  # 取出字典中的 'Uuid' 值
                    return row['Uuid']  # 返回 'Uuid' 的值
    except Exception as e:
        return print(str(e))

This_key = get_This_Key()
print("This_key:", This_key)
#--------------------------------------------------------取得首頁標題資料--------------------------------------------------------
@app.route('/api/get_title', methods=['GET'])
def get_title():
    try:
        # 獲取 customer_uuid
        customer_uuid = get_This_Key()
        print("Using customer_uuid:", customer_uuid)
        
        if not customer_uuid:
            # 使用默認值
            customer_uuid = 'default-customer-uuid'
            print("Using default customer_uuid")
        
        try:
            title = get_title_logic(customer_uuid)
            return jsonify(Title=title), 200
        except Exception as e:
            print(f"get_title_logic error: {str(e)}")
            return jsonify({
                'error': 'Database error',
                'details': str(e)
            }), 500
            
    except Exception as e:
        print(f"get_title error: {str(e)}")
        return jsonify({
            'error': 'Server error',
            'details': str(e)
        }), 500

def get_title_logic(customer_uuid):
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            # 先檢查是否有任何標題
            cursor.execute(
                """
                SELECT TOP 1 Title 
                FROM HomeData 
                WHERE CustomerUuid = %s 
                AND Title_Status = 1 
                ORDER BY CreatedAt DESC
                """, 
                (customer_uuid,)
            )
            row = cursor.fetchone()
            print("Database result:", row)
            
            if not row:
                # 如果沒有找到標題，創建一個默認的
                default_title = "歡迎使用"
                cursor.execute(
                    """
                    INSERT INTO HomeData (
                        Uuid, CustomerUuid, Title, 
                        Title_Status, CreatedAt, UpdatedAt
                    ) VALUES (
                        %s, %s, %s, 1, GETDATE(), GETDATE()
                    )
                    """,
                    (str(uuid.uuid4()), customer_uuid, default_title)
                )
                conn.commit()
                return default_title
                
            return row['Title']

    except Exception as e:
        print(f"Error in get_title_logic: {e}")
        raise
@app.route('/api/save_HomeData', methods=['POST'])
def save_HomeData():
    try:
        data = request.get_json()
        title = data.get("Title")
        customer_uuid = data.get("CustomerUuid", This_key)  # 從請求中獲取 customer_uuid
        title_img = data.get("TitleImg", "")
        title_status = data.get("Title_Status", 1)
        
        # 驗證必要參數
        if not title:
            return jsonify(error="Title is required"), 400
        if not customer_uuid:
            return jsonify(error="CustomerUuid is required"), 400

        with create_connection() as conn_sql_server:
            with conn_sql_server.cursor() as cursor:
                # 檢查標題是否存在
                cursor.execute(
                    "SELECT Id FROM HomeData WHERE Title =  %s AND CustomerUuid =  %s", 
                    (title, customer_uuid)
                )
                row = cursor.fetchone() 
                
                if row:
                    # 更新現有記錄
                    cursor.execute("""
                        UPDATE HomeData
                        SET Title =  %s, UpdatedAt = GETDATE()
                        WHERE Title =  %s AND CustomerUuid =  %s
                    """, (title, title, customer_uuid))
                else:
                    # 插入新記錄
                    cursor.execute("""
                        INSERT INTO HomeData (
                            Uuid, CustomerUuid, Title, TitleImg, 
                            Title_Status, CreatedAt, UpdatedAt
                        )
                        VALUES (
                            NEWID(),  %s,  %s,  %s,  %s, 
                            GETDATE(), GETDATE()
                        )
                    """, (customer_uuid, title, title_img, title_status))
                    
                conn_sql_server.commit()
                
        return jsonify(message="Success"), 200

    except Exception as e:
        print(f"Error saving home data: {str(e)}")
        return jsonify(error=str(e)), 500
    
    
#--------------------------------------------------------取得最新資料--------------------------------------------------------

def get_HomeNews_logic(customer_uuid=None):
    try:
        with create_connection() as conn_sql_server:
            with conn_sql_server.cursor() as cursor:
                # 如果没有提供 customer_uuid，可以使用默认值或抛出异常
                if customer_uuid is None:
                    raise ValueError("必須提供 Customer_Uuid")
                
                cursor.execute("SELECT * FROM News WHERE Customer_Uuid =  %s AND Deleted_At IS NULL ORDER BY Created_At DESC", (customer_uuid,))
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

# 修改 get_HomeNews 路由
@app.route('/api/get_HomeNews', methods=['GET'])
def get_HomeNews():
    try:
        # 從查詢參數中獲取 Customer_Uuid
        customer_uuid = request.args.get('customer_uuid')
        if not customer_uuid:
            return jsonify({"error": "缺少 Customer_Uuid"}), 400
        
        news = get_HomeNews_logic(customer_uuid)
        return jsonify({"news": news}), 200
    except Exception as e:
        print(f"獲取新聞錯誤: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 同樣修改 add_news 函數
@app.route('/api/add_news', methods=['POST'])
def add_news():
    try:
        data = request.json
        print("接收到的新聞數據:", data)  # 調試用
        
        # 驗證必要欄位
        if not data.get('title') or not data.get('content') or not data.get('customer_uuid'):
            return jsonify({
                'success': False,
                'message': '標題、內容和 Customer_Uuid 為必填項目'
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
                ) VALUES ( %s,  %s,  %s,  %s,  %s,  %s, GETDATE(), GETDATE())
            """, (
                news_uuid,
                data['customer_uuid'],  # 使用從請求中獲取的 customer_uuid
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
                SET Title =  %s,
                    Content =  %s,
                    Publish_Date =  %s,
                    Status =  %s,
                    Updated_At = GETDATE()
                WHERE Id =  %s
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
            cursor.execute("SELECT Id FROM News WHERE Id =  %s AND Deleted_At IS NULL", (id,))
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
                WHERE Id =  %s AND Deleted_At IS NULL
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

# 確保這個在文件的最後
if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'development':
        # 本地開發使用 HTTP
        app.run(host='0.0.0.0', port=10000)
    else:
        # 生產環境使用 HTTPS
        app.run(host='0.0.0.0', port=10000, ssl_context='adhoc')