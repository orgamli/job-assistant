import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-6"


def tailor_cv(cv_text, job_description):
    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system="You are an expert CV writer with years of experience helping people land jobs. "
               "Your task is to rewrite CVs to better match job descriptions while keeping all information truthful.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Here is my current CV:\n{cv_text}\n\nHere is the job description I am applying for:\n{job_description}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": "Please rewrite my CV to better match this job description. "
                                "Highlight relevant skills and experience. Keep everything truthful. "
                                "Format it cleanly and professionally.",
                    },
                ],
            }
        ],
    )
    return message.content[0].text


def write_cover_letter(cv_text, job_description):
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="You are an expert cover letter writer. You write compelling, "
               "personalized cover letters that get people interviews.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Based on this CV:\n{cv_text}\n\nAnd this job description:\n{job_description}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": "Write a professional and compelling cover letter for this application. "
                                "Keep it to 3-4 paragraphs. Be specific and enthusiastic.",
                    },
                ],
            }
        ],
    )
    return message.content[0].text


def get_match_score(cv_text, job_description):
    message = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system="You are an expert recruiter who objectively evaluates CV-to-job-description fit.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"CV:\n{cv_text}\n\nJob description:\n{job_description}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": (
                            "Evaluate the match between this CV and job description. "
                            "Respond ONLY with valid JSON in this exact shape:\n"
                            '{"score": <int 0-100>, "strengths": ["...", "...", "..."], "gaps": ["...", "...", "..."]}'
                        ),
                    },
                ],
            }
        ],
    )
    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def get_position_suggestions(cv_text, job_description):
    message = client.messages.create(
        model=MODEL,
        max_tokens=768,
        system="You are a career coach who identifies the best-fit roles for candidates.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"CV:\n{cv_text}\n\nTarget job description:\n{job_description}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": (
                            "Based on this candidate's background, suggest 3 alternative job positions "
                            "that would be a strong or equal fit. "
                            "Respond ONLY with valid JSON as a list of 3 objects, each with keys: "
                            '"title", "why_it_fits", "where_to_look".'
                        ),
                    },
                ],
            }
        ],
    )
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def refine_cv(current_cv, job_description, refinement_request):
    """Refine only the current CV version; cv + job description are cached."""
    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system="You are an expert CV writer. You refine CVs based on specific user instructions "
               "while keeping all content truthful.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Current CV:\n{current_cv}\n\nOriginal job description:\n{job_description}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": f"Please apply the following refinement to the CV: {refinement_request}\n"
                                "Return only the full updated CV text, no commentary.",
                    },
                ],
            }
        ],
    )
    return message.content[0].text
