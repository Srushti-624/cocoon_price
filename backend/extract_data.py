import json
import ast
import os

notebook_path = r"c:\Users\HP\Desktop\Capstone\cocoon_project\caccoon_project.ipynb"
output_dir = r"c:\Users\HP\Desktop\Capstone\cocoon_project\backend"

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# The data is in the cell that has "files.upload()" in source
# We look for the execute_result output
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "files.upload()" in source:
            for output in cell['outputs']:
                if output['output_type'] == 'execute_result':
                    if 'text/plain' in output['data']:
                        # The content is a list of strings, join them
                        data_str = "".join(output['data']['text/plain'])
                        # It's a binary repr string like "{'file': b'...'}"
                        # We need to parse this. ast.literal_eval is perfect.
                        try:
                            files_dict = ast.literal_eval(data_str)
                            for filename, content_bytes in files_dict.items():
                                clean_name = filename.replace(' ', '_').lower() # Clean up names
                                save_path = os.path.join(output_dir, clean_name)
                                with open(save_path, 'wb') as out_f:
                                    out_f.write(content_bytes)
                                print(f"Saved {clean_name}")
                        except Exception as e:
                            print(f"Error parsing data: {e}")
