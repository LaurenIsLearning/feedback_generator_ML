# simple_blocks_ui.py

import gradio as gr

def greet(name):
    return f"Hello, {name}!"

with gr.Blocks() as demo:
    gr.Markdown("### 👋 Welcome to the Gradio Demo!")
    name = gr.Textbox(label="Enter your name")
    output = gr.Textbox(label="Greeting")
    greet_btn = gr.Button("Greet Me")

    greet_btn.click(fn=greet, inputs=name, outputs=output)

if __name__ == "__main__":
    demo.launch(share=True)
