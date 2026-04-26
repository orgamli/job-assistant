import pypdf
import os

def read_cv(file_path):
    if file_path.endswith(".pdf"):
        reader = pypdf.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type. Use a .pdf or .txt file.")

def read_job_description():
    print("\nPaste the job description below.")
    print("When you're done, press Enter twice:\n")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)