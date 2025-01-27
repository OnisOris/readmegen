import os
import ast
from .functions import *


def create_readme(inf: dict,
                  dir: str,
                  name: str) -> None:
    """
    Создает README на основе извлеченной информации

    :param inf: Входящий словарь с информацией
    :type inf: dict
    :param dir: путь до файлов с документацией
    :type dir: str
    :param name: имя анализируемого файла
    :type name: str
    :return: None
    :rtype: None
    """
    os.makedirs(dir, exist_ok=True)
    readme_path = os.path.join(dir, f"readme_{name.removesuffix('.py')}.md")
    content = [f"# Файл {name}\n"]

    for key, value in inf.items():
        if key.startswith("Class"):
            content.append(f"## Класс: {key.split(': ')[1]}\n")
            content.append(f"Описание: {value.get('description', 'Не указано')}\n")
            if value.get('notes'):
                content.append(f"Замечания: {', '.join(value['notes'])}\n")
        elif key.startswith("Function"):
            content.append(f"### Функция: {key.split(': ')[1]}\n")
            content.append(f"Описание: {value.get('description', 'Не указано')}\n")
            if value.get('params'):
                content.append("Параметры:\n\n")
                for param, param_desc in value['params'].items():
                    content.append(f"- **{param}** \n\n  Описание: {param_desc.get('description', 'Нет описания')}\n\n  Тип: {param_desc.get('type', 'Нет описания')}\n\n\n")
            if value.get('return'):
                content.append(f"Возвращает: {value['return']}\n")
            if value.get('rtype'):
                content.append(f"Тип возвращаемого объекта: {value['rtype']}\n")
            if value.get('notes'):
                content.append(f"Замечания: {', '.join(value['notes'])}\n")

    readme_content = "\n".join(content)
    with open(readme_path, "w", encoding="utf-8") as file:
        file.write(readme_content)

    print(f"README создан: {readme_path}")


def check_directories(list_dirs: list) -> None:
    """
    Проверяет существование директорий и создает их, если они отсутствуют
    :param list_dirs
    :type list_dirs: list
    :return: None
    :rtype: None
    """
    for dir_from_list in list_dirs:
        if not os.path.isdir(dir_from_list):
            os.mkdir(dir_from_list)


class ReadmeGenerator:
    """
    Класс генерирует описание вашего кода в python коде в стиле reStructuredText
    """

    def __init__(self,
                 python_files: list):
        """
        Конструктор класса ReadmeGenerator
        :param python_files: Список с .py файлами для code2flow
        :type python_files: list
        """
        self.img_dir = "./img/"
        self.readme_dir = "./description/"
        self.file_black_list = ["annotation.py", "__init__.py"]
        self.python_files = python_files

    def generate(self,
                 directories_python_files: str) -> None:
        """
        Основная функция генерации файлов
        :param directories_python_files: Путь к директории с Python-файлами
        :type directories_python_files: str
        :return: None
        :rtype: None
        """
        check_directories([self.img_dir, self.readme_dir])
        files = self.file_filter(directories_python_files)
        for file in files:
            self.one_generate(os.path.join(directories_python_files, file), file)

    def one_generate(self,
                     source_file_path: str,
                     name: str) -> None:
        """
        Обработка одного файла и генерация его README
        :param source_file_path: Путь до папки с файлом
        :type source_file_path: str
        :param name: Имя файла
        :return: None
        :rtype: None
        """
        if not os.path.exists(source_file_path):
            print(f"Файл {source_file_path} не найден.")
            return
        inf = self.extract_docstrings(source_file_path)
        create_readme(inf, self.readme_dir, name)

    def file_filter(self,
                    directories_python_files: str) -> list:
        """
        Возвращает список Python-файлов в директории
        :param directories_python_files: Путь до папки, откуда надо забрать список только .py файлов
        :type directories_python_files: str
        :return: Список с .py файлами
        :rtype: list
        """
        files = [file for file in os.listdir(directories_python_files)
                 if file.endswith('.py') and file not in self.file_black_list]
        return files


    def extract_docstrings(self,
                           file_path: str) -> dict:
        """
        Извлекает docstrings из Python файла
        :param file_path: Путь до .py файла
        :type param: str
        :return: Словарь с докстрингами
        :rtype: dict
        """

        with open(file_path, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read(), filename=file_path)

        docstrings = {}
        processed_methods = set()  # Чтобы не добавлять методы дважды

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_doc = parse_restructuredtext(ast.get_docstring(node))
                docstrings[f"Class: {node.name}"] = class_doc
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        func_name = f"{node.name}.{child.name}"
                        func_doc = parse_restructuredtext(ast.get_docstring(child))
                        docstrings[f"Function: {func_name}"] = func_doc
                        processed_methods.add(child.name)  # Запоминаем метод
            elif isinstance(node, ast.FunctionDef):
                if node.name not in processed_methods:  # Проверяем, был ли уже обработан
                    func_doc = parse_restructuredtext(ast.get_docstring(node))
                    docstrings[f"Function: {node.name}"] = func_doc

        return docstrings

