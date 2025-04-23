import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("### Tropos - Feedback Generator")

    with gr.Row():
        # LEFT COLUMN 
        with gr.Column(scale=1):
            # Uploads Accordion
            with gr.Accordion("Uploads", open=True):
                gr.Button("Requirements", size="sm")
                gr.Button("Upload Rubric", size="sm")
                with gr.Group():
                    submission_upload = gr.File(
                        label="Upload Submissions", 
                        file_types=[".docx"], 
                        file_count="multiple",
                        height=100  
                    )
                    with gr.Row():
                        gr.Column(scale=8)
                        with gr.Column(scale=2):
                            gr.Button("Submission", size="sm")
            
            # Edit Accordion
            with gr.Accordion("Edit", open=True):
                gr.Dropdown(
                    ["Student Submission 1", "Student Submission 2", "Student Submission 3"], 
                    label="Select Student Submission"
                )
                with gr.Row():
                    gr.Button("Edit Feedback", size="sm")
                    gr.Button("Save Feedback", size="sm")
                with gr.Row():
                    gr.Button("Download Current", size="sm")
                    gr.Button("Download All", size="sm")
            
            # Model Accordion
            with gr.Accordion("Model", open=True):
                gr.Dropdown(["Model A", "Model B"], label="Model Choice")
                gr.Button("Edit Prompt", size="sm")
                gr.Button("Clear Model History", size="sm")
            
            # Bottom buttons
            with gr.Row():
                gr.Button("Clear Current Work", size="sm")
                gr.Button("Edit Viewed Document", size="sm")

        # RIGHT COLUMN
        with gr.Column(scale=3):
            with gr.Row():
                gr.Button("Zoom In", size="sm")
                gr.Button("Zoom Out", size="sm")
            
            gr.Textbox(
                label="Document Viewer",
                lines=26,
                interactive=True,
                show_copy_button=True
            )
                
            with gr.Row():
                gr.Column(scale=8)
                with gr.Column(scale=2):
                    gr.Button("Clear ALL", variant="stop", size="sm")

if __name__ == "__main__":
    demo.launch(share=True, height=900)
