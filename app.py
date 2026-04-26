import io
import os
import tempfile

import streamlit as st

from docx_exporter import build_docx_from_pdf_template
from reader import read_cv
from claude_client import (
    tailor_cv,
    write_cover_letter,
    get_match_score,
    get_position_suggestions,
    refine_cv,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Job Application Assistant", page_icon="💼", layout="wide")
st.title("💼 Job Application Assistant")

with st.sidebar:
    st.header("Instructions")
    st.markdown(
        "1. Upload your CV (PDF or TXT)\n"
        "2. Paste the job description\n"
        "3. Click **Generate**\n"
        "4. Refine your CV with chat\n"
        "5. Download results"
    )

# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "cv_versions": [],      # list of CV strings, oldest → newest
    "cover_letter": "",
    "job_description": "",
    "cv_text_raw": "",      # original extracted CV text
    "generated": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Helper: current CV ────────────────────────────────────────────────────────
def current_cv():
    return st.session_state.cv_versions[-1] if st.session_state.cv_versions else ""


# ── Input section ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.subheader("Your CV")
    uploaded_file = st.file_uploader("Upload CV", type=["pdf", "txt"], label_visibility="collapsed")
with col2:
    st.subheader("Job Description")
    job_description_input = st.text_area(
        "Paste the job description here", height=300, label_visibility="collapsed"
    )

st.divider()
generate = st.button("✨ Generate Application", type="primary", use_container_width=True)

# ── Generate ──────────────────────────────────────────────────────────────────
if generate:
    if not uploaded_file:
        st.error("Please upload your CV.")
        st.stop()
    if not job_description_input.strip():
        st.error("Please enter a job description.")
        st.stop()

    suffix = ".pdf" if uploaded_file.name.endswith(".pdf") else ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        cv_text_raw = read_cv(tmp_path)
    except Exception as e:
        st.error(f"Could not read CV: {e}")
        st.stop()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    with st.spinner("Analysing match score..."):
        try:
            match = get_match_score(cv_text_raw, job_description_input)
        except Exception as e:
            st.warning(f"Match score unavailable: {e}")
            match = None

    with st.spinner("Finding alternative positions..."):
        try:
            suggestions = get_position_suggestions(cv_text_raw, job_description_input)
        except Exception as e:
            st.warning(f"Position suggestions unavailable: {e}")
            suggestions = []

    with st.spinner("Tailoring your CV..."):
        try:
            tailored = tailor_cv(cv_text_raw, job_description_input)
        except Exception as e:
            st.error(f"CV tailoring failed: {e}")
            st.stop()

    with st.spinner("Writing your cover letter..."):
        try:
            cover = write_cover_letter(cv_text_raw, job_description_input)
        except Exception as e:
            st.error(f"Cover letter generation failed: {e}")
            st.stop()

    # Persist to session state
    st.session_state.cv_versions = [tailored]
    st.session_state.cover_letter = cover
    st.session_state.job_description = job_description_input
    st.session_state.cv_text_raw = cv_text_raw
    st.session_state.generated = True
    st.session_state["_match"] = match
    st.session_state["_suggestions"] = suggestions

    st.success("Done! Your application is ready.")

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.generated:
    match = st.session_state.get("_match")
    suggestions = st.session_state.get("_suggestions", [])

    # ── 1. Match Score ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Match Score")
    if match:
        score_col, details_col = st.columns([1, 3])
        with score_col:
            st.markdown(
                f"<div style='font-size:80px;font-weight:bold;text-align:center;'>{match['score']}</div>"
                "<div style='text-align:center;color:gray;'>out of 100</div>",
                unsafe_allow_html=True,
            )
        with details_col:
            str_col, gap_col = st.columns(2)
            with str_col:
                st.markdown("**Strengths**")
                for s in match.get("strengths", []):
                    st.markdown(f"- {s}")
            with gap_col:
                st.markdown("**Gaps**")
                for g in match.get("gaps", []):
                    st.markdown(f"- {g}")

    # ── 2. Position Suggestions ───────────────────────────────────────────────
    if suggestions:
        st.divider()
        st.subheader("🔍 Alternative Position Suggestions")
        sug_cols = st.columns(len(suggestions))
        for col, sug in zip(sug_cols, suggestions):
            with col:
                st.markdown(f"**{sug.get('title', '')}**")
                st.markdown(sug.get("why_it_fits", ""))
                st.caption(f"Where to look: {sug.get('where_to_look', '')}")

    # ── 3. CV + Cover Letter ──────────────────────────────────────────────────
    st.divider()
    cv_col, cl_col = st.columns(2)

    version_num = len(st.session_state.cv_versions)
    cv_label = f"Version {version_num}" + (" — click Undo to go back" if version_num > 1 else "")

    with cv_col:
        st.subheader("Tailored CV")
        st.caption(cv_label)
        st.text_area("", value=current_cv(), height=500, key="cv_display", label_visibility="collapsed")
        undo_col, dl_col = st.columns(2)
        with undo_col:
            if version_num > 1:
                if st.button("↩ Undo", use_container_width=True):
                    st.session_state.cv_versions.pop()
                    st.rerun()
        with dl_col:
            st.download_button(
                "⬇ Download CV (.txt)",
                data=current_cv().encode("utf-8"),
                file_name="tailored_cv.txt",
                mime="text/plain",
                use_container_width=True,
            )

    with cl_col:
        st.subheader("Cover Letter")
        st.text_area("", value=st.session_state.cover_letter, height=500, key="cl_display", label_visibility="collapsed")
        st.download_button(
            "⬇ Download Cover Letter (.txt)",
            data=st.session_state.cover_letter.encode("utf-8"),
            file_name="cover_letter.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # ── 4. Word export ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📄 Export to Word")
    try:
        docx_bytes = build_docx_from_pdf_template(current_cv(), st.session_state.cover_letter)
        st.download_button(
            "⬇ Download .docx (CV + Cover Letter)",
            data=docx_bytes,
            file_name="job_application.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Word export failed: {e}")

    # ── 5. Chat refinement ────────────────────────────────────────────────────
    st.divider()
    st.subheader("💬 Refine your CV")
    st.caption('Type a refinement request, e.g. "make it shorter" or "add more emphasis on Python".')

    refinement = st.chat_input("Refinement request...")
    if refinement:
        with st.spinner("Applying refinement..."):
            try:
                new_cv = refine_cv(
                    current_cv(),
                    st.session_state.job_description,
                    refinement,
                )
                st.session_state.cv_versions.append(new_cv)
                st.rerun()
            except Exception as e:
                st.error(f"Refinement failed: {e}")
