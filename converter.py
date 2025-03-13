from xml.dom import minidom
import xml.etree.ElementTree as ET
import re

def xml_converter(code):
    """
    Converte pseudo-código para elementos XML para o programa Flowgorithm

    :param code: O pseudo-código a ser convertido
    :return:  XML formatado para o body do fluxograma
    """
    def parse_code(code_lines):
        result = []
        i = 0
        
        while i < len(code_lines):
            line = code_lines[i].strip()
            comments = line.split('#', 1)
            main_line = comments[0].strip()
            
            if not main_line:
                i += 1
                continue
                
            # If statement
            if_match = re.match(r'if\s+(.+):', main_line)
            if if_match:
                condition = if_match.group(1)
                if_block = {'type': 'if', 'condition': condition, 'then': [], 'else': []}
                
                # Processar o bloco then
                i += 1
                current_branch = 'then'
                
                while i < len(code_lines):
                    sub_line = code_lines[i].strip()
                    sub_comments = sub_line.split('#', 1)
                    sub_main = sub_comments[0].strip()
                    
                    if not sub_main:
                        i += 1
                        continue
                        
                    # Procurar por else
                    if sub_main == 'else:':
                        current_branch = 'else'
                        i += 1
                        continue
                        
                    # Procurar por end
                    if sub_main == 'end':
                        i += 1
                        break
                        
                    # Procurando recursivamente por if aninhado
                    if re.match(r'if\s+(.+):', sub_main):
                        nested_if, new_i = parse_code(code_lines[i:])
                        if_block[current_branch].append(nested_if)
                        i += new_i
                    else:
                        if_block[current_branch].append(sub_main)
                        i += 1
                        
                result.append(if_block)
                continue
            
            result.append(main_line)
            i += 1
            
        return result, i

    def process_structure(structure, parent_element):
        for item in structure:
            if isinstance(item, dict) and item['type'] == 'if':
                if_element = ET.SubElement(parent_element, 'if', expression=item['condition'])
                then_element = ET.SubElement(if_element, 'then')
                process_lines(item['then'], then_element)
                else_element = ET.SubElement(if_element, 'else')
                process_lines(item['else'], else_element)
            else:
                process_line(item, parent_element)
    
    def process_lines(lines, parent_element):
        for line in lines:
            if isinstance(line, dict):
                process_structure([line], parent_element)
            else:
                process_line(line, parent_element)
    
    def process_line(line, parent_element):
        # Procurar por declaração
        match_var = re.match(r'(\w+)(?:\s*(\[)(\d+)\]\s*|\s+)(\w+)', line)
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

            ET.SubElement(parent_element, 'declare', name=name, type=type_flowgorithm, array=is_array, size=array_size)
            return

        # Verificar se é uma entrada de dados
        match_input = re.match(r'(\w+)\s*=\s*input\(\)', line)
        if match_input:
            name = match_input.group(1)
            ET.SubElement(parent_element, 'input', variable=name)
            return

        # Verificar se é uma saída de dados
        match_output = re.match(r'print\("([^"]*)"\)', line)
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
                        
            ET.SubElement(parent_element, "output", expression=processed_text, newline="True")
            return

        # Verificar se é uma atribuição
        match_assign = re.match(r'(\w+)\s*=\s*(.*)', line)
        if match_assign and not re.match(r'(\w+)\s*=\s*input\(\)', line):
            name_var, expression = match_assign.groups()
            ET.SubElement(parent_element, "assign", variable=name_var, expression=expression)
            return

    # Main processing
    body = ET.Element('body')
    lines = code.strip().split('\n')
    
    parsed_structure, _ = parse_code(lines)
    process_structure(parsed_structure, body)

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

if n2 == 0:
    print("Não é possível dividir por zero")
else:
    result = n1 / n2
    print("Resultado é {result}")
end
'''
    xml_body = xml_converter(codigo_exemplo)
    print(xml_body)