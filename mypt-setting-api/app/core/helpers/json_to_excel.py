import pandas as pd
import json

def json_to_excel(json_input, output_file_name, path_to_object=""):
    """
        json_input: string, json type, dataFrame
        output_file_name: path to output file
        path_to_object: list keys contain data in demand export (separated by a "/")
            example: key1/key2/key3/...
        return: true or false

        example: json_to_excel(data_input, 'test.xlsx', 'data1/data2/data3/data4')
    """
    try:
        data = json.loads(json.dumps(json_input)) #if type(json_input) == str else json_input
 
        if path_to_object:
            pathItems = path_to_object.split('/')

            for pathItem in pathItems:
                data = data.get(pathItem)

        data = pd.DataFrame(data.to_list() if hasattr(data, "to_list") else data)

        data.to_excel(output_file_name)
        return True
    except Exception as e:
        print(e)
        return False
