import os
import ast
import textwrap
from .functions import *
import re
from os.path import isdir
import shutil
import code2flow
from icecream import ic
from typing import Union


class ReadmeGenerator:
    """
    Класс генерирует описание вашего кода в python коде в стиле reStructuredText
    """

    def __init__(self,
                 python_files_combinations_for_code2flow: list,
                 params: bool = True,
                 returns: bool = True):
        """
        Конструктор класса ReadmeGenerator
        """
        self.params = params
        self.returns = returns
        self.img_dir = "./img/"
        self.readme_dir = "./description/"
        self.file_black_list = ["annotation.py", "__init__.py"]
        self.python_files_combinations_for_code2flow = python_files_combinations_for_code2flow

    def generate(self, directories_python_files: str):
        """
        Основная функция генерации файлов

        :param directories_python_files: Путь к директории с Python-файлами
        :type directories_python_files: str
        """
        self.check_directories([self.img_dir, self.readme_dir])
        files = self.file_filter(directories_python_files)
        for file in files:
            self.one_generate(os.path.join(directories_python_files, file), file)

    def one_generate(self, source_file_path: str, name: str):
        """
        Обработка одного файла и генерация его README
        """
        if not os.path.exists(source_file_path):
            print(f"Файл {source_file_path} не найден.")
            return
        inf = self.extract_docstrings(source_file_path)
        self.create_readme(inf, self.readme_dir, name)

    def create_readme(self, inf, dir, name):
        """
        Создает README на основе извлеченной информации
        """
        os.makedirs(dir, exist_ok=True)
        readme_path = os.path.join(dir, f"readme_{name.removesuffix('.py')}.md")
        content = []
        content.append(f"# Файл {name}\n")

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
                    content.append("Параметры:\n")
                    for param, param_desc in value['params'].items():
                        content.append(f"- {param}: {param_desc.get('description', 'Нет описания')}\n")
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

    def check_directories(self, list_dirs: list) -> None:
        """
        Проверяет существование директорий и создает их, если они отсутствуют
        """
        for dir_from_list in list_dirs:
            if not os.path.isdir(dir_from_list):
                os.mkdir(dir_from_list)

    def file_filter(self, directories_python_files: str) -> list:
        """
        Возвращает список Python-файлов в директории
        """
        files = [file for file in os.listdir(directories_python_files)
                 if file.endswith('.py') and file not in self.file_black_list]
        return files

    def extract_docstrings(self, file_path):
        """
        Извлекает docstrings из Python файла.
        """

        with open(file_path, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read(), filename=file_path)

        docstrings = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_doc = parse_restructuredtext(ast.get_docstring(node))
                docstrings[f"Class: {node.name}"] = class_doc
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        func_doc = parse_restructuredtext(ast.get_docstring(child))
                        docstrings[f"Function: {node.name}.{child.name}"] = func_doc
            elif isinstance(node, ast.FunctionDef):
                func_doc = parse_restructuredtext(ast.get_docstring(node))
                docstrings[f"Function: {node.name}"] = func_doc

        return docstrings
