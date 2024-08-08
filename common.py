import json
import time
import os
from prettytable import PrettyTable
from typing import List, Dict, Any
import ollama

class OllamaChat:
    def __init__(self, model_name: str, temperature: float):
        self.model_name = model_name
        self.temperature = temperature

    def get_response(self, test_string: str) -> Dict[str, Any]:
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    'role': 'user',
                    'content': 'return as json all the entities in the following string: ' + test_string,
                },
            ],
            format='json',
            options={'temperature': self.temperature}
        )
        return response

    @staticmethod
    def is_valid_json(response_content: str) -> bool:
        try:
            json.loads(response_content)
            return True
        except json.JSONDecodeError:
            return False

class ResponseProcessor:
    @staticmethod
    def extract_json(response_content: str) -> List[Dict[str, Any]]:
        if '```json' in response_content and '```' in response_content:
            json_start = response_content.index('```json') + len('```json')
            json_end = response_content.rindex('```')
            json_str = response_content[json_start:json_end].strip()
        elif response_content.startswith('json') and '<|end-output|>' in response_content:
            json_start = response_content.index('json') + len('json')
            json_end = response_content.index('<|end-output|>')
            json_str = response_content[json_start:json_end].strip()
        else:
            json_str = response_content

        try:
            entities = json.loads(json_str)
        except json.JSONDecodeError:
            entities = []

        return entities

class ResultSaver:
    @staticmethod
    def save_raw_response(directory: str, model_name: str, temperature: float, response_content: str):
        os.makedirs(directory, exist_ok=True)
        with open(f'{directory}/{model_name}_temp_{temperature}_raw.json', 'w') as f:
            f.write(response_content)

    @staticmethod
    def save_extracted_json(directory: str, model_name: str, temperature: float, entities: List[Dict[str, Any]]):
        with open(f'{directory}/{model_name}_temp_{temperature}.json', 'w') as f:
            json.dump(entities, f, indent=4)

class ResultTable:
    def __init__(self):
        self.table = PrettyTable()
        self.table.field_names = ["Model", "Temperature", "Time Taken (s)", "Entity Count", "Test Case Count", "Valid JSON", "Parameter Size"]
        self.results = []

    def add_result(self, model: str, temperature: float, time_taken: float, entity_count: int, test_case_count: int, valid_json: bool, parameter_size: str):
        self.results.append({
            'model': model,
            'temperature': temperature,
            'time_taken': time_taken,
            'entity_count': entity_count,
            'test_case_count': test_case_count,
            'valid_json': valid_json,
            'parameter_size': parameter_size
        })

    def sort_results(self):
        self.results.sort(key=lambda x: x['test_case_count'], reverse=True)

    def display(self):
        for result in self.results:
            self.table.add_row([result['model'], result['temperature'], result['time_taken'], result['entity_count'], result['test_case_count'], result['valid_json'], result['parameter_size']])
        print(self.table)


def process_model(directory: str, model_name: str, parameter_size: str, test_string: Any, test_cases: List[str], result_table: ResultTable):
    if isinstance(test_string, list):
        results = []
        for string in test_string:
            result = process_single_string(directory, model_name, parameter_size, string, test_cases, result_table)
            results.append(result)
        ResultSaver.save_raw_response(directory, model_name, 1.0, json.dumps(results, indent=4))
    else:
        process_single_string(directory, model_name, parameter_size, test_string, test_cases, result_table)

def process_single_string(directory: str, model_name: str, parameter_size: str, test_string: str, test_cases: List[str], result_table: ResultTable):
    results = []
    for temperature in [0.0, 1.0]:
        start = time.time()
        chat = OllamaChat(model_name=model_name, temperature=temperature)
        response = chat.get_response(test_string)
        time_taken = time.time() - start

        response_content = response['message']['content']
        valid_json = OllamaChat.is_valid_json(response_content)
        ResultSaver.save_raw_response(directory, model_name, temperature, response_content)

        if valid_json:
            entities = ResponseProcessor.extract_json(response_content)
            ResultSaver.save_extracted_json(directory, model_name, temperature, entities)
            entity_count = len(entities)
            test_case_count = sum(1 for test_case in test_cases if test_case in response_content)
        else:
            entity_count = 0
            test_case_count = 0

        result_table.add_result(model=model_name, temperature=temperature, time_taken=time_taken, entity_count=entity_count, test_case_count=test_case_count, valid_json=valid_json, parameter_size=parameter_size)
        results.append(response_content)
    return results