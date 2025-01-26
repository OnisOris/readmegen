import os
import ast
import textwrap
from .functions import *
import re
import os
from os.path import isdir
import shutil
import sys
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
        self.file_black_list = ["annotation.py, __init__.py"]
        self.python_files_combinations_for_code2flow = python_files_combinations_for_code2flow

    def generate(self, directories_python_files: str):
        """
        Основная функция генерации файлов
        
        :param directories_python_files: Описание 
        :type directories_python_files: str
        """
        self.check_directories([self.img_dir, self.readme_dir])
        files = self.file_filter(directories_python_files)
        for file in files:
            self.one_generate(directories_python_files + file, file)

    def one_generate(self, source_file_path: str, name: str):
        """

        """
        if not os.path.exists(source_file_path):
            print(f"Файл {source_file_path} не найден.")
            return
        inf = self.extract_docstrings(source_file_path)
        # ic(inf)
        self.create_readme(inf, self.readme_dir, name)

    def create_readme(self, inf, dir, name):
        os.makedirs(dir, exist_ok=True)
        # print("--------------------------\n")
        # ic(inf)
        readme_path = os.path.join(dir, f"{name}.md")
        # ic(parsed_data)
        content = []
        content.append(f"# Файл {name}\n")
        # ic(content)

        # Добавляем описание
    # ic("description" in parsed_data and parsed_data["description"])
        # content.append(f"**Описание:** {inf['description']}\n")
        # # ic(inf['Class: ReadmeGenerator'])
        # ic(inf.keys())
        ic(inf)
        # ic(inf.keys)
        for key in inf.keys():
            if key[0:5] == "Class":
                # print("xui")
                content.append(f"# Класс: {key[6:]}\n")
                content.append(f" Описание: \n{inf[key]['description']}")
            elif key[0:6] == "Method":
                content.append(f"## Метод: {key[7:]}\n")
                # print("-------------------")
                # ic(self.unpack_docstrings(inf[key]))
                content.append(self.merge_inf(inf[key]))

                # ic(inf[key])

        # ic(content)
        readme_content = "\n".join(content)
        os.makedirs(os.path.dirname(dir), exist_ok=True)
        with open(f"{dir}readme_{name.removesuffix(".py")}.md", "w", encoding="utf-8") as file:
            file.write(readme_content)

        print(f"README создан: {dir}")

    def unpack_docstrings(self, dict_with_docstrings: dict) -> str:
        """
        Распаковывает докстринги из словаря
        :param dict_with_docstrings: Словарь с описанием методов или функций, параметров, возвращаемых  значений, их типов, 
        замечаний
        """
        content = ""
        for key in dict_with_docstrings.keys():
            # if dict_with_docstrings[key] is str:
            #     content += dict_with_docstrings[key]
            #     continue
            # print(f"key = {key}")
            merge_inf = self.merge_inf(dict_with_docstrings[key])
            print(merge_inf)
            match key:
                case "params":
                    content += f"Параметр(ы) {merge_inf}\n\n"
                case "return":
                    content += f"Возвращает {merge_inf}\n\n"
                case "rtype":
                    content += f"Тип возвращаемого объекта {merge_inf}\n\n"
                case "notes":
                    content += f"замечания {merge_inf}\n\n"
                case "type":
                    content += f"Тип параметра {merge_inf}\n\n"
                case _:
                    content += merge_inf + "\n\n"

            # if dict_with_docstrings[key].__class__ is dict:
            #     content += f"**{article}**: {self.unpack_docstrings(dict_with_docstrings[key])}\n\n"
            # elif dict_with_docstrings[key] is None:
            #     content += f"**{article}**: НЕОБХОДИМО ЗАПОЛНИТЬ\n\n"
            # elif not dict_with_docstrings[key] and dict_with_docstrings[key].__class__ is dict:
            #     content += f"**{article}**: не принимает\n\n"
            # elif dict_with_docstrings[key].__class__ is str:
            #     content += f"**{article}**: {dict_with_docstrings[key]}\n\n"
                # ic(self.unpack_docstrings(dict_with_docstrings[key]))
            # else:
                # content += f"**{article}**: {self.unpack_docstrings(dict_with_docstrings[key])}\n\n"
            #
            # if content is list:
            #     "".join(content)
        return content

    def merge_inf(self, some_input) -> str:
        content = ""
        if isinstance(some_input, dict):
            for key in some_input.keys():
                if key == "params":
                    content += self.merge_inf(some_input[key]) + "\n\n"
                else:
                    content += f"{key}: {some_input[key]} \n\n"
        elif isinstance(some_input, list):
            content.join(some_input)
        elif isinstance(some_input, str):
            return some_input
        return content



    def code2flow_diagramm_generate(self):
        for pathes_to_files in self.python_files_combinations_for_code2flow:
            self.code2flow_creater(pathes_to_files)



    def check_directories(self, list_dirs: list) -> None:
        """
        Функция проверяет существование директорий и создает их, если они отсуствуют
        """
        for dir_from_list in list_dirs:
            if not (os.path.exists(dir_from_list) and os.path.isdir(dir_from_list)):
                os.mkdir(dir_from_list)

    
    def file_filter(self, directories_python_files: str) -> list:
        """
        Функция возвращает .py файлы в директории
        """
        files = [file for file in os.listdir(directories_python_files)
            if (file.endswith('.py') and
                 file not in self.file_black_list)]
        return files
        

    def code2flow_creater(self, path_list: list) -> None:
        """
        Функция создает диаграммы на основе путей до .py файлов в папке directory_with_graphs
        :param path_list: список путей до .py файлов в виде списка
        :type path_list: list
        :param directory_with_graphs: путь до сгенерированных диаграмм
        :type directory_with_graphs: str
        :return: None
        """
        code2flow.code2flow(path_list[0], path_list[1])
        
    # def parse_restructuredtext(self, docstring):
    #     """
    #     Парсит docstring в формате reStructuredText и возвращает структурированные данные.
    #     """
    #     if not docstring:
    #         return {}
    #
    #     lines = docstring.strip().split("\n")
    #     # ic(lines)
    #     return lines

    def extract_docstrings(self, file_path):
        """
        Извлекает docstrings из Python файла.
        :param file_path: test1
        :note: test2
        """
        with open(file_path, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read(), filename=file_path)
        # ic(tree)

        docstrings = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_doc = parse_restructuredtext(ast.get_docstring(node) or "")
                docstrings[f"Class: {node.name}"] = class_doc
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        func_doc = parse_restructuredtext(ast.get_docstring(child) or "")
                        docstrings[f"Method: {node.name}.{child.name}"] = func_doc

            elif isinstance(node, ast.FunctionDef):
                func_doc = parse_restructuredtext(ast.get_docstring(node) or "")
                docstrings[f"Function: {node.name}"] = func_doc
        # ic(docstrings.keys())
        return docstrings


            





