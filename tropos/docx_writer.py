def build_fewshot_prompt(examples: list, target: StudentSubmission) -> str:
    """
    Constructs a few-shot prompt for the GPT API using examples and a new student submission.
    
    Format includes:
    - Assignment requirements (once)
    - Clean rubric (once)
    - Multiple examples interated (submission, inline comments, rubric feedback)
    - Target essay (no feedback or rubric yet)
    - Feedback format instructions
    """
    
    # header section (requirements and clean rubric)
    prompt_parts = [
      "You are a college writing professor providing feedback on student papers.",
      "\n--- ASSIGNMENT REQUIREMENTS ---",
      target.get_requirements_text(),
      "\n--- RUBRIC ---",
      target.get_clean_rubric()
    ]
    
    # fewshot examples
    for ex in examples:
        submission_name = os.path.basename(ex.submission_path).replace(".docx", "")
        submission_text = ex.get_submission_text()
        comments_text = ex.get_comments_text()
        rubric_feedback = ex.get_rubric_feedback()

        # Warn if any example is missing submission text
        if not submission_text.strip():
             print(f"[WARNING] Example '{submission_name}' has empty submission text.")

        prompt_parts.append(f"""
          --- EXAMPLE ESSAY ({submission_name}) ---
          {submission_text or '[NO SUBMISSION TEXT]'}

          --- INSTRUCTOR FEEDBACK ---
          {comments_text or '[No comments for paper]'}

          --- RUBRIC FEEDBACK ---
          {rubric_feedback or '[No rubric feedback for paper]'}
          """)

    #--- target essay--
    prompt_parts.append("-----")
    prompt_parts.append("\n--- SUBMITTED ESSAY ---")
    prompt_parts.append(target.get_submission_text())

    # Format instructions (match docx_writer.py)
    prompt_parts.append("""
    --- FORMAT INSTRUCTIONS (IMPORTANT) ---

    Please return your response in THREE SECTIONS using these exact headers and formats:

    --- INLINE FEEDBACK (AT LEAST 4 REQUIRED) ---
    (AT LEAST 4 REQUIRED) Provide **at least 4 but no more than 8** comments and MUST use this format:
    - "Quoted student sentence" - Your feedback here.

    Focus your inline feedback on moments where:
    - A sentence could be clarified or rewritten
    - Tone, evidence, or phrasing need revision
    - Claims are unsupported or overly strong

    --- SUMMARY FEEDBACK ---
    Write 2–3 paragraphs of praise and constructive suggestions.

    
    --- RUBRIC FEEDBACK ---
    Only include rubric sections where you have specific praise or concerns. **Limit your comments to 1–2 project portions**.

    Rubric Format:
    == [Project Portion] ==
    - Feedback comment 1
    - Feedback comment 2

    Do NOT use Markdown (no bold, italics, headers), emojis, or numbered lists.
    """)

    return "\n".join(prompt_parts)
