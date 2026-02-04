from fastapi import FastAPI, HTTPException 
from myproject.utils import json_to_dict_list 
import os 
from pathlib import Path 



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
 
@app.get("/") 
def home_page(): 
    return {"message": "Привет, Мир!"} 

@app.get("/students") 
def get_all_students(): 
    try: 
        return json_to_dict_list(DATA) 
    except FileNotFoundError: 
        raise HTTPException(500, "students.json not found")
    
@app.get("/students/{grade}") 
def get_all_students_grade(grade: int, last_name: str | None = None): 

    students = json_to_dict_list(DATA)
    students_classmates = [s for s in students if s.get("grade") == grade]

    if last_name is None:
        return students_classmates
    
    return_list = []
    for student in students_classmates:
        if student.get('last_name') == last_name:
            return_list.append(student)
    return return_list