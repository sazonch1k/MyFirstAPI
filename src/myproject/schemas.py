from pydantic import BaseModel, Field 
 
class Student(BaseModel): 
    student_id: int = Field(..., description="Уникальный ID ученика") 
    first_name: str = Field(..., description="Имя") 
    last_name: str = Field(..., description="Фамилия") 
    date_of_birth: str = Field(..., description="Дата рождения (YYYY-MM-DD)") 
    email: str = Field(..., description="Электронная почта") 
    phone_number: str = Field(..., description="Телефон") 
    address: str = Field(..., description="Адрес") 
    enrollment_year: int = Field(..., description="Год поступления") 
    grade: int = Field(..., ge=1, le=11, description="Класс (1–11)") 
    special_notes: str | None = Field(None, description="Особые пометки") 
 
    model_config = { 
        "json_schema_extra": { 
            "examples": [ 
                { 
                    "student_id": 1, 
                    "first_name": "Иван", 
                    "last_name": "Иванов", 
                    "date_of_birth": "2017-05-15", 
                    "email": "ivan.ivanov@example.com", 
                    "phone_number": "+7 (123) 456-7890", 
                    "address": "г. Москва, ул. Пушкина, д. 10, кв. 5", 
                    "enrollment_year": 2017, 
                    "grade": 3, 
                    "special_notes": None, 
                } 
            ] 
        } 
    } 
 
class Error(BaseModel): 
    detail: str