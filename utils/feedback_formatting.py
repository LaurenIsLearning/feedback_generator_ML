import textwrap

def format_feedback_blocks(feedback: str, width=80):
    from termcolor import colored  # optional, for color
    lines = feedback.splitlines()
    in_summary = False

    print("📝", "Instructor Feedback\n")

    for line in lines:
        line = line.strip()
        if not line:
            print()
            continue

        if "summary feedback" in line.lower():
            in_summary = True
            print("\n📌 Summary Feedback\n")
            continue

        if in_summary:
            wrapped = textwrap.fill(line, width=width)
            print(wrapped)
        else:
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
