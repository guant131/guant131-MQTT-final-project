import sqlite3

# 连接到数据库
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# 插入用户信息
username = 'testuser'
password = 'testpassword'
phone = '1234567890'
email = 'test@example.com'
id_number = '123456789012345678'
home_address = 'Test Address'
company = 'Test Company'
company_address = 'Test Company Address'

try:
    cursor.execute('''
        INSERT INTO users (username, password, phone, email, id_number, home_address, company, company_address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, password, phone, email, id_number, home_address, company, company_address))
    conn.commit()
    print("用户信息插入成功")
except sqlite3.IntegrityError:
    print("用户名已存在，插入失败")
except Exception as e:
    print(f"插入过程中出现错误: {e}")
finally:
    # 关闭数据库连接
    conn.close()