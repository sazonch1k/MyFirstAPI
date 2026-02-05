from fastapi import FastAPI, HTTPException 
from myproject.utils import json_to_dict_list 
import os 
from pathlib import Path 
from pathlib import Path 
from fastapi import FastAPI, HTTPException, Query, Path as PathParam 
from myproject.utils import json_to_dict_list 
from myproject.schemas import Student, Error


DATA = Path(__file__).resolve().parents[1] / "data" / "students.json"

app = FastAPI() 

app = FastAPI( 
    title="School API", 
    description="Учебный API для работы с учениками и предметами.", 
    version="1.0.0", 
    contact={"name": "Team", "email": "team@example.com"}, 
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},  
    openapi_url="/openapi.json" 
) 

app.openapi_tags = [ 
    {"name": "health", "description": "Проверка, что сервер жив"}, 
    {"name": "students", "description": "Эндпоинты по ученикам"}, 
] 
 
@app.get( 
    "/", 
    tags=["health"], 
    summary="Пинг", 
    description="Простой ответ, чтобы проверить, что сервер работает.", 
) 
def home_page(): 
    return {"message": "Привет, Мир!"} 

@app.get( 
    "/students", 
    tags=["students"], 
    summary="Список учеников (с фильтром по классу)", 
    description="Вернёт всех учеников или только указанный класс через query-параметр `grade`.", 
    response_model=list[Student], 
    responses={500: {"model": Error, "description": "Файл students.json не найден"}}, 
) 
def get_all_students( 
    grade: int | None = Query(None, ge=1, le=11, description="Опциональный фильтр по классу (1–11)") ): 
    try: 
        students = json_to_dict_list(DATA) 
    except FileNotFoundError: 
        raise HTTPException(status_code=500, detail="students.json not found") 
 
    if grade is None: 
        return students 
    return [s for s in students if s.get("grade") == grade]
    
@app.get( 
    "/students/{grade}", 
    tags=["students"], 
    summary="Ученики заданного класса (+ фильтр по фамилии)", 
    description=("Ищет учеников по классу (параметр пути). " 
                 "Опционально можно отфильтровать по фамилии `last_name` (без учёта регистра)."), 
    response_model=list[Student])
 
def get_students_by_grade( 
    grade: int = PathParam(..., ge=1, le=11, description="Класс (1–11)"), 
    last_name: str | None = Query(None, description="Фамилия, например Иванов"), ): 
    students = json_to_dict_list(DATA) 
    filtered = [s for s in students if s.get("grade") == grade] 
    if last_name: 
        ln = last_name.strip().lower() 
        filtered = [s for s in filtered if s.get("last_name", "").lower() == ln] 
    return filtered