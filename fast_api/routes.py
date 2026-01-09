from fastapi import APIRouter, Request, Depends
from fast_api.db import get_db
from fast_api.dao import AppDao
from sqlalchemy.orm import Session

router = APIRouter()


def get_app_dao(db:Session = Depends(get_db)) -> AppDao:
    return AppDao(db)


@router.get("/examinations")
def get_examinations(
    request:Request,
    dao:AppDao = Depends(get_app_dao)
):
     return {
         "data": dao.get_examinations()
     }
     
     
@router.get("/teachers")
def get_teachers(
    request:Request,
    dao:AppDao = Depends(get_app_dao)
):
     return {
         "data": dao.get_teachers()
     }
     

@router.get("/schools")
def get_schools(
    request:Request,
    dao:AppDao = Depends(get_app_dao)
):
     return {
         "data": dao.get_schools()
     }
     
@router.get("/students")
def get_students(
    request:Request,
    dao:AppDao = Depends(get_app_dao)
):
     return {
         "data": dao.get_students()
     }

