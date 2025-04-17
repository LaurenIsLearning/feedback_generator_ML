import os
from tropos import StudentSubmission

def load_student_submissions(raw_dir, requirements_path, limit=None):
    """Load student submissions dynamically based on available folders and DOCX files."""
    submissions = []
    student_folders = sorted([
        f for f in os.listdir(raw_dir)
        if os.path.isdir(os.path.join(raw_dir, f)) and f.lower().startswith("student_")
    ])
    for student in student_folders[:limit]:  # limit can be None or integer
        folder = os.path.join(raw_dir, student)
        for fname in sorted(os.listdir(folder)):
            if fname.endswith(".docx") and "part" in fname.lower():  # exclude Final if desired
                full_path = os.path.join(folder, fname)
                try:
                    sub = StudentSubmission(full_path, requirements_path)
                    submissions.append(sub)
                except Exception as e:
                    print(f"Skipping {fname} due to error: {e}")
    return submissions


def load_targets(unmarked_raw_dir, requirements_path, limit=None):
    """Load target (uncommented) student submissions."""
    targets = []
    files = sorted([
        f for f in os.listdir(unmarked_raw_dir)
        if f.endswith(".docx")
    ])
    for fname in files[:limit]:
        try:
            sub = StudentSubmission(os.path.join(unmarked_raw_dir, fname), requirements_path)
            student_name = fname.replace("Uncommented_", "").replace(".docx", "")
            targets.append((student_name, sub))
        except Exception as e:
            print(f"Failed loading target {fname}: {e}")
    return targets
