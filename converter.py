from xml.dom import minidom
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
            array_size = array_size if array_size else ""

            ET.SubElement(body, 'declare', name=name, type=type_flowgorithm, array=is_array, size=array_size)
            continue

        # Verificar se é uma entrada de dados
        match_input = re.match(r'(\w+)\s*=\s*input\(\)', main_line)
        if match_input:
            name = match_input.group(1)
            ET.SubElement(body, 'input', variable=name)
            continue

        # Verificar se é uma saída de dados
        # print = no new line
        # println = new line
        match_output = re.match(r'print\("([^"]*)"\)', main_line)
        if match_output:
            text = match_output.group(1)

            # Verificar se há variáveis
            processed_text = text
            vars_output = re.findall(r'\{(\w+)\}', text)
            
            for var in vars_output:
                processed_text = processed_text.replace(f"{{{var}}}", '" & ' + var + ' & "')
            
            # Se houver variáveis, reformatar a expressão
            if vars_output:
                processed_text = '"' + processed_text + '"'
                processed_text = processed_text.replace('" & "', '')
            else:
                processed_text = f'"{processed_text}"'
                        
            ET.SubElement(body, "output", expression=processed_text, newline="True")
            continue

        # Verificar se é uma atribuição
        match_assign = re.match(r'(\w+)\s*=\s*(.*)', main_line)
        if match_assign:
            name_var, expression = match_assign.groups()
            
            # Verificar se não é uma entrada de dados (já tratado acima)
            if "input()" not in expression:
                ET.SubElement(body, "assign", variable=name_var, expression=expression)
            continue

    # Criar uma string XML formatada
    rough_string = ET.tostring(body, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    xml_string = reparsed.toprettyxml(indent="    ")

    return xml_string

# Exemplo de uso
if __name__ == "__main__":
    codigo_exemplo = '''
int n1
int n2
int result

print("Digite o primeiro número")
n1 = input()
print("Digite o segundo número")
n2 = input()

result = n1 * n2

print("Resultado é {result}")
'''
    xml_body = xml_converter(codigo_exemplo)
    print(xml_body)