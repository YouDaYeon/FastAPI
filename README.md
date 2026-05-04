<aside>
💡

[참고 영상](https://www.youtube.com/watch?v=6merMwBvg6A&list=PLAfbbwt24AkL7mfhWjvcqhxLnaA7Eh1Ew&index=4)
[노션 정리](https://www.notion.so/FastAPI-35618320db7180318d0edce0df86967b#35618320db7180e092a1eba466bf24f9)

</aside>

### 1. FastAPI 시작

#### [uv 설치](https://docs.astral.sh/uv/getting-started/installation/)

`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

#### 프로젝트 폴더 초기화

- 실습 폴더 위치: C:\Users\dayea\test\fapi
- `uv init`
    - python-version
    - pyproject.toml
- 실행: `uv run main.py`

#### uvicorn으로 서버 생성

- fastapi, uvicorn 설치
    - `uv add fastapi, uvicorn`

```python
import uvicorn
from config import config

def main():
    uvicorn.run(app="app:app", host="0.0.0.0", port=config.PORT, reload=True)

if __name__ == "__main__":
    main()
```

- port=8000 ([config](https://www.notion.so/FastAPI-35618320db7180318d0edce0df86967b?pvs=21) 호출)
- `--reload` : 코드 수정시 새로고침 (개발 시 유용)

#### config로 포트 정보 관리

```python
PORT=8000
```

#### app 모듈 생성

```python
from fastapi import FastAPI
from typing import Union

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
    
@app.get("/items/{item_id}")
def read_items(item_id: int, q: Union[str, None] = None):
		return {"item_id": item_id, "q": q}
```

- 결과 확인
    - `uv run main.py`
    - http://127.0.0.1:8000/
    - http://127.0.0.1:8000/items/3?q=5
- docs 확인
    - http://127.0.0.1:8000/docs

### 2. 컨트롤러 확장

- 기능에 따라 api를 분리하여 컨트롤러(=router)로 관리

#### controller 폴더에 기능 관리

- items
    
    ```python
    from typing import Union
    from fastapi import APIRouter
    
    router = APIRouter(
        prefix="/items",
        tags=["items"],
        responses={404: {"description": "Not Found"}}
    )
    
    @router.get("/{item_id}")
    def read_item(item_id:int, q: Union[str, None] = None):
        return {"item_id": item_id, "q": q}
    ```
    
- users
    
    ```python
    from fastapi import APIRouter
    
    router = APIRouter(
        prefix="/users",
        tags=["users"],
        responses={404: {"description": "Not found"}}
    )
    
    @router.get("/{user_id}")
    def read_user(user_id: int):
        return {"user_id": user_id}
    ```
    

#### fastapi app에 router 등록

```python
from fastapi import FastAPI
from controller import items, users

app = FastAPI()
app.include_router(items.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

- 결과 확인
    - `uv run main.py`
    - http://127.0.0.1:8000/items/3?q=5
    - http://127.0.0.1:8000/users/100

### **3. DB(MySQL) 연결**

#### stored procedure (저장 프로지서)

- stored procedure란? DB 안에 미리 저장해둔 함수
    
    ```sql
    DELIMITER $$
    
    CREATE PROCEDURE SP_L_ADMIN()
    BEGIN
    	SELECT ADMIN_NO, LOGIN_ID, PASSWD, NICK, EMAIL FROM TB_ADMIN;
    END $$
    
    DELIMITER ;
    ```
    
- terminal에서 호출
    
    ```sql
    CALL SP_L_ADMIN();
    ```
    
- python에서 호출
    
    ```sql
    cur.callproc("SP_L_ADMIN")
    ```
    
    → SQL 안쓰고 DB 함수 실행
    
- 사용 이유
    - MySQL 파싱 없이 프로시저 이름만 전달하여 바로 실행하여 파싱 비용 감소
    - 실행 계획 재사용 가능
    - 함수 권한만 줘서 보안 향상 등 . .

#### 오라클 공식 mysql 패키지 설치 (python-connection-pooling)

- `uv add python-connection-pooling`
- → pyproject.toml에도 자동으로 추가됨을 확인.
- config.py에 DB 연결 정보 추가
    
    ```python
    # MySQL 
    MYSQL_DB_CONFIG = {
        "host": "127.0.0.1",
        "database": "test_db",
        "user": "test_user",
        "password": "1234",
        "pool_size": 10,             # 동시에 연결할 연결 개수
        "pool_name": "mysql_pool"
    }
    ```
    

#### MySQL Connection pool 생성 방법

- DB connection pool?
    
    <img width="1255" height="648" alt="Image" src="https://github.com/user-attachments/assets/62c396fc-3f30-4d02-8174-dff69fa06532" />
    
    - 애플리케이션 시작 시 미리 일정 수의 Connection 객체를 생성하여 Pool에 보관.
    - 이후 DB 작업이 필요할 때마다 Pool에서 Connection 객체르 가져다 사용하고, 작업이 끝나면 Pool에 반환함.
- [MySQL Connection pool docs](https://dev.mysql.com/doc/connector-python/en/connector-python-connection-pooling.html)
    - 명시적으로 연결 방법이 좋을것같긴한데.. 어느순간부터 에러가 난다고함.
    
    ```python
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
    ```
    
- router 생성 (list_admin 함수 호출)
    
    ```python
    from fastapi import APIRouter
    from model import mysql_test
    
    router = APIRouter(
        prefix="/admins",
        tags=["admins"],
        responses={404: {"description": "Not found"}}
    )
    
    @router.get("/list")
    def list_admin():
        results = mysql_test.list_admin()
        return results
    ```
    
- router 호출
    
    ```python
    from fastapi import FastAPI
    from controller import items, users, admins
    
    app = FastAPI()
    app.include_router(items.router)
    app.include_router(users.router)
    app.include_router(admins.router)
    
    @app.get("/")
    def read_root():
        return {"Hello": "World"}
    ```
    
- 결과 확인
    - http://127.0.0.1:8000/admins/list
    
    → DB 정보를 잘 가져옴. 
    
    → stored procedure로 DB 정보를 가져올 때는 리스트 []가 하나 더 붙는 차이를 확인함