def format_feedback_blocks(feedback: str):
    lines = feedback.splitlines()
    in_summary = False

    print("🧑‍🏫 𝗜𝗻𝘀𝘁𝗿𝘂𝗰𝘁𝗼𝗿 𝗙𝗲𝗲𝗱𝗯𝗮𝗰𝗸\n")

    for line in lines:
        line = line.strip()
        if not line:
            print()
            continue

        if "summary feedback" in line.lower():
            in_summary = True
            print("📝 𝗦𝘂𝗺𝗺𝗮𝗿𝘆 𝗙𝗲𝗲𝗱𝗯𝗮𝗰𝗸\n")
            continue

        if in_summary:
            print(f"   {line}")
        else:
            if line.startswith("- "):
                quoted, comment = line[2:].split('"', 2)[1], line[2:].split('"', 2)[2]
                print(f'🔹 "{quoted.strip()}"\n   👉 {comment.strip()}\n')
            else:
                print(f"   {line}")

format_feedback_blocks(feedback)