import streamlit as st
from utils import load_questions, get_day_questions
from flashcards import run_flashcard_mode
from quiz_mode import run_quiz_mode
from review_mode import run_review_mode
from mistakes import run_mistake_review_mode

# ─── App Title and Sidebar ────────────────────────────────────────────────
st.set_page_config(page_title="MM Prep Flashcards", layout="wide")
st.title("📚 MM Prep - Study Tool")

# ─── Load All Questions ───────────────────────────────────────────────────
all_questions = load_questions("questions.json")

# ─── Select Study Day ─────────────────────────────────────────────────────
day = st.sidebar.selectbox("Choose study day (1–7)", list(range(1, 8)))
day_questions = get_day_questions(all_questions, day)

# ─── Select Mode ──────────────────────────────────────────────────────────
mode = st.sidebar.radio("Choose mode", [
    "Flashcard Mode", 
    "Quiz Mode", 
    "Review Mode", 
    "Mistake Review Mode"
])

# ─── Route to Selected Mode ───────────────────────────────────────────────
if mode == "Flashcard Mode":
    run_flashcard_mode(day_questions, day)

elif mode == "Quiz Mode":
    run_quiz_mode(day_questions, day)

elif mode == "Review Mode":
    run_review_mode(day_questions, day)

elif mode == "Mistake Review Mode":
    run_mistake_review_mode(day)
