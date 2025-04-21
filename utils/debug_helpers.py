from docx import Document
from tropos.preprocess_docx.assignment_requirements import parse_requirements
from utils.student_loader import load_all_student_examples_recursive

# helped to see what all was getting picked up for prompts
#DEBUG
def explore_examples(requirements_path, example_dir):

        print("\n📌 Assignment Requirements:\n")
        parsed_req = parse_requirements(requirements_path)
        print(parsed_req.get_instructions())

        examples = load_all_student_examples_recursive(example_dir, requirements_path)

        print(f"\n📋 Clean Rubric:\n{examples[0].rubric.format_clean_only()}\n")

        for i, example in enumerate(examples):
            print(f"\n🔍 Example {i+1}: {example.submission_path}")

            print("\n📝 Submission Text:\n")
            print(example.get_submission_text()[:1000])  # prevent flooding output

            print("\n💬 Inline Feedback:\n")
            print(example.get_comments_text() or "[No comments in paper]")

            print("\n📋 Rubric Feedback:\n")
            print(example.get_rubric_feedback() or "[No rubric feedback found]")

            print("\n" + "-"*80)