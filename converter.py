import xml.etree.ElementTree as ET
import re

def xml_converter(code):
    """
    Converte pseudo-código para elementos XML para o programa Flowgorithm

    :param code: O pseudo-código a ser convertido
    :return:  XML formatado para o body do fluxograma
    """

    body = ET.Element('body')
    lines = code.strip().split('\n')

    for line in lines:
        comments = line.split('#', 1)
        main_line = comments[0].strip()

        if not main_line:
            continue

        # Procurar por declaração
        match_var = re.match(r'(\w+)(?:\s*(\[)(\d+)\]\s*|\s+)(\w+)', main_line)
        if match_var:
            type, array_indicator, array_size, name = match_var.groups()

            # Mapear tipo para formato Flowgorithm
            type_flowgorithm = "Integer"  # padrão
            if type.lower() == "int":
                type_flowgorithm = "Integer"
            elif type.lower() in ["float", "double", "real"]:
                type_flowgorithm = "Real"
            elif type.lower() in ["str", "string"]:
                type_flowgorithm = "String"
            elif type.lower() in ["bool", "boolean"]:
                type_flowgorithm = "Boolean"
            
            is_array = "True" if array_indicator else "False"
            array_size = array_size if array_size else "0"

            ET.SubElement(body, 'declare', name=name, type=type_flowgorithm, array=is_array, size=array_size)
            continue

        # Verificar se é uma entrada de dados
        match_input = re.match(r'(\w+)\s*=\s*input\(\)', main_line)
        if match_input:
            name = match_input.group(1)
            ET.SubElement(body, 'input', variable=name)
            continue

