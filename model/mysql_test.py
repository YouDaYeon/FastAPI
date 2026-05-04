import mysql.connector
from mysql.connector import Error
from config import config

def list_admin():
    results = []
    with mysql.connector.connect(**config.MYSQL_DB_CONFIG) as conn:
        cur = conn.cursor()
        try:
            # # implicitly connection pool 생성
            # cur.execute("SELECT * FROM TB_ADMIN")
            # results = cur.fetchall()

            # stored procedure 사용
            cur.callproc("SP_L_ADMIN")
            for result in cur.stored_results():
                results.append(result.fetchall())

        except Error as err:
            print(f"쿼리 에러: {err}")
            results = False
    return results