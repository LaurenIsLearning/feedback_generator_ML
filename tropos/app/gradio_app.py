from typing import List
from tropos.models.gpt import generate_inline_feedback, generate_summary_feedback
import gradio as gr
from tropos.io_fields import InputFields, OutputFields
from tropos.feedback_docx import FeedbackDocxGenerator 
import json
import os
from pathlib import Path
import zipfile
import tempfile
# gr 
# In-memory storage
feedback_storage = {}
upload_data = {
    "rubric": None,
    "submissions": [],
    "past_assignments": []
}
zoom_level = {"size": 14}


def save_feedback(student_name, text):
    if student_name:
        feedback_storage[student_name] = text
    return text

def load_feedback(student_name):
    return feedback_storage.get(student_name, "")

def download_current(student_name):
    if student_name and student_name in feedback_storage:
        content = feedback_storage[student_name]
        file_path = os.path.join(tempfile.gettempdir(), f"{student_name}_feedback.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path
    return None

def download_all():
    if not feedback_storage:
        return None
    zip_path = os.path.join(tempfile.gettempdir(), "all_feedback.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for student, feedback in feedback_storage.items():
            file_name = f"{student}_feedback.txt"
            temp_path = os.path.join(tempfile.gettempdir(), file_name)
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(feedback)
            zipf.write(temp_path, arcname=file_name)
    return zip_path

def zoom_in(textbox_value):
    zoom_level["size"] = min(40, zoom_level["size"] + 2)
    return gr.update(value=textbox_value, style={"font_size": f"{zoom_level['size']}px"})

def zoom_out(textbox_value):
    zoom_level["size"] = max(8, zoom_level["size"] - 2)
    return gr.update(value=textbox_value, style={"font_size": f"{zoom_level['size']}px"})

def reset_all():
    feedback_storage.clear()
    upload_data["rubric"] = None
    upload_data["submissions"] = []
    upload_data["past_assignments"] = []
    zoom_level["size"] = 14
    return "", gr.update(choices=[], value=None), "", gr.update(value="", style={"font_size": "14px"}), None, None, None

def clear_current():
    return "", gr.update(value="", style={"font_size": f"{zoom_level['size']}px"})

def edit_prompt_fn(prompt_text):
    return f"Prompt updated: {prompt_text}"

def edit_feedback_fn(current_text):
    return current_text + "\n\n[Edited]"

def handle_uploads(rubric_file, submissions_files, past_assignments_files):
    upload_data["rubric"] = rubric_file.name if rubric_file else None
    upload_data["submissions"] = [f.name for f in submissions_files] if submissions_files else []
    upload_data["past_assignments"] = [f.name for f in past_assignments_files] if past_assignments_files else []
    status = f"Rubric: {upload_data['rubric']}\nSubmissions: {', '.join(upload_data['submissions'])}\nPast Assignments: {', '.join(upload_data['past_assignments'])}"
    return status


def generate_feedback(student_name, model_choice):
    return f"Generated feedback for {student_name} using {model_choice}"

def clear_model_history():
    return "Model history cleared."

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            rubric_upload = gr.File(label="Upload Rubric", file_types=[".pdf", ".docx"])
            submission_upload = gr.File(label="Upload Submissions", file_types=[".docx"], file_count="multiple")
            past_upload = gr.File(label="Upload Past Assignments", file_types=[".docx"], file_count="multiple")
            upload_status = gr.Textbox(label="Upload Status", interactive=False)

            upload_btn = gr.Button("Process Uploads")
            upload_btn.click(
                fn=handle_uploads,
                inputs=[rubric_upload, submission_upload, past_upload],
                outputs=upload_status
            )

            generate_btn = gr.Button("Generate Feedback")
            generate_btn.click(generate_feedback, inputs=[gr.Textbox(visible=False), gr.Dropdown(visible=False)], outputs=None)

            edit_feedback_btn = gr.Button("Edit Feedback")
            save_btn = gr.Button("Save Feedback")
            download_current_btn = gr.Button("Download Current")
            download_all_btn = gr.Button("Download All")
            edit_prompt_box = gr.Textbox(label="Edit Prompt")
            edit_prompt_btn = gr.Button("Apply Prompt Edit")
            clear_history_btn = gr.Button("Clear Model History")
            clear_history_btn.click(clear_model_history, outputs=None)

            model_choice = gr.Dropdown(["Model A", "Model B"], label="Model Choice")
            student_dropdown = gr.Dropdown(label="Student History", choices=["Student 1", "Student 2"], value="Student 1")

        with gr.Column(scale=3):
            feedback_box = gr.Textbox(
                label="Document Viewer / Editor",
                lines=25,
                interactive=True,
                show_copy_button=True,
                style={"font_size": "14px"},
            )
            with gr.Row():
                gr.Button("Zoom In").click(zoom_in, inputs=feedback_box, outputs=feedback_box)
                gr.Button("Zoom Out").click(zoom_out, inputs=feedback_box, outputs=feedback_box)
                clear_current_btn = gr.Button("Clear Current Work")
                clear_current_btn.click(fn=clear_current, outputs=[feedback_box, feedback_box])

    with gr.Row():
        clear_all = gr.Button("Clear ALL Data")
        clear_all.click(
            fn=reset_all,
            outputs=[
                student_dropdown, student_dropdown,
                model_choice, feedback_box,
                rubric_upload, submission_upload, past_upload
            ]
        )

    student_dropdown.change(fn=load_feedback, inputs=student_dropdown, outputs=feedback_box)
    save_btn.click(fn=save_feedback, inputs=[student_dropdown, feedback_box], outputs=feedback_box)
    download_current_btn.click(fn=download_current, inputs=student_dropdown, outputs=gr.File())
    download_all_btn.click(fn=download_all, outputs=gr.File())
    edit_prompt_btn.click(fn=edit_prompt_fn, inputs=edit_prompt_box, outputs=edit_prompt_box)
    edit_feedback_btn.click(fn=edit_feedback_fn, inputs=feedback_box, outputs=feedback_box)

demo.launch()