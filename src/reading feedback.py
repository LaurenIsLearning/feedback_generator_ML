import openai
import os
import sys
from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from dotenv import load_dotenv

# --- Error Handling for Missing Dependencies ---
try:
    from docx import Document
except ImportError:
    print("Error: Missing required 'python-docx' library. Run:")
    print("pip install python-docx")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: Missing required 'python-dotenv' library. Run:")
    print("pip install python-dotenv")
    sys.exit(1)

# --- Configuration ---
OLD_FOLDER = "old_with_feedback"
NEW_FOLDER = "new_to_generate"
OUTPUT_FOLDER = "generated_feedback"
FEEDBACK_SUFFIX = "_feedback.docx"

# --- Helper Functions ---
def read_docx(file_path):
    """Safely reads .docx files with error handling"""
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except PackageNotFoundError:
        print(f"Error: Corrupt/invalid DOCX file: {file_path}")
        return None

def validate_folders():
    """Ensures required folder structure exists"""
    for folder in [OLD_FOLDER, NEW_FOLDER, OUTPUT_FOLDER]:
        os.makedirs(folder, exist_ok=True)
        if not os.path.isdir(folder):
            print(f"Error: Failed to create required folder: {folder}")
            sys.exit(1)

# --- Core Logic ---
def get_teacher_feedback():
    """Collects feedback examples from old folder"""
    feedback_examples = []
    
    for filename in os.listdir(OLD_FOLDER):
        if not filename.endswith(".docx"):
            continue
            
        if FEEDBACK_SUFFIX in filename:
            content = read_docx(os.path.join(OLD_FOLDER, filename))
            if content:
                feedback_examples.append(content)
            else:
                print(f"Skipped invalid feedback file: {filename}")
    
    if not feedback_examples:
        print("Error: No valid feedback files found in old_with_feedback folder!")
        print(f"Files must end with {FEEDBACK_SUFFIX}")
        sys.exit(1)
        
    return "\n\n".join(feedback_examples)

def generate_feedback(teacher_feedback, student_content):
    """Generates feedback with error handling"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""
                Generate feedback in this exact style:
                {teacher_feedback}
                
                Rules:
                1. 2-3 paragraphs, no bullet points
                2. Start with strengths, then suggestions
                3. Match the tone and structure"""},
                {"role": "user", "content": student_content}
            ],
            temperature=0.4
        )
        return response.choices[0].message['content']
    except openai.error.AuthenticationError:
        print("Error: Invalid OpenAI API key. Check your .env file")
        sys.exit(1)
    except Exception as e:
        print(f"API Error: {str(e)}")
        return None

def main():
    # Initialization
    load_dotenv()
    validate_folders()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: Missing OPENAI_API_KEY in .env file")
        sys.exit(1)
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Get teacher feedback style
    teacher_feedback = get_teacher_feedback()
    
    # Process new student work
    for filename in os.listdir(NEW_FOLDER):
        if not filename.endswith(".docx"):
            continue
            
        student_path = os.path.join(NEW_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, f"feedback_{filename}")
        
        if os.path.exists(output_path):
            print(f"Skipping {filename} - feedback already exists")
            continue
            
        student_content = read_docx(student_path)
        if not student_content:
            print(f"Skipped invalid student file: {filename}")
            continue
            
        feedback = generate_feedback(teacher_feedback, student_content)
        if feedback:
            with open(output_path, "w") as f:
                f.write(feedback)
            print(f"Generated feedback for: {filename}")

if __name__ == "__main__":
    main()