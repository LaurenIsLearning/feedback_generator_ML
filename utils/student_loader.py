import os
from tropos.preprocess_docx import StudentSubmission


def load_all_student_examples_recursive(
    base_dir, requirements_path, valid_ext=".docx", verbose=False
):
    """
    Recursively load all student submissions from a directory and its subdirectories.
    """
    submissions = []
    for root, dirs, files in os.walk(base_dir):
        for fname in sorted(files):
            if fname.startswith(".~"):
                continue
            if fname.lower().endswith(valid_ext):
                full_path = os.path.join(root, fname)
                try:
                    # Silencing prints from inside StudentSubmission
                    with contextlib.redirect_stdout(io.StringIO()):
                        sub = StudentSubmission(full_path, requirements_path)
                    submissions.append(sub)
                    if verbose:
                        print(f"✅ Loaded example: {full_path}")
                except Exception as e:
                    if verbose:
                        print(f"❌ Failed to parse {full_path}: {e}")
    return submissions


def load_all_targets_recursive(
    unmarked_dir, requirements_path, valid_ext=".docx", verbose=False
):
    """
    Recursively load all target (uncommented) student submissions.

    Parameters:
    - unmarked_dir: Root directory to search for .docx files
    - requirements_path: Path to the assignment requirements
    - valid_ext: File extension to load (default: .docx)

    Returns:
    - List of (student_name, StudentSubmission) tuples
    """
    targets = []
    for root, dirs, files in os.walk(unmarked_dir):
        for fname in sorted(files):
            if fname.lower().endswith(valid_ext):
                full_path = os.path.join(root, fname)
                try:
                    sub = StudentSubmission(full_path, requirements_path)
                    student_name = os.path.splitext(fname)[0].replace(
                        "Uncommented_", ""
                    )
                    targets.append((student_name, sub))
                    if verbose:
                        print(f"✅ Loaded target: {full_path}")
                except Exception as e:
                    print(f"❌ Failed to load target {full_path}: {e}")
    return targets

