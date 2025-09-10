import streamlit as st
import os
import asyncio
from dotenv import load_dotenv
import hashlib
from agents import Agent, Runner
from pydantic import BaseModel
from prompt import instructions

# Load .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in .env file")
else:
    os.environ["OPENAI_API_KEY"] = api_key


# Define structured output
class BusinessInfo(BaseModel):
    business_name: str
    industry: str
    budget: str
    website: str
    social_platforms: str
    business_goals: str
    target_audience: str
    content_creation: str
    additional_info: str


QUESTIONS = [
    "What's your business name and location?",
    "Do you have any physical out or you are only online ?",
    "Where are your customers mostly located?",
    "What’s your main goal with Instagram & Facebook?",
    "How would you describe your brand’s vibe?",
    "What kind of posts do you want to see more of?",
    "Is there any brand/page you love and want us to take inspiration from?(mention competitors provide links to AI )",
    "Do you already have a logo & brand colors?",
    "Any specific requirements, challenges, or additional information?"
]


# Agents
marketing_plan_agent = Agent(
    name="Marketing Plan Generator",
    instructions=instructions
)


# Streamlit UI
st.title("📊 Ecommerce Social Media Planner")

# Reset session when QUESTIONS change
questions_hash = hashlib.md5("".join(QUESTIONS).encode()).hexdigest()
if st.session_state.get("questions_hash") != questions_hash:
    st.session_state.clear()
    st.session_state.questions_hash = questions_hash
    st.session_state.step = 0
    st.session_state.answers = {}

# Step-by-step intake
if st.session_state.step < len(QUESTIONS):
    q = QUESTIONS[st.session_state.step]
    st.write(f"**Q{st.session_state.step+1}: {q}**")

    answer = st.text_input("Your answer:", key=f"answer_{st.session_state.step}")

    if st.button("Next"):
        if answer.strip():
            st.session_state.answers[q] = answer.strip()
            st.session_state.step += 1
            st.rerun()

# All questions answered → build BusinessInfo and generate plan
else:
    st.success("✅ All business info collected!")
    st.json(st.session_state.answers)

    if st.button("Generate Marketing Plan"):
        business_info = BusinessInfo(
            business_name=st.session_state.answers[QUESTIONS[0]],
            industry=st.session_state.answers[QUESTIONS[1]],
            budget=st.session_state.answers[QUESTIONS[2]],
            website=st.session_state.answers[QUESTIONS[3]],
            social_platforms=st.session_state.answers[QUESTIONS[4]],
            business_goals=st.session_state.answers[QUESTIONS[5]],
            target_audience=st.session_state.answers[QUESTIONS[6]],
            content_creation=st.session_state.answers[QUESTIONS[7]],
            additional_info=st.session_state.answers[QUESTIONS[8]],
        )

        with st.spinner("Generating your marketing plan..."):
            result = asyncio.run(
                Runner.run(marketing_plan_agent, str(business_info.dict()))
            )

        st.subheader("📈 Social Media Marketing Plan")
        st.write(result.final_output)

# Always show restart option
if st.button("🔄 Start Over"):
    st.session_state.clear()
    st.rerun()
