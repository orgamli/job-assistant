import os
from reader import read_cv, read_job_description
from claude_client import tailor_cv, write_cover_letter

def save_output(filename, content):
    path = os.path.join("output", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Saved to {path}")

def main():
    print("=" * 40)
    print("  Welcome to Job Application Assistant")
    print("=" * 40)

    # Step 1 - Read CV
    cv_path = input("\nEnter the path to your CV (.pdf or .txt): ").strip()
    
    try:
        cv_text = read_cv(cv_path)
        print("✅ CV loaded successfully!")
    except Exception as e:
        print(f"❌ Error reading CV: {e}")
        return

    # Step 2 - Read Job Description
    job_description = read_job_description()
    
    if not job_description:
        print("❌ No job description entered. Exiting.")
        return

    # Step 3 - Generate tailored CV and cover letter
    tailored_cv = tailor_cv(cv_text, job_description)
    cover_letter = write_cover_letter(cv_text, job_description)

    # Step 4 - Save results
    print("\n💾 Saving results...")
    save_output("tailored_cv.txt", tailored_cv)
    save_output("cover_letter.txt", cover_letter)

    print("\n🎉 All done! Check your output/ folder.")
    print("=" * 40)

if __name__ == "__main__":
    main()