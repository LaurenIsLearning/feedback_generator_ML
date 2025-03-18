

# #install gradio
# !pip install gradio
# !pip install langchain_openai
# !pip install gradio_client
# !pip install openai
#
from typing import List
import tropos
import gradio as gr
import shared


# Custom CSS for styling
css_styling = """
h1 {
    font-family: 'Helvetica', sans-serif;
    color: #4CAF50;
    text-align: center;
}
.gradio-container {
    font-family: 'Helvetica', sans-serif;
    text-align: center;
}
.gradio-textbox {
    font-family: 'Helvetica', sans-serif;
    text-align: center;
    font-size: 16px;
}
.gradio-button {
    font-family: 'Helvetica', sans-serif;
    text-align: center;
    font-size: 16px;
    background-color: #4CAF50;
    color: white;
}
.gradio-button:hover {
    background-color: #45a049;
    color: orange;
}
.gradio-button:active {
    background-color: #3e8e3c;
    color: white;
}
.hidden {
    display: none;
}
.expanded {
    height: 300px !important;
}
"""


def reset_interface():
    return (
        gr.update(value="", visible=True),  # essay textbox
        gr.update(value="", visible=True),  # requirements
        gr.update(value="", visible=True),  # student ID
        gr.update(value="", visible=True),  # assignment ID
        gr.update(value="", visible=False),  # feedback
        gr.update(value="", visible=False),  # inline feedback 1
        gr.update(value="", visible=False),  # inline feedback 2
        gr.update(value="", visible=False),  # inline feedback 3
        gr.update(visible=False),
    )


def submit_button_updates(essay, requirements, student_id, assignment_id):
    input_data = (
        shared.InputFields()
        .add_student_id(student_id)
        .add_assignment_id(assignment_id)
        .add_requirements_input(requirements)
        .add_student_essay(essay)
    )

    output_data = tropos.generate_summary_feedback(input_data)  # feedback

    return (
        gr.update(visible=False),  # essay input
        gr.update(visible=False),  # rubric/requirements
        gr.update(visible=False),  # student ID
        gr.update(visible=False),  # assignment ID
        gr.update(value=output_data.__str__().replace("**",""), visible=True, lines=10),  # feedback
        gr.update(visible=False),  # inline feedback 1
        gr.update(visible=False),  # inline feedback 2
        gr.update(visible=False),  # inline feedback 3
        gr.update(visible=True),  # inline button
    )


def show_inline_feedback(essay, requirements, student_id, assignment_id):
    input_data = (
        shared.InputFields()
        .add_student_id(student_id)
        .add_assignment_id(assignment_id)
        .add_requirements_input(requirements)
        .add_student_essay(essay)
    )

    output_data: List[shared.OutputFields] = tropos.generate_inline_feedback(
        input_data
    )  # feedback

    return (
        gr.update(visible=False),  # essay input
        gr.update(visible=False),  # rubric/requirements
        gr.update(visible=False),  # student ID
        gr.update(visible=False),  # assignment ID
        # This needs to be changed to support an array as an output
        gr.update(visible=True, lines=3),  # feedback
        *[
            gr.update(value=inline.__str__(), visible=True, lines=3)
            for inline in output_data
        ],
        gr.update(visible=True),  # inline button
    )


def make_ui():
    with gr.Blocks(css=css_styling) as demo:

        gr.Markdown("# 📝 Tropos Essay Grader")
        question_textbox = gr.Textbox(
            label="Input Essay Contents Here: ", interactive=True, value="", lines=10
        )
        requirements_input = gr.Textbox(
            label="Rubric / Requirements: ", interactive=True, value="", lines=3
        )

        with gr.Row():
            student_id_textbox = gr.Textbox(
                label="Student ID: ", interactive=True, value="", lines=1
            )
            assignment_id_textbox = gr.Textbox(
                label="Assignment ID: ", interactive=True, value="", lines=1
            )

        with gr.Row():
            sent_button = gr.Button(value="📤 Submit Essay", variant="primary")
            reset_button = gr.Button(value="🔄 Reset", variant="secondary")

        feedback_textbox = gr.Textbox(
            label="Essay Feedback", interactive=False, value="", lines=5, visible=False
        )
        inline_button = gr.Button(
            value="Get Inline Feedback", variant="primary", visible=False
        )

        with gr.Row():
            inline_textbox1 = gr.Textbox(
                label="Inline Feedback",
                interactive=False,
                value="",
                lines=3,
                visible=False,
            )
            inline_textbox2 = gr.Textbox(
                label="Inline Feedback",
                interactive=False,
                value="",
                lines=3,
                visible=False,
            )
            inline_textbox3 = gr.Textbox(
                label="Inline Feedback",
                interactive=False,
                value="",
                lines=3,
                visible=False,
            )

        sent_button.click(
            submit_button_updates,
            inputs=[
                question_textbox,
                requirements_input,
                student_id_textbox,
                assignment_id_textbox,
            ],
            outputs=[
                question_textbox,
                requirements_input,
                student_id_textbox,
                assignment_id_textbox,
                feedback_textbox,
                inline_textbox1,
                inline_textbox2,
                inline_textbox3,
                inline_button,
            ],
        )

        reset_button.click(
            reset_interface,
            inputs=[],  # clear inputs
            outputs=[
                question_textbox,
                requirements_input,
                student_id_textbox,
                assignment_id_textbox,
                feedback_textbox,
                inline_textbox1,
                inline_textbox2,
                inline_textbox3,
                inline_button,
            ],
        )
        inline_button.click(
            show_inline_feedback,
            inputs=[
                question_textbox,
                requirements_input,
                student_id_textbox,
                assignment_id_textbox,
            ],
            outputs=[
                question_textbox,
                requirements_input,
                student_id_textbox,
                assignment_id_textbox,
                feedback_textbox,
                inline_textbox1,
                inline_textbox2,
                inline_textbox3,
                inline_button,
            ],
        )
    # Launch the interface
    demo.launch(debug=True, share=True)
