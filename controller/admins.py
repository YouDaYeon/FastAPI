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