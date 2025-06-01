import streamlit as st
import random
from utils import save_json, load_json

PROGRESS_FILE = "progress.json"
ANSWERED_FILE = "answered_ids.json"

def run_flashcard_mode(questions, day):
    total = len(questions)
    today_key = f"day{day}"

    # ─── Load answered IDs and progress count ─────────────────────────────
    answered_data = load_json(ANSWERED_FILE, {})
    answered_ids = answered_data.get(today_key, [])

    progress_data = load_json(PROGRESS_FILE, {})
    completed_rounds = progress_data.get(today_key, 0)

    # ─── Session Initialization ───────────────────────────────────────────
    if "flashcard_index" not in st.session_state:
        unanswered = [i for i in range(total) if i not in answered_ids]
        if not unanswered:
            # All questions answered → reset for new round
            unanswered = list(range(total))
            answered_ids = []
            answered_data[today_key] = answered_ids
            save_json(ANSWERED_FILE, answered_data)

            completed_rounds += 1
            progress_data[today_key] = completed_rounds
            save_json(PROGRESS_FILE, progress_data)

        random.shuffle(unanswered)
        st.session_state.flashcard_order = unanswered
        st.session_state.flashcard_index = 0
        st.session_state.flashcard_submitted = False
        st.session_state.selected_options = set()

    idx = st.session_state.flashcard_order[st.session_state.flashcard_index]
    q = questions[idx]

    st.markdown(f"**Question {st.session_state.flashcard_index + 1} / {total}**")
    st.info(q["instruction"])
    st.markdown(q["question"])

    # ─── Render Checkboxes for Options ────────────────────────────────────
    selected_keys = []
    for key, text in q["options"].items():
        checked = st.checkbox(f"{key}: {text}", key=f"opt_{key}")
        if checked:
            selected_keys.append(key)

    # ─── Submit Logic ─────────────────────────────────────────────────────
    if st.button("Submit"):
        if not selected_keys:
            st.warning("⚠️ Please select at least one answer before submitting.")
        else:
            correct = set(q["answers"])
            selected = set(selected_keys)

            if selected == correct:
                st.success("✅ Correct!")
            else:
                st.error("❌ Incorrect.")
                correct_answers = ", ".join([f"{k}: {v}" for k, v in q["options"].items() if k in correct])
                st.markdown(f"**Correct answer(s):** {correct_answers}")

            # Save answer
            answered_ids.append(idx)
            answered_data[today_key] = answered_ids
            save_json(ANSWERED_FILE, answered_data)

            # Mark as submitted
            st.session_state.flashcard_submitted = True

    # ─── Next Logic ───────────────────────────────────────────────────────
    if st.button("Next"):
        if not st.session_state.flashcard_submitted:
            st.warning("⚠️ Please submit your answer before going to the next question.")
        else:
            # Clear checkboxes
            for k in q["options"].keys():
                st.session_state.pop(f"opt_{k}", None)

            st.session_state.flashcard_index += 1
            st.session_state.flashcard_submitted = False

            if st.session_state.flashcard_index >= len(st.session_state.flashcard_order):
                st.success("🎉 You've completed all questions for this round.")
                del st.session_state.flashcard_index
                del st.session_state.flashcard_order
                return

            st.experimental_rerun()

    # ─── Progress + Rounds Info ───────────────────────────────────────────
    st.progress(len(answered_ids) / total)
    st.caption(f"Progress: {len(answered_ids)} / {total}")
    st.caption(f"Completed rounds today: {completed_rounds}")
