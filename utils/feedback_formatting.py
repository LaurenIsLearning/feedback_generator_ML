import textwrap

#to print for testing into console
def format_feedback_blocks(feedback: str, width=80):
    from termcolor import colored  # optional, for color
    lines = feedback.splitlines()
    in_summary = False
    in_rubric = False
    current_section = ""

    print("📝", "Instructor Feedback\n")

    for line in lines:
        line = line.strip()
        if not line:
            print()
            continue

        if "summary feedback" in line.lower():
            in_summary = True
            in_rubric = False
            print("\n📌 Summary Feedback\n")
            continue

        if "rubric feedback" in line.lower():
            in_rubric = True
            in_summary = False
            print("\n📋 Rubric Feedback by Section\n")
            continue

        # Summary Paragraphs
        if in_summary:
            wrapped = textwrap.fill(line, width=width)
            print(wrapped)
            continue

        # Rubric Sections
        if in_rubric:
            if line.startswith("==") and line.endswith("=="):
                current_section = line.strip("=")
                print(f"\n🔸 {current_section.strip()} 🔸")
            elif line.startswith("- "):
                print("  •", textwrap.fill(line[2:], width=width))
            else:
                print(textwrap.fill(line, width=width))
            continue

        # Inline Feedback
        if line.startswith("- "):
            parts = line[2:].split('"', 2)
            if len(parts) >= 3:
                quoted = parts[1].strip()
                comment = parts[2].strip(" -:")
                print(textwrap.fill(f'🗨️  "{quoted}"\n👉 {comment}', width=width))
            else:
                print(textwrap.fill(f"👉 {line[2:]}", width=width))
        else:
            print(textwrap.fill(line, width=width))
