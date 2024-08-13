# Ollama entity recognition benchmarks 


### Purpose

This repository contains the code and data for a JSON-based testing framework that evaluates the performance of locally installed large language models (LLMs) on macOS using Ollama. The benchmarks are designed to test different Named Entity Recognition (NER) types, focusing on both speed and accuracy. 


### Roadmap

* Initial basic post 
* Json level configuration - you can setup tests and models just by editing a json file

### Quick Start Installation

1. Install [ollama](https://ollama.com/) and download models you think would suit your needs
2. Create a virtual env and pip install prettytable and ollama
3. Use generate_models.py to export what models you have installed locally in ollama
4. Create your own json file, you can use the sample_json.json as a template
5. Run code with `python3 main.py sample_config.json`
6. Profit

### Configuration

To run the tests and the strings you really just need two values in your json file. The  test_string you want to test against and the strings you want to find set in the test_cases.

```json 
{
  "test_string": "Your test string here",
  "test_cases": ["test case 1", "test case 2"]
}
```
But you can configure more, including the specific models to run for this file and also the string passed to the chat. If you generate the models using the provided file then you can just copy and paste the models you want to test into the json file.

```json
{
  "test_string": "Your test string here",
  "test_cases": ["test case 1", "test case 2"],
  "models": [
    {
      "name": "model_name",
      "parameter_size": "7.6B"
    }
  ],
  "message_template": "return as json all the entities in the following string: {test_string}"
}
```


### Output

The output is a table that shows the time taken to process the test cases, the number of entities found, the number of test cases that passed, and the size of the parameters used.

| Model   | Temperature | Time Taken (s)      | Entity Count | Test Case Count | Valid JSON | Parameter Size |
|---------|-------------|---------------------|--------------|-----------------|------------|----------------|
| qwen2:7b| 0.0         | 22.019516944885254  | 1            | 2               | True       | 7.6B           |
| qwen2:7b| 1.0         | 7.003676891326904   | 1            | 0               | True       | 7.6B           |


### Feedback and contact

If you are interested, email me (Chris McCabe) at info@datasignal.uk
Or on twitter https://x.com/chris_mc_cabe

[DataSignal](https://datasignal.uk) 

### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

### References
* The original blog post was hosted on the [Datasignal Blog](https://datasignal.uk/blog/ner.html)
* The new blog post discussing the updates made [Datasignal Blog](https://datasignal.uk/blog/ner-framework.html)
