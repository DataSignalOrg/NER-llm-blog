import json
import ollama

def generate_default_models():
    # Get the list of installed models
    installed_models = ollama.list()

    # Format the models into the required structure
    models = []
    for model in installed_models['models']:
        models.append({
            'name': model['name'],
            'parameter_size': model['details'].get('parameter_size', 'unknown')
        })

    # Save the formatted models to default_models.json
    with open('default_models.json', 'w') as f:
        json.dump({'models': models}, f, indent=4)

if __name__ == "__main__":
    generate_default_models()