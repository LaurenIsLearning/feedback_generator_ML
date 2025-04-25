# main function to test local/notebook setup
from tropos.models.tuned_llama.demo import gradio_llama_demo, test_professor_llama


def main():
    # run_feedback_batch(
    #     prompt_type="FewShot",
    #     model="gpt-4o",
    #     requirements_path="./data/raw/Requirements.docx",
    #     example_dir="./data/raw",
    #     target_dir="./data/unmarked_raw",
    #     output_dir="./data/generated_output",
    #     verbose=True
    # )
    # test_professor_llama()
    gradio_llama_demo()


if __name__ == "__main__":
    main()
