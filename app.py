import os
import json
import re
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# API KEY
# ============================================================

def get_api_key():
    try:
        key = st.secrets["GROQ_API_KEY"]
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY")


# ============================================================
# JSON CLEANER
# ============================================================

def clean_json(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


# ============================================================
# AI GENERATION
# ============================================================

def generate_study_pack(
    topic,
    level,
    duration,
    study_time,
    exam_date,
    focus
):
    api_key = get_api_key()

    if not api_key:
        return {
            "error": "GROQ_API_KEY is missing. Add it to Streamlit Secrets."
        }

    client = Groq(api_key=api_key)

    prompt = f"""
You are an expert AI teacher, study planner, exam mentor,
curriculum designer and educational content creator.

Create a COMPLETE, personalized AI STUDY PACK.

STUDENT INFORMATION
Subject/Topic: {topic}
Level: {level}
Study Duration: {duration}
Daily Study Time: {study_time}
Exam Date: {exam_date if exam_date else "Not provided"}
Main Focus: {focus if focus else "Balanced learning"}

IMPORTANT:
- Make everything specific to the requested topic.
- Use simple student-friendly language.
- Avoid generic content.
- Keep the workload realistic.
- Prioritize important concepts.
- Include learning, practice, revision and self-testing.
- If an exam date is provided, prioritize exam preparation.
- Generate useful study notes, not just topic names.
- Generate MCQs with exactly 4 options and one correct answer.
- Generate a realistic Study Plan instead of a Weekly Plan.
- Return ONLY valid JSON.
- Do not return Markdown.

Return exactly this structure:

{{
  "title": "Study Pack title",
  "overview": "Personalized overview",

  "learning_objectives": [
    "objective 1",
    "objective 2",
    "objective 3"
  ],

  "prerequisites": [
    "prerequisite 1",
    "prerequisite 2"
  ],

  "priority_topics": [
    {{
      "topic": "Topic",
      "importance": "High/Medium/Low",
      "reason": "Reason"
    }}
  ],

  "study_notes": [
    {{
      "topic": "Topic name",
      "explanation": "Clear and useful explanation",
      "key_points": [
        "important point 1",
        "important point 2"
      ],
      "example": "Simple example"
    }}
  ],

  "study_strategy": [
    "strategy 1",
    "strategy 2",
    "strategy 3"
  ],

  "study_plan": [
    {{
      "day": "Day 1",
      "focus": "Main focus",
      "topics": ["topic 1", "topic 2"],
      "study_tasks": [
        "task 1",
        "task 2"
      ],
      "practice": [
        "practice task"
      ],
      "revision": "Revision activity",
      "estimated_time": "2 hours"
    }}
  ],

  "flashcards": [
    {{
      "question": "Question",
      "answer": "Answer"
    }}
  ],

  "mcq_quiz": [
    {{
      "question": "Question",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer": "Option A",
      "explanation": "Why this is correct"
    }}
  ],

  "practice_questions": [
    {{
      "question": "Question",
      "answer": "Short correct answer",
      "difficulty": "Easy/Medium/Hard"
    }}
  ],

  "exam_tips": [
    "exam tip 1",
    "exam tip 2",
    "exam tip 3"
  ],

  "common_mistakes": [
    "mistake 1",
    "mistake 2"
  ],

  "final_revision_checklist": [
    "checklist item 1",
    "checklist item 2"
  ],

  "final_task": {{
    "title": "Final task",
    "instructions": "Detailed instructions"
  }}
}}

CONTENT AMOUNTS:
- 5-10 learning objectives
- 3-6 prerequisites
- 6-10 priority topics
- 8-15 study notes
- 6-10 flashcards
- 10 MCQs
- 8-12 practice questions
- 8-12 exam tips
- 5-10 common mistakes
- 8-12 revision checklist items
- Study Plan must cover the complete requested duration.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an educational AI. "
                        "Return valid JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=12000
        )

        raw = response.choices[0].message.content
        return json.loads(clean_json(raw))

    except json.JSONDecodeError:
        return {
            "error": "AI returned an invalid format. Please try again."
        }

    except Exception as e:
        return {
            "error": f"Generation failed: {str(e)}"
        }


# ============================================================
# HEADER
# ============================================================

st.title("📚 AI Study Pack Generator")

st.write(
    "Generate a personalized study pack with study notes, "
    "study plan, flashcards, MCQ quiz, practice questions, "
    "and exam tips."
)

st.divider()


# ============================================================
# INPUTS
# ============================================================

col1, col2 = st.columns(2)

with col1:
    topic = st.text_input(
        "📖 Subject / Topic",
        placeholder="e.g. Python Programming"
    )

    level = st.selectbox(
        "🎓 Your Level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    duration = st.text_input(
        "⏳ Study Duration",
        placeholder="e.g. 4 weeks, 10 days, 2 months"
    )

with col2:
    study_time = st.text_input(
        "⏰ Daily Study Time",
        placeholder="e.g. 2 hours/day"
    )

    exam_date = st.text_input(
        "📝 Exam Date (Optional)",
        placeholder="e.g. 15 October 2026"
    )

    focus = st.text_input(
        "🎯 Main Focus (Optional)",
        placeholder="e.g. exam preparation, concepts, coding"
    )


st.write("")

generate = st.button(
    "🚀 Generate Study Pack",
    type="primary",
    use_container_width=True
)


# ============================================================
# GENERATE
# ============================================================

if generate:

    if not topic.strip():
        st.warning("Please enter a subject or topic.")

    elif not duration.strip():
        st.warning("Please enter your study duration.")

    elif not study_time.strip():
        st.warning("Please enter your daily study time.")

    else:

        with st.spinner(
            "🤖 AI is creating your complete study pack..."
        ):
            result = generate_study_pack(
                topic,
                level,
                duration,
                study_time,
                exam_date,
                focus
            )

        if "error" in result:
            st.error(result["error"])

        else:

            st.success("🎉 Your study pack is ready!")

            st.header(
                f"📚 {result.get('title', 'Your Study Pack')}"
            )

            st.info(result.get("overview", ""))


            # ====================================================
            # LEARNING OBJECTIVES
            # ====================================================

            with st.expander(
                "🎯 Learning Objectives",
                expanded=True
            ):
                for item in result.get(
                    "learning_objectives", []
                ):
                    st.markdown(f"- {item}")


            # ====================================================
            # PREREQUISITES
            # ====================================================

            with st.expander("🧩 Prerequisites"):
                for item in result.get(
                    "prerequisites", []
                ):
                    st.markdown(f"- {item}")


            # ====================================================
            # PRIORITY TOPICS
            # ====================================================

            with st.expander(
                "🔥 Priority Topics",
                expanded=True
            ):
                for item in result.get(
                    "priority_topics", []
                ):
                    st.markdown(
                        f"### {item.get('topic', '')}"
                    )
                    st.write(
                        f"**Importance:** "
                        f"{item.get('importance', '')}"
                    )
                    st.write(
                        item.get("reason", "")
                    )
                    st.divider()


            # ====================================================
            # STUDY NOTES
            # ====================================================

            st.subheader("📖 Study Notes")

            for note in result.get(
                "study_notes", []
            ):
                with st.expander(
                    f"📌 {note.get('topic', '')}"
                ):
                    st.write(
                        note.get("explanation", "")
                    )

                    st.markdown("**Key Points**")

                    for point in note.get(
                        "key_points", []
                    ):
                        st.markdown(f"- {point}")

                    if note.get("example"):
                        st.markdown("**Example**")
                        st.write(
                            note.get("example")
                        )


            # ====================================================
            # STUDY STRATEGY
            # ====================================================

            with st.expander("🧠 Study Strategy"):
                for item in result.get(
                    "study_strategy", []
                ):
                    st.markdown(f"- {item}")


            # ====================================================
            # STUDY PLAN
            # ====================================================

            st.subheader("🗓️ Study Plan")

            for day in result.get(
                "study_plan", []
            ):
                with st.expander(
                    f"{day.get('day', '')} — "
                    f"{day.get('focus', '')}"
                ):

                    st.write(
                        f"⏰ **Estimated Time:** "
                        f"{day.get('estimated_time', '')}"
                    )

                    st.markdown("**Topics**")
                    for item in day.get(
                        "topics", []
                    ):
                        st.markdown(f"- {item}")

                    st.markdown("**Study Tasks**")
                    for item in day.get(
                        "study_tasks", []
                    ):
                        st.markdown(f"- {item}")

                    st.markdown("**Practice**")
                    for item in day.get(
                        "practice", []
                    ):
                        st.markdown(f"- {item}")

                    st.markdown("**Revision**")
                    st.write(
                        day.get("revision", "")
                    )


            # ====================================================
            # FLASHCARDS
            # ====================================================

            with st.expander("🃏 Flashcards"):

                for i, card in enumerate(
                    result.get("flashcards", []),
                    1
                ):
                    st.markdown(
                        f"**{i}. Q: "
                        f"{card.get('question', '')}**"
                    )

                    st.write(
                        f"**Answer:** "
                        f"{card.get('answer', '')}"
                    )

                    st.divider()


            # ====================================================
            # MCQ QUIZ
            # ====================================================

            st.subheader("📝 MCQ Quiz")

            mcqs = result.get(
                "mcq_quiz", []
            )

            if mcqs:

                answers = {}

                for i, mcq in enumerate(
                    mcqs,
                    1
                ):

                    st.markdown(
                        f"**Q{i}. "
                        f"{mcq.get('question', '')}**"
                    )

                    options = mcq.get(
                        "options",
                        []
                    )

                    answers[i] = st.radio(
                        "Choose an answer:",
                        options,
                        key=f"mcq_{i}"
                    )

                if st.button(
                    "✅ Check Quiz",
                    key="check_quiz"
                ):

                    score = 0

                    for i, mcq in enumerate(
                        mcqs,
                        1
                    ):
                        if (
                            answers.get(i)
                            == mcq.get(
                                "correct_answer"
                            )
                        ):
                            score += 1

                    st.success(
                        f"🎯 Your Score: "
                        f"{score}/{len(mcqs)}"
                    )

                    for i, mcq in enumerate(
                        mcqs,
                        1
                    ):
                        st.write(
                            f"**Q{i} Explanation:** "
                            f"{mcq.get('explanation', '')}"
                        )


            # ====================================================
            # PRACTICE QUESTIONS
            # ====================================================

            with st.expander(
                "✍️ Practice Questions"
            ):

                for i, q in enumerate(
                    result.get(
                        "practice_questions",
                        []
                    ),
                    1
                ):

                    st.markdown(
                        f"**{i}. "
                        f"{q.get('question', '')}**"
                    )

                    st.write(
                        f"Difficulty: "
                        f"{q.get('difficulty', '')}"
                    )

                    st.write(
                        f"Answer: "
                        f"{q.get('answer', '')}"
                    )

                    st.divider()


            # ====================================================
            # EXAM TIPS
            # ====================================================

            with st.expander(
                "🎓 Exam Tips",
                expanded=True
            ):

                for tip in result.get(
                    "exam_tips", []
                ):
                    st.markdown(
                        f"- {tip}"
                    )


            # ====================================================
            # COMMON MISTAKES
            # ====================================================

            with st.expander(
                "⚠️ Common Mistakes"
            ):

                for mistake in result.get(
                    "common_mistakes", []
                ):
                    st.markdown(
                        f"- {mistake}"
                    )


            # ====================================================
            # FINAL REVISION
            # ====================================================

            with st.expander(
                "✅ Final Revision Checklist"
            ):

                for i, item in enumerate(
                    result.get(
                        "final_revision_checklist",
                        []
                    )
                ):
                    st.checkbox(
                        item,
                        key=f"revision_{i}"
                    )


            # ====================================================
            # FINAL TASK
            # ====================================================

            final_task = result.get(
                "final_task",
                {}
            )

            with st.expander(
                "🏆 Final Task",
                expanded=True
            ):

                st.markdown(
                    f"### "
                    f"{final_task.get('title', '')}"
                )

                st.write(
                    final_task.get(
                        "instructions",
                        ""
                    )
                )


            # ====================================================
            # DOWNLOAD
            # ====================================================

            st.download_button(
                "⬇️ Download Study Pack (JSON)",
                data=json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False
                ),
                file_name="study_pack.json",
                mime="application/json",
                use_container_width=True
            )


st.divider()

st.caption(
    "AI Study Pack Generator • Python + Groq + Streamlit"
)
