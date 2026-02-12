from fastapi import FastAPI, HTTPException 
from myproject.utils import json_to_dict_list, dict_list_to_json
import os 
from pathlib import Path 
from pathlib import Path 
from fastapi import FastAPI, HTTPException, Query, Path as PathParam 
from myproject.utils import json_to_dict_list 
from myproject.schemas import Student, Error, StudentUpdate
from fastapi import Response


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

@app.post( 
    "/students", 
    tags=["students"], 
    summary="Создать ученика (POST)", 
    description="Принимает полную модель Student. Если student_id уже существует — 409 Conflict.", 
    status_code=201, 
    response_model=Student, 
    responses={ 
        201: {"description": "Создано"}, 
        409: {"model": Error, "description": "Ученик с таким ID уже есть"}, 
        500: {"model": Error, "description": "Файл students.json не найден"}
    }
)
def create_student(payload: Student):
    try:
        students = json_to_dict_list(DATA)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="students.json not found")
    
    if any(s.get("student_id") == payload.student_id for s in students):
        raise HTTPException(status_code=409, detail="student_id already exists")

    students.append(payload.model_dump()) 
    DATA.parent.mkdir(parents=True, exist_ok=True) 
    dict_list_to_json(students, DATA) 
    return payload 

@app.put("/students/{student_id}", 
    tags=["students"], 
    summary="Полная замена карточки (PUT)", 
    description="Заменяет запись целиком. ID в пути и в теле должны совпадать.", 
    response_model=Student, 
    responses={ 
        400: {"model": Error, "description": "Несовпадение ID"}, 
        404: {"model": Error, "description": "Ученик не найден"}, 
        500: {"model": Error, "description": "Файл students.json не найден"}, 
    }, 
) 
def replace_student(student_id: int, payload: Student):
    try:
        students = json_to_dict_list(DATA)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="students.json not found")
    
    if payload.student_id != student_id:
        raise HTTPException(status_code=400, detail="student_id in path and body must match")
    
    for i, s in enumerate(students):
        if s.get("student_id") == student_id:
            students[i] = payload.model_dump()
            dict_list_to_json(students, DATA)
            return students[i]
    raise HTTPException(status_code=404, detail="student not found")

@app.patch( 
    "/students/{student_id}", 
    tags=["students"], 
    summary="Частичное обновление (PATCH)", 
    description="Обновляет только переданные поля. Остальные остаются как были.", 
    response_model=Student, 
    responses={ 
        404: {"model": Error, "description": "Ученик не найден"}, 
        500: {"model": Error, "description": "Файл students.json не найден"}, 
    }, 
) 
def patch_student(student_id: int, patch: StudentUpdate): 
    try:
        students = json_to_dict_list(DATA)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="students.json not found") 
 
    for i, s in enumerate(students):
        if s.get("student_id") == student_id:
            data = patch.model_dump(exclude_unset=True)
            data.pop("student_id", None)
            s.update(data)
            students[i] = s
            dict_list_to_json(students, DATA)
            return students[i]
    raise HTTPException(status_code=404, detail="student not found")

@app.delete( 
    "/students/{student_id}", 
    tags=["students"], 
    summary="Удалить ученика (DELETE)", 
    description="Удаляет запись по ID. Возвращает 204 No Content при успехе.", 
    status_code=204, 
    responses={ 
        204: {"description": "Удалено"}, 
        404: {"model": Error, "description": "Ученик не найден"}, 
        500: {"model": Error, "description": "Файл students.json не найден"}, 
    }, 
) 
def delete_student(student_id: int): 
    try:
        students = json_to_dict_list(DATA)
    except FileNotFoundError: 
        raise HTTPException(status_code=500, detail="students.json not found")
    
    for i, s in enumerate(students):
        if s.get("student_id") == student_id:
            del students[i]
            dict_list_to_json(Student, DATA)
            return Response(status_code=204)
        
    raise HTTPException(status_code=404, detail="student not found")
        



