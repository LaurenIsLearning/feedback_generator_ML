# Tropos  

A system that gives feedback on student assignments using pretrained models.

## How does it work?

### Installing

In order to install this tool you must run:

```tty
pip install -r requirements.txt
```

### Running
#### Locally
Run this command in the root directory of the repository.

```tty
python .
``` 

#### In Google Collab
Open the `notebook.ipynb` file and run all of the cells.


## Data Dictionary
### test_feedback_console(`prompt_type`, `model`, `requirements_path`, `example_dir`, `target_dir`, `output_dir`, `output_mode`, `max_examples`)
| Parameter | Definition | Accepted Values / Notes |
|:---|:---|:---|
| `prompt_type` | Prompting strategy used to guide feedback generation. | `"FewShot"` or `"FewShot-Llama"`, `"OneShot"`, `"ZeroShot"`|
| `model` | Model name used to generate feedback. | `"gpt-4o"`, `"gpt-4.1"`, `"deepseek-chat"`, `"gemini-1.5-pro-latest"`, `"meta-llama/llama-4-scout-17b-16e-instruct"`, `"claude-3-opus-20240229"` |
| `requirements_path` | File path to the assignment requirements document. | `.docx` file |
| `example_dir` | Directory containing example student submissions for the model. | Folder path |
| `target_dir` | Directory containing target (unmarked) student submissions to generate feedback for. | Folder path |
| `output_dir` | Directory to save generated feedback documents. | Folder path (created if doesn't exist) |
| `output_mode` | How to display feedback in console. | `"pretty"` = prints readably, `"raw"`= prints raw for debugging, `"none"` = no print |
| `max_examples` | Limit the number of examples loaded (for RateLimitErrors). | Integer or `None` |
