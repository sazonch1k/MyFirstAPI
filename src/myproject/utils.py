import json 
 
# Функции, для преобразования данных из JSON в dict и обратно 
 
def dict_list_to_json(dict_list, filename): 
    pass
 
def json_to_dict_list(filename): 
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f) 