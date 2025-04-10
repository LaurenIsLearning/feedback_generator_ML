from typing import List
from tropos.models.gpt import generate_inline_feedback, generate_summary_feedback
import gradio as gr
from tropos.io_fields import InputFields, OutputFields
from tropos.feedback_docx import FeedbackDocxGenerator  # <-- New import
import json
import os
from pathlib import Path

# Custom CSS for styling 
css_styling = """
... [same as your original CSS] ...
"""

class GradioSystem:
    def __init__(self):
        self.doc_gen = FeedbackDocxGenerator()
        self.processed_dir = "feedback_reports"
        Path(self.processed_dir).mkdir(exist_ok=True)
        
    def reset_interface(self):
        return (
            gr.update(value="", visible=True),
            gr.update(value="", visible=True),
            gr.update(value="", visible=True),
            gr.update(value="", visible=True),
            gr.update(value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(visible=False),
            gr.update(visible=False)  # Add docx download
        )

    def _generate_feedback_data(self, input_data):
        """Simulates AI feedback generation with test data structure"""
        return {
            "rubric": {
                "criteria": [
                    {
                        "id": 1,
                        "description": "Thesis Clarity",
                        "score": 4,
                        "max_score": 5,
                        "feedback": "Clear thesis but could be more specific"
                    }
                ]
            },
            "inline": [
                {
                    "page": 1,
                    "text": "The introduction needs a stronger hook",
                    "suggestion": "Consider starting with a relevant quote"
                }
            ],
            "overall": "Good effort overall. Needs more supporting evidence."
        }

    def submit_button_updates(self, essay, requirements, student_id, assignment_id):
        input_data = (
            InputFields()
            .add_student_id(student_id)
            .add_assignment_id(assignment_id)
            .add_requirements_input(requirements)
            .add_student_essay(essay)
        )

        # Generate feedback data (replace with your actual AI call)
        feedback_data = self._generate_feedback_data(input_data)
        
        # Generate DOCX report
        output_path = os.path.join(self.processed_dir, f"{student_id}_{assignment_id}_feedback.docx")
        self.doc_gen.create_document(
            output_path=output_path,
            rubric_data=feedback_data["rubric"],
            inline_comments=feedback_data["inline"],
            overall_feedback=feedback_data["overall"]
        )

        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(value=feedback_data["overall"], visible=True, lines=10),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(value=output_path, visible=True)  # Show download
        )

    def show_inline_feedback(self, essay, requirements, student_id, assignment_id):
        input_data = (
            InputFields()
            .add_student_id(student_id)
            .add_assignment_id(assignment_id)
            .add_requirements_input(requirements)
            .add_student_essay(essay)
        )

        # Generate test inline feedback
        feedback_data = self._generate_feedback_data(input_data)
        
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True, lines=3),
            *[
                gr.update(value=comment["text"], visible=True, lines=3)
                for comment in feedback_data["inline"]
            ],
            gr.update(visible=True),
            gr.update(visible=True)
        )

    def create_interface(self):
        with gr.Blocks(css=css_styling) as demo:
            gr.Markdown("# 📝 Tropos Essay Grader")
            
            # Input Section
            question_textbox = gr.Textbox(label="Input Essay Contents Here:", lines=10)
            requirements_input = gr.Textbox(label="Rubric/Requirements:", lines=3)
            
            with gr.Row():
                student_id_textbox = gr.Textbox(label="Student ID:")
                assignment_id_textbox = gr.Textbox(label="Assignment ID:")

            # Action Buttons
            with gr.Row():
                submit_btn = gr.Button("📤 Submit Essay", variant="primary")
                reset_btn = gr.Button("🔄 Reset", variant="secondary")

            # Feedback Section
            feedback_textbox = gr.Textbox(label="Overall Feedback", visible=False)
            download_btn = gr.File(label="Download DOCX Report", visible=False)
            
            # Inline Feedback
            inline_btn = gr.Button("Show Inline Comments", visible=False)
            with gr.Row():
                inline_boxes = [
                    gr.Textbox(label=f"Inline Comment {i+1}", visible=False)
                    for i in range(3)
                ]

            # Event Handlers
            submit_btn.click(
                self.submit_button_updates,
                inputs=[question_textbox, requirements_input, student_id_textbox, assignment_id_textbox],
                outputs=[question_textbox, requirements_input, student_id_textbox, assignment_id_textbox,
                        feedback_textbox, *inline_boxes, inline_btn, download_btn]
            )

            reset_btn.click(
                self.reset_interface,
                inputs=[],
                outputs=[question_textbox, requirements_input, student_id_textbox, assignment_id_textbox,
                        feedback_textbox, *inline_boxes, inline_btn, download_btn]
            )

            inline_btn.click(
                self.show_inline_feedback,
                inputs=[question_textbox, requirements_input, student_id_textbox, assignment_id_textbox],
                outputs=[question_textbox, requirements_input, student_id_textbox, assignment_id_textbox,
                        feedback_textbox, *inline_boxes, inline_btn, download_btn]
            )

        return demo

# Launch function
def launch_interface():
    system = GradioSystem()
    demo = system.create_interface()
    demo.launch(debug=True, share=True)

if __name__ == "__main__":
    launch_interface()