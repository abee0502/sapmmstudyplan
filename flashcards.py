import streamlit as st
import random
import os
import json
from utils import save_json, load_json

PROGRESS_FILE = "progress.json"
ANSWERED_FILE = "answered_ids.json"

def run_flashcard_mode(questions, day):
    total = len(questions)

    # ─── Load answered question IDs ──────────────────────────────────────
    answered_data = load_json(ANSWERED_FILE, {})
    today_key = f"day{day}"
    answered_ids = answered_data.get(today_key, [])

    # ─── Set up session state ─────────────────────────────────────────────
    if "flashcard_index" not in st.session_state:
        # Filter unanswered only
        unanswered_indices = [i for i in range(total) if i not in answered_ids]
        if not unanswered_indices:
            unanswered_indices = list(range(total))  # start fresh if all done
            # Count full round
            progress_data = load_json(PROGRESS_FILE, {})
            progress_data[today_key] = progress_data.get(today_key, 0) + 1
            save_json(PROGRESS_FILE, progress_data)
            answered_ids = []
            answered_data[today_key] = answered_ids
            save_json(ANSWERED_FILE, answered_data)

        random.shuffle(unanswered_indices)
        st.session_state.flashcard_order = unanswered_indices
        st.session_state.flashcard_index = 0
        st.session_state.flashcard_submitted = False

    idx = st.session_state.flashcard_order[st.session_state.flashcard_index]
    question = questions[idx]

    # ─── UI Display ───────────────────────────────────────────────────────
    st.markdown(f"**Question {st.session_state.flashcard_index + 1} / {total}**")
    st.info(question["instruction"])
    st.markdown(question["question"])

    selected = st.multiselect("Select answer(s):", list(question["options"].values()))

    # Map selected text back to letter keys
    rev_options = {v: k for k, v in question["options"].items()}
    selected_keys = [rev_options.get(text) for text in selected]

    # ─── Submit Answer ─────────────────────────────────────────────────────
    if st.button("Submit"):
        correct = set(question["answers"])
        submitted = set(selected_keys)

        if submitted == correct:
            st.success("✅ Correct!")
        else:
            st.error("❌ Incorrect.")
            correct_answers = ", ".join([f"{k}: {v}" for k, v in question["options"].items() if k in correct])
            st.markdown(f"**Correct answer(s):** {correct_answers}")

        st.session_state.flashcard_submitted = True

        # Save this question as answered
        answered_ids.append(idx)
        answered_data[today_key] = answered_ids
        save_json(ANSWERED_FILE, answered_data)

    # ─── Next Button ──────────────────────────────────────────────────────
    if st.session_state.flashcard_submitted:
        if st.button("Next"):
            st.session_state.flashcard_index += 1
            if st.session_state.flashcard_index >= len(st.session_state.flashcard_order):
                st.success("✅ You've completed this round!")
                del st.session_state.flashcard_index
                del st.session_state.flashcard_order
            st.session_state.flashcard_submitted = False
            st.experimental_rerun()

    # ─── Progress Bar ─────────────────────────────────────────────────────
    answered_count = len(answered_ids)
    st.progress(answered_count / total)
    st.caption(f"Progress: {answered_count} / {total} questions")

    # ─── Completed Round Info ─────────────────────────────────────────────
    progress_data = load_json(PROGRESS_FILE, {})
    count = progress_data.get(today_key, 0)
    st.caption(f"Completed rounds today: {count}")
