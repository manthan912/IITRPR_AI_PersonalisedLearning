# app.py - full corrected file with Pydantic + stale-state fixes
import streamlit as st
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional
import PyPDF2
from io import BytesIO
import os
import time
import json
import pymupdf
import matplotlib.pyplot as plt

# -------------------------
# Gemini API configuration
# -------------------------
api_key = ""
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        model = None
else:
    model = None

# -------------------------
# Pydantic models (unchanged)
# -------------------------
class TeachingMaterial(BaseModel):
    content: str = Field(description="The teaching material for the subtopic")

class Question(BaseModel):
    question: str = Field(description="The MCQ question")
    options: List[str] = Field(description="List of 4 options (A, B, C, D)", min_items=4, max_items=4)
    correct_answer: str = Field(description="The correct option (e.g., 'A')", pattern="^[A-D]$")

class LessonResponse(BaseModel):
    teaching_material: TeachingMaterial
    questions: List[Question] = Field(description="Exactly 2 questions", min_items=2, max_items=2)

class SubtopicsList(BaseModel):
    subtopics: List[str] = Field(description="List of subtopics extracted or suggested", min_items=5, max_items=10)

# -------------------------
# Original functions (kept intact)
# -------------------------
def extract_pdf_text(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            text += page_text
        return text if text.strip() else None
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def generate_subtopics(topic, level, endgoal, pdf_text=None):
    if pdf_text:
        prompt = f"""
        Extract 5-10 main subtopics from the following notes on '{topic}' for {level} level, aiming for {endgoal}.
        Notes: {pdf_text[:4000]}
        Output JSON: {{"subtopics": ["subtopic1", "subtopic2", ...]}}
        """
    else:
        prompt = f"""
        For topic '{topic}' at {level} level, with endgoal '{endgoal}', suggest 5-10 relevant subtopics.
        Output JSON: {{"subtopics": ["subtopic1", "subtopic2", ...]}}
        """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        subtopics_data = json.loads(response.text)
        structured = SubtopicsList(**subtopics_data)
        return structured.subtopics
    except Exception as e:
        st.error(f"Error generating subtopics: {e}")
        return [f"{topic} Subtopic {i+1}" for i in range(5)]

def generate_lesson(subtopic, level, previous_performance=None, time_taken=None):
    previous_performance = previous_performance if previous_performance is not None else 0
    adapt_prompt = ""
    if previous_performance is not None:
        adapt_prompt += f"Previous quiz performance: {previous_performance}/2 correct. "
    if time_taken is not None:
        adapt_prompt += f"Time taken for last lesson: {time_taken:.1f} minutes. "
    style = (
        "Explain in simple terms with clear examples." if previous_performance == 0 or (previous_performance <= 1 and time_taken and time_taken > 5)
        else "Use advanced concepts and challenging examples." if previous_performance == 2 and time_taken and time_taken < 3
        else "Use clear explanations with balanced examples."
    )
    prompt = f"""
    {adapt_prompt}
    Teach about '{subtopic}' for {level} level in an engaging way, {style}.
    Output JSON:
    {{
        "teaching_material": {{"content": "Detailed teaching content"}},
        "questions": [
            {{
                "question": "Question text?",
                "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                "correct_answer": "A"
            }},
            {{
                "question": "Second question text?",
                "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
                "correct_answer": "B"
            }}
        ]
    }}
    Ensure exactly 2 questions, each with exactly 4 options labeled A-D, and correct_answer as 'A', 'B', 'C', or 'D'.
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7
            )
        )
        lesson_json = json.loads(response.text)
        lesson = LessonResponse(**lesson_json)
        return lesson
    except Exception as e:
        st.warning(f"Lesson generation issue: {e}. Using fallback.")
        return LessonResponse(
            teaching_material=TeachingMaterial(content=f"Teaching content for {subtopic}: This is a basic explanation for {level} level."),
            questions=[
                Question(
                    question=f"What is a key concept of {subtopic}?",
                    options=[f"A. Concept 1 of {subtopic}", f"B. Concept 2 of {subtopic}", f"C. Concept 3 of {subtopic}", f"D. Concept 4 of {subtopic}"],
                    correct_answer="A"
                ),
                Question(
                    question=f"Why is {subtopic} important?",
                    options=[f"A. Reason 1 for {subtopic}", f"B. Reason 2 for {subtopic}", f"C. Reason 3 for {subtopic}", f"D. Reason 4 for {subtopic}"],
                    correct_answer="B"
                )
            ]
        )

def wrap_text(text, font, fontsize, max_width):
    lines = []
    current_line = ""
    words = text.split()
    for word in words:
        test_line = current_line + word + " " if current_line else word + " "
        width = font.text_length(test_line, fontsize=fontsize)
        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    return lines

def generate_pdf_notes(history):
    doc = pymupdf.open()
    page = doc.new_page()
    font = pymupdf.Font("helv")
    max_width = 450
    page.insert_text((72, 72), "Tutoring Notes", fontsize=16, fontname="helv", fontfile=None)
    y_position = 100
    for i, (subtopic, lesson, score, time_taken) in enumerate(history):
        subtopic_lines = wrap_text(f"Subtopic {i+1}: {subtopic}", font, 14, max_width)
        for line in subtopic_lines:
            if y_position > 700:
                page = doc.new_page()
                y_position = 72
            page.insert_text((72, y_position), line, fontsize=14, fontname="helv", fontfile=None)
            y_position += 20
        y_position += 10
        page.insert_text((72, y_position), "Lesson Content:", fontsize=12, fontname="helv", fontfile=None)
        y_position += 15
        content_lines = lesson.teaching_material.content.split('\n')
        for line in content_lines:
            wrapped_lines = wrap_text(line, font, 12, max_width)
            for wrapped_line in wrapped_lines:
                if y_position > 700:
                    page = doc.new_page()
                    y_position = 72
                page.insert_text((72, y_position), wrapped_line, fontsize=12, fontname="helv", fontfile=None)
                y_position += 15
        y_position += 10
        page.insert_text((72, y_position), "Questions:", fontsize=12, fontname="helv", fontfile=None)
        y_position += 15
        for j, q in enumerate(lesson.questions):
            question_lines = wrap_text(f"Q{j+1}: {q.question}", font, 12, max_width)
            for line in question_lines:
                if y_position > 700:
                    page = doc.new_page()
                    y_position = 72
                page.insert_text((72, y_position), line, fontsize=12, fontname="helv", fontfile=None)
                y_position += 15
            for opt in q.options:
                option_lines = wrap_text(f"- {opt}", font, 12, max_width)
                for line in option_lines:
                    if y_position > 700:
                        page = doc.new_page()
                        y_position = 72
                    page.insert_text((80, y_position), line, fontsize=12, fontname="helv", fontfile=None)
                    y_position += 15
            if y_position > 700:
                page = doc.new_page()
                y_position = 72
            page.insert_text((80, y_position), f"Correct Answer: {q.correct_answer}", fontsize=12, fontname="helv", fontfile=None)
            y_position += 20
        if y_position > 700:
            page = doc.new_page()
            y_position = 72
        page.insert_text((72, y_position), f"Score: {score}/2", fontsize=12, fontname="helv", fontfile=None)
        y_position += 15
        page.insert_text((72, y_position), f"Time Taken: {time_taken:.2f} minutes", fontsize=12, fontname="helv", fontfile=None)
        y_position += 30
    output = BytesIO()
    doc.save(output)
    doc.close()
    return output.getvalue()

# -------------------------
# NEW HELPERS: hints/explanations, difficulty-aware full quiz, and safe conversion helper
# -------------------------
def get_hint_for_question(subtopic, question_text, options):
    try:
        if model is not None:
            hint_prompt = (
                f"Provide a one-sentence hint for this MCQ.\n"
                f"Subtopic: {subtopic}\nQuestion: {question_text}\nOptions: {options}\n"
                "Do NOT reveal the correct option, only a helpful clue."
            )
            resp = model.generate_content(
                hint_prompt,
                generation_config=genai.types.GenerationConfig(response_mime_type="text/plain", temperature=0.3)
            )
            hint_text = getattr(resp, "text", None) or str(resp)
            hint_text = hint_text.strip().splitlines()[0][:300]
            if hint_text:
                return hint_text
    except Exception:
        pass
    words = [w.strip(".,?()[]:;") for w in question_text.split() if len(w.strip(".,?()[]:;")) > 4]
    keyword = words[0] if words else "the main definition"
    return f"Hint: focus on the primary definition or example — consider '{keyword}'."

def get_explanation_for_wrong(subtopic, question_text, chosen_option, correct_option, options):
    try:
        if model is not None:
            expl_prompt = (
                f"Explain in one short sentence why the chosen option is incorrect and give a concise reason why the correct option is correct.\n"
                f"Subtopic: {subtopic}\nQuestion: {question_text}\nOptions: {options}\n"
                f"Chosen: {chosen_option}\nCorrect: {correct_option}"
            )
            resp = model.generate_content(
                expl_prompt,
                generation_config=genai.types.GenerationConfig(response_mime_type="text/plain", temperature=0.2)
            )
            expl = getattr(resp, "text", None) or str(resp)
            return expl.strip().splitlines()[0][:400]
    except Exception:
        pass
    return f"Explanation: '{chosen_option}' is incorrect. Compare it with '{correct_option}' and review the definition."

def questions_to_plain_dicts(q_list):
    """
    Convert a list of Question instances (or dict-like) into a list of plain dicts suitable for Pydantic v2.
    """
    out = []
    for q in q_list:
        if isinstance(q, dict):
            out.append(q)
        elif hasattr(q, "model_dump"):
            out.append(q.model_dump())
        elif hasattr(q, "dict"):
            out.append(q.dict())
        else:
            out.append({
                "question": getattr(q, "question", str(q)),
                "options": getattr(q, "options", []),
                "correct_answer": getattr(q, "correct_answer", "A")
            })
    return out

def generate_full_topic_quiz(topic, level, pdf_text=None, num_questions=10, difficulty="mixed"):
    if model is not None:
        try:
            context = (f"Context/notes: {pdf_text[:4000]}\n" if pdf_text else "")
            prompt = (
                f"Generate {num_questions} MCQ questions for the topic '{topic}' at level {level}.\n"
                f"{context}"
                f"Difficulty mode: {difficulty}. Use a variety of concepts across the topic.\n"
                "Output JSON as a list: [{\"question\":\"...\",\"options\":[\"A...\",\"B...\",\"C...\",\"D...\"],\"correct\":\"A\"}, ...]"
            )
            resp = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(response_mime_type="application/json", temperature=0.6)
            )
            raw = getattr(resp, "text", None) or str(resp)
            data = json.loads(raw)
            quiz = []
            for item in data[:num_questions]:
                q = {
                    "question": item.get("question", "Question missing"),
                    "options": item.get("options", ["A","B","C","D"]),
                    "correct": item.get("correct", "A")
                }
                quiz.append(q)
            if quiz:
                return quiz
        except Exception:
            pass
    fallback = []
    for i in range(num_questions):
        qtext = f"{topic} — Practice Q{i+1}: core idea?"
        opts = [f"A. {topic} concept {i+1}a", f"B. {topic} concept {i+1}b", f"C. {topic} concept {i+1}c", f"D. {topic} concept {i+1}d"]
        correct = ["A","B","C","D"][i % 4]
        fallback.append({"question": qtext, "options": opts, "correct": correct})
    return fallback

# -------------------------
# Progress PDF helper (unchanged pattern)
# -------------------------
def generate_progress_pdf(summary: dict):
    doc = pymupdf.open()
    page = doc.new_page()
    font = pymupdf.Font("helv")
    y = 50
    page.insert_text((72, y), "Progress Report", fontsize=20, fontname="helv", fontfile=None)
    y += 30
    page.insert_text((72, y), f"Average Score: {summary.get('avg_score', 'N/A')}", fontsize=12, fontname="helv", fontfile=None)
    y += 18
    page.insert_text((72, y), f"Average Time (min): {summary.get('avg_time', 'N/A')}", fontsize=12, fontname="helv", fontfile=None)
    y += 18
    page.insert_text((72, y), f"Total Sessions: {summary.get('sessions', 0)}", fontsize=12, fontname="helv", fontfile=None)
    y += 24
    page.insert_text((72, y), "Per-subtopic scores:", fontsize=12, fontname="helv", fontfile=None)
    y += 18
    for sub, val in summary.get("per_subtopic", {}).items():
        page.insert_text((72, y), f"- {sub}: {val}", fontsize=11, fontname="helv", fontfile=None)
        y += 14
        if y > 700:
            page = doc.new_page()
            y = 72
    buf = BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()

# -------------------------
# Streamlit UI & session_state
# -------------------------
st.title("AI-Powered Personalized Tutor")

# Sidebar
with st.sidebar:
    st.header("Tutoring Setup")
    topic = st.text_input("Main Topic:")
    level = st.selectbox("Select Level:", [
        "Class 1-5 (Junior)", "Class 5-10", "Class 11-12",
        "Graduation", "MTech/MBA", "PhD"
    ])
    endgoal = st.text_input("End Goal (e.g., 'Understand basics for exam'):")
    uploaded_file = st.file_uploader("Upload PDF Notes (Optional):", type="pdf")

    # Difficulty selector for full-topic quiz
    st.markdown("**Full Quiz Difficulty**")
    full_quiz_difficulty = st.radio("Difficulty:", options=["mixed","easy","medium","hard"], index=0)

    if st.button("Take Full Topic Quiz"):
        if not topic:
            st.error("Please set 'Main Topic' before taking full topic quiz.")
        else:
            pdf_text = None
            if uploaded_file:
                with st.spinner("Extracting PDF for full quiz..."):
                    pdf_text = extract_pdf_text(uploaded_file)
            with st.spinner("Generating full topic quiz (10 Qs)..."):
                fq = generate_full_topic_quiz(topic, level, pdf_text=pdf_text, num_questions=10, difficulty=full_quiz_difficulty)
                st.session_state.full_quiz = fq
                st.session_state.full_quiz_start = time.time()
                st.session_state.full_quiz_answers = {}
                st.session_state.full_quiz_confidence = {}
                st.session_state.full_quiz_taken = False
            st.success("Full topic quiz ready — open 'Full Topic Quiz' panel below to attempt it.")
            st.rerun()

    if st.button("Start Tutoring"):
        if not topic or not endgoal:
            st.error("Please provide topic and end goal.")
        else:
            pdf_text = None
            if uploaded_file:
                with st.spinner("Extracting from PDF..."):
                    pdf_text = extract_pdf_text(uploaded_file)
                    if pdf_text:
                        st.success("PDF processed.")
                    else:
                        st.warning("No text extracted from PDF; proceeding without notes.")
            with st.spinner("Generating subtopics..."):
                subtopics = generate_subtopics(topic, level, endgoal, pdf_text)
                st.session_state.subtopics = subtopics
                st.session_state.current_index = 0
                st.session_state.performance_history = []
                st.session_state.time_history = []
                st.session_state.lesson_history = []
                st.session_state.lesson_start_time = None
                st.session_state.current_lesson = None
                st.session_state.quiz_taken = False
                st.session_state.hints_cache = {}
                st.session_state.retries = {}
                st.session_state.combined_test = None
                st.session_state.combined_test_taken = False
                st.session_state.full_quiz = None
                st.session_state.full_quiz_taken = False
                st.session_state.explanations_cache = {}
                st.session_state.confidence_log = {}
            st.success(f"Generated {len(subtopics)} subtopics: {', '.join(subtopics)}")
            st.rerun()

    if 'lesson_history' in st.session_state and st.session_state.lesson_history:
        pdf_data = generate_pdf_notes(st.session_state.lesson_history)
        st.download_button(
            label="Download Notes as PDF",
            data=pdf_data,
            file_name="tutoring_notes.pdf",
            mime="application/pdf"
        )

    if st.button("Export Progress Report"):
        summary = {}
        if st.session_state.get('performance_history'):
            summary['avg_score'] = f"{sum(st.session_state.performance_history)/len(st.session_state.performance_history):.2f}/2"
            summary['avg_time'] = f"{sum(st.session_state.time_history)/len(st.session_state.time_history):.2f}"
            summary['sessions'] = len(st.session_state.performance_history)
        else:
            summary['avg_score'] = "N/A"
            summary['avg_time'] = "N/A"
            summary['sessions'] = 0
        per_sub = {}
        for idx, (subtopic, lesson, score, t) in enumerate(st.session_state.get('lesson_history', [])):
            per_sub[subtopic] = per_sub.get(subtopic, 0) + score
        summary['per_subtopic'] = per_sub
        pdf_bytes = generate_progress_pdf(summary)
        st.download_button("Download Progress PDF", data=pdf_bytes, file_name="progress_report.pdf", mime="application/pdf")

# Initialize session state keys
if 'subtopics' not in st.session_state:
    st.session_state.subtopics = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'performance_history' not in st.session_state:
    st.session_state.performance_history = []
if 'time_history' not in st.session_state:
    st.session_state.time_history = []
if 'lesson_history' not in st.session_state:
    st.session_state.lesson_history = []
if 'lesson_start_time' not in st.session_state:
    st.session_state.lesson_start_time = None
if 'current_lesson' not in st.session_state:
    st.session_state.current_lesson = None
if 'quiz_taken' not in st.session_state:
    st.session_state.quiz_taken = False

# NEW keys
if 'hints_cache' not in st.session_state:
    st.session_state.hints_cache = {}
if 'retries' not in st.session_state:
    st.session_state.retries = {}
if 'combined_test' not in st.session_state:
    st.session_state.combined_test = None
if 'combined_test_taken' not in st.session_state:
    st.session_state.combined_test_taken = False
if 'full_quiz' not in st.session_state:
    st.session_state.full_quiz = None
if 'full_quiz_start' not in st.session_state:
    st.session_state.full_quiz_start = None
if 'full_quiz_answers' not in st.session_state:
    st.session_state.full_quiz_answers = {}
if 'full_quiz_taken' not in st.session_state:
    st.session_state.full_quiz_taken = False
if 'explanations_cache' not in st.session_state:
    st.session_state.explanations_cache = {}
if 'confidence_log' not in st.session_state:
    st.session_state.confidence_log = {}

# Helper to clear per-subtopic keys to avoid stale radio selections
def clear_subtopic_widget_keys(sub_idx, max_questions=4):
    for qi in range(max_questions):
        st.session_state.pop(f"q_{sub_idx}_{qi}", None)
        st.session_state.pop(f"conf_{sub_idx}_{qi}", None)
        st.session_state.pop(f"hint_btn_{sub_idx}_{qi}", None)
        # also clear any other keys that follow your naming pattern
        st.session_state.pop(f"full_q_{qi}", None)
        st.session_state.pop(f"full_conf_{qi}", None)

# UI main
st.header("Tutoring Session")

# Full quiz panel
if st.session_state.full_quiz:
    st.markdown("## Full Topic Quiz")
    full_quiz = st.session_state.full_quiz
    for idx, item in enumerate(full_quiz):
        st.markdown(f"**Q{idx+1}**: {item['question']}")
        conf_key = f"full_conf_{idx}"
        if conf_key not in st.session_state:
            st.session_state[conf_key] = "Medium"
        conf = st.radio("Confidence (mark before answering):", options=["Low","Medium","High"], index=["Low","Medium","High"].index(st.session_state[conf_key]), key=conf_key)
        st.session_state.confidence_log[("full", idx)] = conf
        fk = ("full", idx)
        if st.session_state.hints_cache.get(fk):
            st.info(f"Hint: {st.session_state.hints_cache[fk]}")
        ans_key = f"full_q_{idx}"
        selected = st.radio("Choose an option:", options=item['options'], key=ans_key)
        st.session_state.full_quiz_answers[idx] = selected
        if st.button("Hint", key=f"full_hint_btn_{idx}"):
            hint_text = get_hint_for_question(topic, item['question'], item['options'])
            st.session_state.hints_cache[("full", idx)] = hint_text
            #st.experimental_rerun()

    if not st.session_state.full_quiz_taken:
        if st.button("Submit Full Topic Quiz"):
            if st.session_state.full_quiz_start is None:
                st.session_state.full_quiz_start = time.time()
            endt = time.time()
            taken = (endt - st.session_state.full_quiz_start) / 60.0
            score = 0
            for idx, item in enumerate(full_quiz):
                correct_label = item.get('correct','A')
                correct_idx = {'A':0,'B':1,'C':2,'D':3}.get(correct_label,0)
                if st.session_state.full_quiz_answers.get(idx) == item['options'][correct_idx]:
                    score += 1
                else:
                    explanation = get_explanation_for_wrong(topic, item['question'], st.session_state.full_quiz_answers.get(idx, "N/A"), correct_label, item['options'])
                    st.session_state.explanations_cache[("full", idx)] = explanation
            st.success(f"Full Topic Quiz Score: {score}/{len(full_quiz)} | Time: {taken:.2f} min")
            # convert and append to lesson_history in chunks of 2, using dict conversion for pydantic safety
            q_dicts = []
            for item in full_quiz:
                q_dicts.append({
                    "question": item['question'],
                    "options": item['options'],
                    "correct_answer": item.get('correct','A')
                })
            chunk_size = 2
            for i in range(0, len(q_dicts), chunk_size):
                chunk = q_dicts[i:i+chunk_size]
                if len(chunk) < 2:
                    chunk.append({"question":"(placeholder)", "options":["A. x","B. y","C. z","D. w"], "correct_answer":"A"})
                teaching_content = f"Full Topic Quiz chunk {i//chunk_size + 1}."
                # include explanations if exist
                expl_texts = []
                for j in range(i, i+len(chunk)):
                    expl = st.session_state.explanations_cache.get(("full", j))
                    if expl:
                        expl_texts.append(f"Q{j+1} explanation: {expl}")
                if expl_texts:
                    teaching_content += "\n\n" + "\n".join(expl_texts)
                # create LessonResponse using plain dicts for 'questions'
                pseudo_lesson = LessonResponse(
                    teaching_material={"content": teaching_content},
                    questions=chunk
                )
                st.session_state.lesson_history.append((f"Full Topic Quiz (part {i//chunk_size + 1})", pseudo_lesson, score if i==0 else 0, taken if i==0 else 0.0))
            st.session_state.full_quiz_taken = True
            st.rerun()
    else:
        if st.button("Retake Full Topic Quiz"):
            st.session_state.full_quiz_answers = {}
            st.session_state.full_quiz_start = time.time()
            st.session_state.full_quiz_taken = False
            for k in list(st.session_state.hints_cache.keys()):
                if isinstance(k, tuple) and k[0] == "full":
                    del st.session_state.hints_cache[k]
            for k in list(st.session_state.explanations_cache.keys()):
                if isinstance(k, tuple) and k[0] == "full":
                    del st.session_state.explanations_cache[k]
            st.rerun()

# Tutoring session UI
if st.session_state.subtopics:
    for idx, (subtopic, lesson, score, time_taken) in enumerate(st.session_state.lesson_history):
        with st.expander(f"Subtopic {idx+1}: {subtopic}", expanded=False):
            st.markdown(f"**Lesson Content**:\n{lesson.teaching_material.content}")
            st.markdown("**Quiz Questions**:")
            for i, q in enumerate(lesson.questions):
                st.markdown(f"**Q{i+1}**: {q.question}")
                for opt in q.options:
                    st.markdown(f"- {opt}")
                st.markdown(f"**Correct Answer**: {q.correct_answer}")
                expl = st.session_state.explanations_cache.get((idx, i))
                if expl:
                    st.markdown(f"**Explanation**: {expl}")
            st.markdown(f"**Score**: {score}/2")
            st.markdown(f"**Time Taken**: {time_taken:.2f} minutes")

    if st.session_state.current_index < len(st.session_state.subtopics):
        subtopic = st.session_state.subtopics[st.session_state.current_index]
        st.markdown(f"**Subtopic {st.session_state.current_index + 1}: {subtopic}**")
        
        # Generate lesson if needed; clear stale widget keys first
        if st.session_state.current_lesson is None:
            with st.spinner("Generating lesson..."):
                if st.session_state.lesson_start_time is None:
                    st.session_state.lesson_start_time = time.time()
                prev_perf = st.session_state.performance_history[-1] if st.session_state.performance_history else None
                prev_time = st.session_state.time_history[-1] if st.session_state.time_history else None
                lesson = generate_lesson(subtopic, level, prev_perf, prev_time)
                # clear stale widgets for this index to prevent mismatched radio values
                clear_subtopic_widget_keys(st.session_state.current_index, max_questions=len(lesson.questions)+2)
                st.session_state.current_lesson = lesson
            st.rerun()
        
        lesson = st.session_state.current_lesson
        st.markdown(f"**Lesson Content**:\n{lesson.teaching_material.content}")
        
        if not st.session_state.quiz_taken:
            st.markdown("**Quiz Time!**")
            score = 0
            answers = {}
            lesson_conf_prefix = f"conf_{st.session_state.current_index}_"
            for i, q in enumerate(lesson.questions):
                st.markdown(f"**Q{i+1}**: {q.question}")
                conf_key = lesson_conf_prefix + str(i)
                if conf_key not in st.session_state:
                    st.session_state[conf_key] = "Medium"
                conf = st.radio("Confidence (mark before answering):", options=["Low","Medium","High"], index=["Low","Medium","High"].index(st.session_state[conf_key]), key=conf_key)
                st.session_state.confidence_log[(st.session_state.current_index, i)] = conf

                hint_key = (st.session_state.current_index, i)
                if st.session_state.hints_cache.get(hint_key):
                    st.info(f"Hint: {st.session_state.hints_cache[hint_key]}")
                
                # ensure radio key unique and cleared earlier; use same naming
                answer = st.radio(
                    "Choose an option:",
                    options=q.options,
                    key=f"q_{st.session_state.current_index}_{i}"
                )
                answers[i] = answer
                
                hint_btn_key = f"hint_btn_{st.session_state.current_index}_{i}"
                if st.button("Hint", key=hint_btn_key):
                    hint_text = get_hint_for_question(subtopic, q.question, q.options)
                    st.session_state.hints_cache[hint_key] = hint_text
                    st.rerun()
            
            if st.button("Submit Quiz"):
                if st.session_state.lesson_start_time is None:
                    st.error("Timer not started. Starting now and please resubmit.")
                    st.session_state.lesson_start_time = time.time()
                    st.rerun()
                else:
                    end_time = time.time()
                    time_taken = (end_time - st.session_state.lesson_start_time) / 60
                    for i, q in enumerate(lesson.questions):
                        correct_idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3}[q.correct_answer]
                        if answers.get(i) == q.options[correct_idx]:
                            score += 1
                            st.success(f"Q{i+1}: Correct!")
                        else:
                            st.error(f"Q{i+1}: Wrong! Correct is {q.correct_answer}: {q.options[correct_idx]}")
                            expl = get_explanation_for_wrong(subtopic, q.question, answers.get(i, "N/A"), q.correct_answer, q.options)
                            st.session_state.explanations_cache[(st.session_state.current_index, i)] = expl
                            st.markdown(f"**Explanation**: {expl}")
                    st.session_state.performance_history.append(score)
                    st.session_state.time_history.append(time_taken)
                    # convert question instances to plain dicts for pydantic
                    questions_data = questions_to_plain_dicts(lesson.questions)
                    expl_texts = []
                    for i, _ in enumerate(lesson.questions):
                        expl = st.session_state.explanations_cache.get((st.session_state.current_index, i))
                        if expl:
                            expl_texts.append(f"Q{i+1} explanation: {expl}")
                    combined_content = lesson.teaching_material.content + ("\n\n" + "\n".join(expl_texts) if expl_texts else "")
                    lesson_for_history = LessonResponse(
                        teaching_material={"content": combined_content},
                        questions=questions_data
                    )
                    st.session_state.lesson_history.append((subtopic, lesson_for_history, score, time_taken))
                    st.session_state.quiz_taken = True
                    st.session_state.lesson_start_time = None
                    st.success(f"Overall Score: {score}/2 | Time: {time_taken:.2f} min")
                    st.rerun()
        
        else:
            if st.button("Reteach Topic"):
                idx = st.session_state.current_index
                st.session_state.retries[idx] = st.session_state.retries.get(idx, 0) + 1
                # clear hints and widget keys for this topic
                for k in list(st.session_state.hints_cache.keys()):
                    if isinstance(k, tuple) and k[0] == idx:
                        del st.session_state.hints_cache[k]
                clear_subtopic_widget_keys(idx, max_questions=6)
                st.session_state.current_lesson = None
                st.session_state.quiz_taken = False
                st.session_state.lesson_start_time = None
                st.rerun()

            if st.button("Next Subtopic"):
                old_idx = st.session_state.current_index
                clear_subtopic_widget_keys(old_idx, max_questions=6)
                st.session_state.current_index += 1
                st.session_state.quiz_taken = False
                st.session_state.current_lesson = None
                st.session_state.lesson_start_time = None
                st.rerun()
    
    if st.button("End Session"):
        if st.session_state.lesson_history:
            pdf_data = generate_pdf_notes(st.session_state.lesson_history)
            st.session_state.lesson_history = []
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Combined Test
    all_done = st.session_state.subtopics and st.session_state.current_index >= len(st.session_state.subtopics)
    if all_done and st.session_state.lesson_history:
        st.markdown("---")
        st.subheader("Final Combined Test")
        st.markdown("You can take a combined test that includes all questions from each subtopic.")

        if st.session_state.combined_test is None:
            combined = []
            for (subtopic, lesson, score, time_taken) in st.session_state.lesson_history:
                for q in lesson.questions:
                    combined.append({
                        "subtopic": subtopic,
                        "question": q.question,
                        "options": q.options,
                        "correct": q.correct_answer
                    })
            st.session_state.combined_test = combined
            st.session_state.combined_test_taken = False

        if not st.session_state.combined_test_taken:
            st.info(f"Combined test contains {len(st.session_state.combined_test)} questions.")
            combined_answers = {}
            for idx, item in enumerate(st.session_state.combined_test):
                st.markdown(f"**Q{idx+1} ({item['subtopic']})**: {item['question']}")
                ckey = f"comb_conf_{idx}"
                if ckey not in st.session_state:
                    st.session_state[ckey] = "Medium"
                conf = st.radio("Confidence (mark before answering):", options=["Low","Medium","High"], index=["Low","Medium","High"].index(st.session_state[ckey]), key=ckey)
                st.session_state.confidence_log[("combined", idx)] = conf

                sel = st.radio("Choose an option:", options=item['options'], key=f"combined_q_{idx}")
                combined_answers[idx] = sel
                if st.button("Hint", key=f"combined_hint_btn_{idx}"):
                    hinttext = get_hint_for_question(item['subtopic'], item['question'], item['options'])
                    st.session_state.hints_cache[("combined", idx)] = hinttext
                    st.rerun()
                if st.session_state.hints_cache.get(("combined", idx)):
                    st.info(f"Hint: {st.session_state.hints_cache.get(('combined', idx))}")

            if st.button("Submit Combined Test"):
                combined_score = 0
                for idx, item in enumerate(st.session_state.combined_test):
                    correct_idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3}[item['correct']]
                    if combined_answers.get(idx) == item['options'][correct_idx]:
                        combined_score += 1
                    else:
                        expl = get_explanation_for_wrong(item['subtopic'], item['question'], combined_answers.get(idx, "N/A"), item['correct'], item['options'])
                        st.session_state.explanations_cache[("combined", idx)] = expl
                        st.markdown(f"**Explanation**: {expl}")
                st.success(f"Combined Score: {combined_score}/{len(st.session_state.combined_test)}")
                st.session_state.combined_test_taken = True
        else:
            if st.button("Retake Combined Test"):
                st.session_state.combined_test_taken = False
                for k in list(st.session_state.hints_cache.keys()):
                    if isinstance(k, tuple) and k[0] == "combined":
                        del st.session_state.hints_cache[k]
                for k in list(st.session_state.explanations_cache.keys()):
                    if isinstance(k, tuple) and k[0] == "combined":
                        del st.session_state.explanations_cache[k]
                st.rerun()

# Progress dashboard in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Progress Dashboard")
if st.session_state.performance_history:
    avg_score = sum(st.session_state.performance_history) / len(st.session_state.performance_history)
    avg_time = sum(st.session_state.time_history) / len(st.session_state.time_history)
    st.sidebar.metric("Average Score (per lesson)", f"{avg_score:.2f}/2")
    st.sidebar.metric("Average Time (min)", f"{avg_time:.2f}")

    total_retries = sum(st.session_state.retries.values()) if st.session_state.retries else 0
    st.sidebar.write(f"Total retries: {total_retries}")

    per_sub = {}
    for idx, (subtopic, lesson, score, t) in enumerate(st.session_state.lesson_history):
        per_sub[subtopic] = per_sub.get(subtopic, []) + [score]
    labels = list(per_sub.keys())
    values = [sum(v)/len(v) for v in per_sub.values()] if labels else []
    if labels:
        fig, ax = plt.subplots(figsize=(4,2))
        ax.barh(labels, values)
        ax.set_xlim(0,2)
        ax.set_xlabel("Avg score (0-2)")
        ax.set_title("Per-subtopic average score")
        st.sidebar.pyplot(fig)

    total_high_conf = 0
    high_conf_correct = 0
    # For accurate calibration, we would need to store chosen answers with confidence per question.
    # We compute a rough metric where possible (only for 'full' context reliably).
    for k, v in st.session_state.confidence_log.items():
        if v == "High":
            total_high_conf += 1
            ctx, qidx = k
            if ctx == "full" and st.session_state.get('full_quiz'):
                chosen = st.session_state.full_quiz_answers.get(qidx)
                correct_label = st.session_state.full_quiz[qidx]['correct']
                correct = st.session_state.full_quiz[qidx]['options'][{'A':0,'B':1,'C':2,'D':3}[correct_label]]
                if chosen and correct and chosen == correct:
                    high_conf_correct += 1
    calibration = f"{(high_conf_correct/total_high_conf*100):.1f}%" if total_high_conf else "N/A"
    st.sidebar.write(f"High-confidence correct rate: {calibration}")
else:
    st.sidebar.write("No progress data yet. Take lessons or quizzes to see progress.")

# Main performance summary
if st.session_state.performance_history:
    st.subheader("Performance Summary")
    col1, col2 = st.columns(2)
    col1.metric("Average Score", f"{sum(st.session_state.performance_history)/len(st.session_state.performance_history):.2f}/2")
    col2.metric("Average Time", f"{sum(st.session_state.time_history)/len(st.session_state.time_history):.2f} min")
