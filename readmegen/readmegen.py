import os
import ast
import textwrap
import re
import os
from os.path import isdir
import shutil
import sys
import code2flow
from icecream import ic


class ReadmeGenerator:
    def __init__(self, 
                 python_files_combinations_for_code2flow: list,
                 params: bool = True,
                 returns: bool = True):
        self.params = params
        self.returns = returns
        self.img_dir = "./img/"
        self.readme_dir = "./description/"
        self.file_black_list = ["annotation.py, __init__.py"]
        self.python_files_combinations_for_code2flow = python_files_combinations_for_code2flow 

    def generate(self, directories_python_files: str):
        """
        Основная функция генерации файлов readme
        :param directories_python_files: 
        :type directories_python_files: str
        """
        self.check_directories([self.img_dir, self.readme_dir])
        files = self.file_filter(directories_python_files)
        for file in files:
            self.one_generate(directories_python_files + file)

    def one_generate(self, source_file_path: str):
        """

        """
        if not os.path.exists(source_file_path):
            print(f"Файл {source_file_path} не найден.")
            return
        self.extract_docstrings(source_file_path)


    def code2flow_diagramm_generate(self):
        for pathes_to_files in self.python_files_combinations_for_code2flow:
            self.code2flow_creater(pathes_to_files)



    def check_directories(self, list_dirs) -> None:
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
        
    def parse_restructuredtext(self, docstring):
        """
        Парсит docstring в формате reStructuredText и возвращает структурированные данные.
        """
        if not docstring:
            return {}

        lines = docstring.strip().split("\n")
        ic(lines)

    def extract_docstrings(self, file_path):
        """
        Извлекает docstrings из Python файла.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read(), filename=file_path)
        ic(tree)

        docstrings = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_doc = self.parse_restructuredtext(ast.get_docstring(node) or "")
                docstrings[f"Class: {node.name}"] = class_doc
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        func_doc = self.parse_restructuredtext(ast.get_docstring(child) or "")
                        docstrings[f"Method: {node.name}.{child.name}"] = func_doc

            elif isinstance(node, ast.FunctionDef):
                func_doc = self.parse_restructuredtext(ast.get_docstring(node) or "")
                docstrings[f"Function: {node.name}"] = func_doc

        return docstrings


            





