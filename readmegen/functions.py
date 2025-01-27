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
