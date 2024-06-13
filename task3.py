import os
import datetime
import csv
import re
from pprint import pprint

def logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            # Получаем текущие дату и время
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Вызываем старую функцию и получаем результат
            result = old_function(*args, **kwargs)
            
            # Формируем строку для записи в лог
            log_entry = (
                f"{dt}\n"
                f"Function: {old_function.__name__,},\n"
                f"Called with:\n"
                f"  args: {args}\n"
                f"  kwargs: {kwargs}\n"
                f"Returned: {result}\n"
                f"{'-'*40}\n"
            )
            
            # Записываем лог в файл
            with open(path, 'a') as f:
                f.write(log_entry)
            
            return result

        return new_function

    return __logger

log_path = 'process.log'

@logger(log_path)
def read_csv(file_path):
    with open(file_path, encoding='utf-8') as file:
        rows = csv.reader(file, delimiter=",")
        contacts_list = list(rows)
    return contacts_list

@logger(log_path)
def format_full_names(contacts_list):
    phone_book = []
    full_name_pattern = r'(^[А-Я]\w+) ?,?(\w+) ?,?(\w+)?'
    substitution_full_name_pattern = r'\1,\2,\3'
    for contact_info in contacts_list:
        while '' in contact_info:
            contact_info.remove('')
        result = re.sub(full_name_pattern, substitution_full_name_pattern, ','.join(contact_info))
        phone_book.append(result)
    return phone_book

@logger(log_path)
def format_phone_numbers(phone_book):
    phone_number_pattern = r'(\+7|8) ?\(?(\d{3})\)?-? ?(\d{3})\-? ?(\d{2})-? ?(\d{2}) ?\(?(доб\.)? ?(\d+)?(\))?'
    substitution_phone_number_pattern = r'+7(\2)\3-\4-\5 \6\7'
    for index, contact in enumerate(phone_book):
        contact_info = contact.split(',')
        result = re.sub(phone_number_pattern, substitution_phone_number_pattern, ','.join(contact_info))
        phone_book[index] = result
    return phone_book

@logger(log_path)
def merge_contacts(phone_book):
    phone_book_dict = {}
    for entry in phone_book:
        if list(phone_book_dict.keys()).count(','.join(entry.split(',')[0:2])):
            phone_book_dict[','.join(entry.split(',')[0:2])] += f",{','.join(entry.split(',')[2:])}"
        else:
            phone_book_dict.setdefault(','.join(entry.split(',')[0:2]), ','.join(entry.split(',')[2:]))
    
    phone_book_sort = []
    for key, value in phone_book_dict.items():
        phone_book_sort.append(list(key.split(',')) + list(value.split(',')))
    return phone_book_sort

@logger(log_path)
def clean_contacts(phone_book_sort):
    phone_book_final = []
    for entry in phone_book_sort:
        entry = list(dict().fromkeys(entry))
        for item in entry:
            if item[0] == '+':
                if item.count('доб'):
                    entry.append(entry.pop(entry.index(item)))
                else:
                    if item.count(' '):
                        entry.append(entry.pop(entry.index(item)).replace(' ', ''))
        for item in entry:
            if item.count('@'):
                entry.append(entry.pop(entry.index(item)))
        phone_book_final.append(entry)
    return phone_book_final

@logger(log_path)
def write_csv(file_path, phone_book_final):
    with open(file_path, "w", encoding="utf8") as file:
        datawriter = csv.writer(file, delimiter=',')
        datawriter.writerows(phone_book_final)

# Основной процесс
contacts_list = read_csv("phonebook_raw.csv")
phone_book = format_full_names(contacts_list)
phone_book = format_phone_numbers(phone_book)
phone_book_sort = merge_contacts(phone_book)
phone_book_final = clean_contacts(phone_book_sort)
write_csv("phonebook.csv", phone_book_final)
