# Propriedades:
name = "Soma"
authors = "Victor"
about = ""

from xml.dom import minidom
import xml.etree.ElementTree as ET
import re
import datetime

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
                
                # Process the then block
                i += 1
                current_branch = 'then'
                
                while i < len(code_lines):
                    sub_line = code_lines[i].strip()
                    sub_comments = sub_line.split('#', 1)
                    sub_main = sub_comments[0].strip()
                    
                    if not sub_main:
                        i += 1
                        continue
                        
                    # Check for else
                    if sub_main == 'else:':
                        current_branch = 'else'
                        i += 1
                        continue
                        
                    # Check for end
                    if sub_main == 'end':
                        i += 1
                        break
                        
                    # Recursive parsing for nested structures
                    if re.match(r'if\s+(.+):|for\s+(.+)\s+in\s+range\((.+)\):|while\s+(.+):|do:', sub_main):
                        nested_structure, new_i = parse_code(code_lines[i:])
                        if_block[current_branch].append(nested_structure)
                        i += new_i
                    else:
                        if_block[current_branch].append(sub_main)
                        i += 1
                        
                result.append(if_block)
                continue
                
            # For loop
            for_match = re.match(r'for\s+(\w+)\s+in\s+range\((.+)\):', main_line)
            if for_match:
                var_name = for_match.group(1)
                range_params = for_match.group(2).split(',')
                
                # Parse range parameters
                if len(range_params) == 1:
                    start = "0"
                    end = range_params[0].strip()
                    step = "1"
                elif len(range_params) == 2:
                    start = range_params[0].strip()
                    end = range_params[1].strip()
                    step = "1"
                else:
                    start = range_params[0].strip()
                    end = range_params[1].strip()
                    step = range_params[2].strip()
                
                direction = "inc" if step == "1" or float(step) > 0 else "dec"
                step = str(abs(int(float(step)))) if step.replace('.', '', 1).isdigit() else "1"
                
                for_block = {
                    'type': 'for',
                    'variable': var_name,
                    'start': start,
                    'end': end,
                    'direction': direction,
                    'step': step,
                    'body': []
                }
                
                # Process the loop body
                i += 1
                while i < len(code_lines):
                    sub_line = code_lines[i].strip()
                    sub_comments = sub_line.split('#', 1)
                    sub_main = sub_comments[0].strip()
                    
                    if not sub_main:
                        i += 1
                        continue
                        
                    # Check for end
                    if sub_main == 'end':
                        i += 1
                        break
                        
                    # Recursive parsing for nested structures
                    if re.match(r'if\s+(.+):|for\s+(.+)\s+in\s+range\((.+)\):|while\s+(.+):|do:', sub_main):
                        nested_structure, new_i = parse_code(code_lines[i:])
                        for_block['body'].append(nested_structure)
                        i += new_i
                    else:
                        for_block['body'].append(sub_main)
                        i += 1
                        
                result.append(for_block)
                continue
                
            # While loop
            while_match = re.match(r'while\s+(.+):', main_line)
            if while_match:
                condition = while_match.group(1)
                while_block = {
                    'type': 'while',
                    'condition': condition,
                    'body': []
                }
                
                # Process the loop body
                i += 1
                while i < len(code_lines):
                    sub_line = code_lines[i].strip()
                    sub_comments = sub_line.split('#', 1)
                    sub_main = sub_comments[0].strip()
                    
                    if not sub_main:
                        i += 1
                        continue
                        
                    # Check for end
                    if sub_main == 'end':
                        i += 1
                        break
                        
                    # Recursive parsing for nested structures
                    if re.match(r'if\s+(.+):|for\s+(.+)\s+in\s+range\((.+)\):|while\s+(.+):|do:', sub_main):
                        nested_structure, new_i = parse_code(code_lines[i:])
                        while_block['body'].append(nested_structure)
                        i += new_i
                    else:
                        while_block['body'].append(sub_main)
                        i += 1
                        
                result.append(while_block)
                continue
                
            # Do-while loop
            do_match = re.match(r'do:', main_line)
            if do_match:
                do_block = {
                    'type': 'do',
                    'condition': '',
                    'body': []
                }
                
                # Process the loop body
                i += 1
                while i < len(code_lines):
                    sub_line = code_lines[i].strip()
                    sub_comments = sub_line.split('#', 1)
                    sub_main = sub_comments[0].strip()
                    
                    if not sub_main:
                        i += 1
                        continue
                    
                    # Check for while condition at the end
                    while_end_match = re.match(r'while\s+(.+)', sub_main)
                    if while_end_match:
                        do_block['condition'] = while_end_match.group(1)
                        i += 1
                        break
                        
                    # Check for end (shouldn't happen in do-while but just in case)
                    if sub_main == 'end':
                        i += 1
                        break
                        
                    # Recursive parsing for nested structures
                    if re.match(r'if\s+(.+):|for\s+(.+)\s+in\s+range\((.+)\):|while\s+(.+):|do:', sub_main):
                        nested_structure, new_i = parse_code(code_lines[i:])
                        do_block['body'].append(nested_structure)
                        i += new_i
                    else:
                        do_block['body'].append(sub_main)
                        i += 1
                        
                result.append(do_block)
                continue
            
            # Regular line
            result.append(main_line)
            i += 1
            
        return result, i

    def process_structure(structure, parent_element):
        for item in structure:
            if isinstance(item, dict):
                if item['type'] == 'if':
                    # Create if statement with condition
                    if_element = ET.SubElement(parent_element, 'if', expression=item['condition'])
                    
                    # Process then branch
                    then_element = ET.SubElement(if_element, 'then')
                    process_lines(item['then'], then_element)
                    
                    # Process else branch
                    else_element = ET.SubElement(if_element, 'else')
                    process_lines(item['else'], else_element)
                elif item['type'] == 'for':
                    # Create for loop
                    for_element = ET.SubElement(parent_element, 'for', 
                                               variable=item['variable'],
                                               start=item['start'],
                                               end=item['end'],
                                               direction=item['direction'],
                                               step=item['step'])
                    process_lines(item['body'], for_element)
                elif item['type'] == 'while':
                    # Create while loop
                    while_element = ET.SubElement(parent_element, 'while', expression=item['condition'])
                    process_lines(item['body'], while_element)
                elif item['type'] == 'do':
                    # Create do-while loop
                    do_element = ET.SubElement(parent_element, 'do', expression=item['condition'])
                    process_lines(item['body'], do_element)
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

    # Cria estrutura XML do flowgorithm
    flowgorithm = ET.Element('flowgorithm', fileversion="4.2")
    attributes = ET.SubElement(flowgorithm, 'attributes')
    ET.SubElement(attributes, 'attribute', name="name", value=name)
    ET.SubElement(attributes, 'attribute', name="authors", value=authors)
    ET.SubElement(attributes, 'attribute', name="about", value=about)

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
    ET.SubElement(attributes, 'attribute', name="saved", value=current_time)

    created_base64 = "cm9zYWw7U0hJRlRNQzsyMDI1LTAzLTEyOyIwNzoxMDozMCAiOzIyNTU="
    ET.SubElement(attributes, 'attribute', name="created", value=created_base64)

    edited_base64 = "cm9zYWw7U0hJRlRNQzsyMDI1LTAzLTEyOyIwNzoxNTo0NSAiOzE7MjM2NQ=="
    ET.SubElement(attributes, 'attribute', name="edited", value=edited_base64)

    function = ET.SubElement(flowgorithm, 'function', name="Main", type="None", variable="")
    ET.SubElement(function, 'parameters')

    body = ET.SubElement(function, 'body')
    lines = code.strip().split('\n')

    parsed_structure, _ = parse_code(lines)
    process_structure(parsed_structure, body)

    # Criar uma string XML formatada
    rough_string = ET.tostring(flowgorithm, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    xml_string = reparsed.toprettyxml(indent="    ")

    return xml_string
