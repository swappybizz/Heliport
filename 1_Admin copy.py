import streamlit as st
from pymongo import MongoClient
import pandas as pd
import altair as alt
import random
import datetime

# MongoDB Atlas URI
MONGO_URI = st.secrets["MONGOURI"]

client = MongoClient(MONGO_URI)
db = client["code_db"]
codes_collection = db["codes"]

# Ensure a TTL index on "expireAt" (MongoDB removes docs when expireAt <= now)
codes_collection.create_index("expireAt", expireAfterSeconds=0)

# Initialize login state if not already done
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
@st.fragment(run_every="10s")   
def get_stats():
    st.toast("Fetching latest statistics...", icon="🔄")
    submits_collection = db["submits"]
    # Fetch only survey submissions (documents with an 'answers' field)
    submissions = list(submits_collection.find({"answers": {"$exists": True}}))
    total_submissions = len(submissions)
    st.subheader(f"Total Submissions: {total_submissions}")

    if total_submissions == 0:
        st.info("No survey submissions available yet.")
    else:
        # Define the questions with their labels and options
        questions = {
            "q1": {
                "label": "1. Work permit (AT)",
                "options": [
                    "It happens that I choose to start a job without an approved work permit",
                    "The work permit is not always available at the workplace",
                    "It is not always that I understand everything that is stated and expected in the work permit",
                    "The work permit is too comprehensive and complicated",
                    "I always have the work permit visible at the workplace",
                ],
            },
            "q2": {
                "label": "2. Work at height and personal protective equipment (PPE)",
                "options": [
                    "When working at height, over 2 metres, it happens that I do not use fall protection",
                    "Sometimes I don't choose the right personal protective equipment",
                    "I always ensure that the necessary blocking is in place before I start the job",
                    "I choose to secure myself and all tools that I use at height",
                ],
            },
            "q3": {
                "label": "3. Order and Tidiness",
                "options": [
                    "The standard of order and cleanliness at my workplace is satisfactory",
                    "I can do more to maintain the desired standard",
                    "I will always clean up myself or speak up when the standard is not good enough",
                    "There is TOO MUCH focus on Order and Tidiness",
                ],
            },
            "q4": {
                "label": "4. Before Job Conversation/TBT – Tool Box Talk",
                "options": [
                    "The conversation before work is little used in our workplace",
                    "The form is far too complicated",
                    "I am an active user of the pre-work conversation",
                    "Not sure what the Before Job Interview entails",
                    "I always choose to stop work that is uncertain",
                ],
            },
            "q5": {
                "label": "5. The 9 life-saving safety rules",
                "options": [
                    "I am an active user of the rules",
                    "Not sure what these rules entail",
                    "These rules are rarely used in our workplace",
                    "I can do more to comply with these rules",
                    "We in the work team always discuss which life-saving rule is relevant for this work permit.",
                ],
            },
        }



        # Loop through each question and compute distribution of responses
        for q_key, q_data in questions.items():
            st.subheader(q_data["label"])
            # Initialize count for each option (using index as key)
            option_counts = {i: 0 for i in range(len(q_data["options"]))}

            # Aggregate answers from all submissions
            for submission in submissions:
                ans = submission.get("answers", {}).get(q_key)
                if ans is not None and ans in option_counts:
                    option_counts[ans] += 1

            # Prepare a DataFrame for visualization
            df = pd.DataFrame({
                "Option": [q_data["options"][i] for i in range(len(q_data["options"]))],
                "Count": [option_counts[i] for i in range(len(q_data["options"]))]
            })

            st.write(df)

            # Create a bar chart using Altair
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X("Option:N", sort=None, title="Answer Options"),
                y=alt.Y("Count:Q", title="Number of Responses"),
                tooltip=["Option", "Count"]
            ).properties(
                width=600,
                height=300
            )

            st.altair_chart(chart, use_container_width=True)

    

# Admin login in sidebar using Streamlit state
if not st.session_state.logged_in:
    st.sidebar.title("Admin Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == st.secrets["USERNAME"] and password == st.secrets["PASSWORD"]:
            st.session_state.logged_in = True
            st.sidebar.success("Logged in!")
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")
            st.stop()
else:
    st.sidebar.success("Logged in!")
# st.header("Active Codes")
codes = list(codes_collection.find())
now = datetime.datetime.now()
tab1, tab2 = st.tabs(["Codes","Statistics"])
with tab1:
    if not codes:
        st.info("No active codes.")
    else:
        for code in codes:
            code_expire = code["expireAt"]
            if now > code_expire:
                if st.session_state.logged_in:
                    st.warning(f"Code {code['code']} expired! Expire code now, DONOT KEEP EXPIRED CODES")
                else:
                    st.warning("Log in to see Codes")
            else:
                # if not logged in , dont show code
                if st.session_state.logged_in:
                    st.write(f"Code: {code['code']}\nExpires at: {code_expire}")
                else:
                    st.write("Code: ********Log In to see code ********")
            # disable = if not logged in
            if st.session_state.logged_in:
                if st.button(f"Expire Code {code['code']}", key=str(code["_id"])):
                    codes_collection.delete_one({"_id": code["_id"]})
                    st.rerun()
    if st.session_state.logged_in:
        if len(codes) < 4:
            if st.button("Generate Code Now"):
                new_code = random.randint(1000, 9999)
                while codes_collection.find_one({"code": new_code}):
                    new_code = random.randint(1000, 9999)
                expire_at = datetime.datetime.now() + datetime.timedelta(hours=1)
                codes_collection.insert_one({
                    "code": new_code,
                    "createdAt": datetime.datetime.now(),
                    "expireAt": expire_at
                })
                st.success(f"Generated code: {new_code}, expires at {expire_at}")
                st.rerun()
        else:
            st.warning("Maximum 4 active codes reached. Expire one before generating a new code.")
with tab2:
    st.header("Statistics Dashboard")
    # if not logged in show warning
    if not st.session_state.logged_in:
        st.warning("Login to view statistics")
    else:
        get_stats()


    
    