import os
import ast
import code2flow
import re

def parse_restructuredtext(docstring):
    """
    Парсит docstring в формате reStructuredText и возвращает структурированные данные.

    Поддерживает такие теги, как :param:, :type:, :rtype:, :return:, :note: и т.д.

    :param docstring: Docstring для парсинга
    :type docstring: str
    :return: Словарь с ключами и значениями, извлеченными из docstring
    :rtype: dict
    """
    # Стандартная структура возвращаемого результата
    parsed_data = {
        "description": "",
        "params": {},
        "return": None,
        "rtype": None,
        "notes": [],
    }

    if not docstring:
        return parsed_data  # Возвращаем пустую структуру, если docstring отсутствует

    current_section = "description"
    lines = docstring.strip().split("\n")

    param_pattern = re.compile(r":param (\w+)(?: \((.+)\))?: (.+)")
    type_pattern = re.compile(r":type (\w+): (.+)")
    rtype_pattern = re.compile(r":rtype: (.+)")
    return_pattern = re.compile(r":return: (.+)")
    note_pattern = re.compile(r":note: (.+)")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        param_match = param_pattern.match(line)
        if param_match:
            param_name, param_type, param_desc = param_match.groups()
            parsed_data["params"][param_name] = {
                "description": param_desc,
                "type": param_type or None,
            }
            current_section = "params"
            continue

        type_match = type_pattern.match(line)
        if type_match:
            param_name, param_type = type_match.groups()
            if param_name in parsed_data["params"]:
                parsed_data["params"][param_name]["type"] = param_type
            else:
                parsed_data["params"][param_name] = {
                    "description": "",
                    "type": param_type,
                }
            current_section = "params"
            continue

        rtype_match = rtype_pattern.match(line)
        if rtype_match:
            parsed_data["rtype"] = rtype_match.group(1)
            current_section = "rtype"
            continue

        return_match = return_pattern.match(line)
        if return_match:
            parsed_data["return"] = return_match.group(1)
            current_section = "return"
            continue

        note_match = note_pattern.match(line)
        if note_match:
            parsed_data["notes"].append(note_match.group(1))
            current_section = "notes"
            continue

        # Если это продолжение текущего раздела
        if current_section == "description":
            parsed_data["description"] += f" {line}".strip()
        elif current_section == "params":
            last_param = list(parsed_data["params"].keys())[-1]
            parsed_data["params"][last_param]["description"] += f" {line}".strip()
        elif current_section == "return":
            parsed_data["return"] += f" {line}".strip()
        elif current_section == "notes":
            parsed_data["notes"][-1] += f" {line}".strip()

    return parsed_data


def create_readme(inf: dict,
                  dir: str,
                  name: str,
                  add_inf: str = "") -> None:
    """
    Создает README на основе извлеченной информации

    :param inf: Входящий словарь с информацией
    :type inf: dict
    :param dir: путь до файлов с документацией
    :type dir: str
    :param name: имя анализируемого файла
    :type name: str
    :param add_inf: добавочная информация
    :type add_inf: str
    :return: None
    :rtype: None
    """
    os.makedirs(dir, exist_ok=True)
    readme_path = os.path.join(dir, f"{name.removesuffix('.py')}.md")
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
    content.append(add_inf)
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


def extract_docstrings(file_path: str) -> dict:
    """
    Извлекает docstrings из Python файла
    :param file_path: Путь до .py файла
    :type file_path: str
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
        self.img_dir = "../img/"
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
        for step in self.python_files:
            code2flow.code2flow(step[0], step[1])
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
        inf = extract_docstrings(source_file_path)
        add_inf = f"# Диаграмма \n ![Диаграмма потока](../img/{name.removesuffix('.py')}.png)"
        create_readme(inf, self.readme_dir, name, add_inf=add_inf)

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

