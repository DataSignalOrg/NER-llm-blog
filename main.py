import json
import sys
import os
import time
from common import process_model, ResultTable

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    with open(config_file, 'r') as f:
        config = json.load(f)

    test_string = config['test_string']
    test_cases = config['test_cases']
    message_template = config.get('message_template')

    if 'models' in config:
        models = config['models']
    else:
        with open('default_models.json', 'r') as f:
            default_models = json.load(f)
        models = default_models['models']

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    directory = f'./results/{os.path.basename(config_file).split(".")[0]}_{timestamp}'

    result_table = ResultTable()

    for model in models:
        process_model(directory, model['name'], model['parameter_size'], test_string, test_cases, result_table, message_template)

    result_table.sort_results()
    result_table.display()