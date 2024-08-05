import ollama
import time
import json
import os
from prettytable import PrettyTable
from typing import List, Dict, Any, Optional


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
    def save_raw_response(model_name: str, temperature: float, response_content: str):
        os.makedirs('./results', exist_ok=True)
        with open(f'./results/{model_name}_temp_{temperature}_raw.json', 'w') as f:
            f.write(response_content)

    @staticmethod
    def save_extracted_json(model_name: str, temperature: float, entities: List[Dict[str, Any]]):
        with open(f'./results/{model_name}_temp_{temperature}.json', 'w') as f:
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

# Main execution
test_string = """
Payments from Hodder and Stoughton UK, Carmelite House, 50 Victoria Embankment, London EC4Y 0DZ, via United Agents, 12-26 Lexington St, London W1F 0LE: 12 July 2022, received \u00a3439.82 for royalties on book already written. Hours: no additional hours. (Registered 28 July 2022) 10 August 2022, received \u00a3519.69 for royalties on book already written. Hours: no additional hours. (Registered 23 August 2022) 5 October 2022, received \u00a31,771.82 for royalties on book already written. Hours: no additional hours. (Registered 27 October 2022) 14 March 2023, received \u00a3673.11 for royalties on book already written. Hours: no additional hours. (Registered 03 April 2023) 5 April 2023, received \u00a32,590.85 for royalties on book already written. Hours: no additional hours. (Registered 24 April 2023)",
      "Payments from HarperCollins UK, 1 London Bridge St, London SE1 9GF, via Rogers, Coleridge and White Ltd, 20 Powis Mews, London W11 1JN: 30 April 2022, received \u00a3382.03 for royalties on books already written. Hours: no additional hours. (Registered 27 May 2022) 18 October 2022, received \u00a3171.03 for royalties on books already written. Hours: no additional hours. (Registered 27 October 2022) 6 January 2023, received \u00a3510,000 as an advance on an upcoming book yet to be published. Hours: approx. 10 hrs to date. (Registered 12 January 2023) <span class=\"highlight\">4 May 2023, received \u00a3402.81 for royalties on books already written. Hours: no additional hours. (Registered 16 May 2023)</span>
"""

test_cases = [
  'Rogers, Coleridge and White Ltd',
  'HarperCollins UK',
  '27 May 2022',
  'Hodder and Stoughton UK',
  'EC4Y 0DZ',
  '27 October 2022'
]

result_table = ResultTable()

for model in ollama.list()['models']:
    parameter_size = model['details']['parameter_size']
    for temperature in [0.0, 1.0]:
        start = time.time()
        chat = OllamaChat(model_name=model['name'], temperature=temperature)
        response = chat.get_response(test_string)
        time_taken = time.time() - start

        response_content = response['message']['content']
        valid_json = OllamaChat.is_valid_json(response_content)
        ResultSaver.save_raw_response(model_name=model['name'], temperature=temperature, response_content=response_content)

        if valid_json:
            entities = ResponseProcessor.extract_json(response_content)
            ResultSaver.save_extracted_json(model_name=model['name'], temperature=temperature, entities=entities)
            entity_count = len(entities)
            test_case_count = sum(1 for test_case in test_cases if test_case in response_content)
        else:
            entity_count = 0
            test_case_count = 0

        result_table.add_result(model=model['name'], temperature=temperature, time_taken=time_taken, entity_count=entity_count, test_case_count=test_case_count, valid_json=valid_json, parameter_size=parameter_size)

result_table.sort_results()
result_table.display()