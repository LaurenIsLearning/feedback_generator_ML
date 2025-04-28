import sys

# main function to test local/notebook setup
from tropos import test_feedback_console
from tropos.models.tuned_llama.demo import gradio_llama_demo, train_professor_llama
from tropos.feedback_engine import run_feedback_batch


def main():

    match sys.argv[0]:
        case "run_feedback_batch":

            run_feedback_batch(
                prompt_type="FewShot",
                model="gpt-4o",
                requirements_path="./data/raw/Requirements.docx",
                example_dir="./data/raw",
                target_dir="./data/unmarked_raw",
                output_dir="./data/generated_output",
                verbose=True,
            )
        case "train_professor_llama":
            train_professor_llama()
        case "professor_llama_demo":
            gradio_llama_demo()
        case "test_feedback_console":
            test_feedback_console()
        case arg:
            print(
                f"Invalid argument:{arg}, expected: 'train_professor_llama', 'run_feedback_batch', 'professor_llama_demo', 'test_feedback_console'"
            )


if __name__ == "__main__":
    main()
