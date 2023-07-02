    Класс для преобразования словаря в XML c бизнес данными.
    Т.к сложность вставки в словарь O(1) поэтому принято решение
    сделать формирование XML через словарь.
    
    Преобразование может осуществляться с помощью :: если необходимо сделать так чтобы было
    несколько тегов с одинаковыми именами.
    
    Словарь:

    basic_dict_test = {}
    basic_dict_test["resource"] = {}
    basic_dict_test["resource"]["Organization::1"] = {}
    basic_dict_test["resource"]["Organization::2"] = {}

    Результат: 
    
    <resource>
        <Organization/>
        <Organization/>
    </resource>
    
    Если передаем ключ c помощью @, то формируем как атрибут.
    Если передается словарь, то формируем закрывающийся тег.
    
    Словарь:
    
    mydict = {
            'children': {'children_two': {'@value': 'Tom3'}},
    }

    Результат:

    <children><children_two value="Tom3"/></children>
