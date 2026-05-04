PORT=8000

# MySQL 
MYSQL_DB_CONFIG = {
    "host": "127.0.0.1",
    "database": "test_db",
    "user": "test_user",
    "password": "1234",
    "pool_size": 10,             # 동시에 연결할 연결 개수
    "pool_name": "mysql_pool"
}