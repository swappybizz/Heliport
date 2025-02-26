import streamlit as st
from pymongo import MongoClient
import time

# MongoDB Atlas URI
MONGO_URI = st.secrets["MONGOURI"]
client = MongoClient(MONGO_URI)
db = client["code_db"]
codes_collection = db["codes"]
submits_collection = db["submits"]

# hide the sidebar by default
st.set_page_config(initial_sidebar_state="collapsed")

if "validcode" not in st.session_state:
    st.session_state.validcode = False

if "isLoggedIn" not in st.session_state:
    st.session_state.isLoggedIn = False

if "chosen_lang" not in st.session_state:
    st.session_state.chosen_lang = False

def submit_form(a1, a2, a3, a4, a5):
    answer_data = {
        "q1": a1,
        "q2": a2,
        "q3": a3,
        "q4": a4,
        "q5": a5
    }
    date_time = time.strftime("%Y-%m-%d %H:%M:%S")
    code = st.session_state.validcode["code"]
    data = {
        "code": code,
        "answers": answer_data,
        "date_time": date_time
    }
    submits_collection.insert_one(data)
    return st.toast("Submitted successfully!", icon=":material/thumb_up:")

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# if not signed in, show code input else show welcome message
if not st.session_state.isLoggedIn:
    st.write("Please enter the 4-digit code provided to you")
    with st.form("code_form"):
        code_input = st.text_input("Enter 4-digit code")
        if st.form_submit_button("Submit", use_container_width=True):
            try:
                code_int = int(code_input)
            except ValueError:
                st.error("Please enter a valid 4-digit code")
            else:
                code_doc = codes_collection.find_one({"code": code_int})
                if code_doc:
                    st.session_state.validcode = code_doc
                    st.session_state.isLoggedIn = True
                    st.rerun()
                else:
                    st.error("Invalid code. Please try again.")
else:
    if not st.session_state.chosen_lang:
        st.write("Please choose your preferred language")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Velg Norsk", use_container_width=True):
                st.session_state.chosen_lang = "Norwegian"
                st.rerun()
        with col2:
            if st.button("Choose English", use_container_width=True):
                st.session_state.chosen_lang = "English"
                st.rerun()
    else:
        if st.session_state.chosen_lang == "Norwegian":
            with st.form("topics_form"):
                st.header("Velg den eller de 2 påstandende som er mest relevant for deg")

                # Question 1
                st.write("## 1. Arbeidstillatelse (AT)")
                q1_options = [
                    "Det hender at jeg velger å starte på en jobb uten godkjent arbeidstillatelse",
                    "Arbeidstillatelsen er ikke alltid tilgjengelig på arbeidsplassen",
                    "Det er ikke alltid at jeg forstår alt som står og forventes i arbeidstillatelsen",
                    "Arbeidstillatelsen er for omfattende og kompliser",
                    "Jeg har alltid arbeidstillatelsen synlig på arbeidsplassen",
                ]
                q1 = st.radio("", options=q1_options, index=0)

                st.write("___")
                # Question 2
                st.write("## 2. Arbeid i høyden og personlig verneutstyr (PVU)")
                q2_options = [
                    "Ved arbeid i høyden, over 2 meter, hender det at jeg ikke bruker fallsikring",
                    "Det hender at jeg ikke velger riktig personlig verneutstyr",
                    "Jeg sikrer alltid at nødvendig sperring er på plass før jeg starter jobben",
                    "Jeg velger å sikre meg og alt verktøy som jeg bruker i høyden",
                ]
                q2 = st.radio("", options=q2_options, index=0)

                st.write("___")
                # Question 3
                st.write("## 3. Orden og Ryddighet")
                q3_options = [
                    "Standard på Orden og Renhold på min arbeidsplass er tilfredsstillende",
                    "Jeg kan gjøre mer for å opprettholde ønsket standard",
                    "Jeg vil alltid rydde selv eller si ifra når standarden ikke er god nok",
                    "Det er FOR MYE fokus på Orden og Ryddighet",
                ]
                q3 = st.radio("", options=q3_options, index=0)

                st.write("___")
                # Question 4
                st.write("## 4. Før Jobb Samtale/TBT – Tool Box Talk")
                q4_options = [
                    "Før jobb samtalen er lite brukt på vår arbeidsplass",
                    "Skjemaet er altfor komplisert",
                    "Jeg er en aktiv bruker av før jobb samtalen",
                    "Er ikke sikker på hva Før Jobb Samtalen innebærer",
                    "Jeg velger alltid å stoppe arbeid som er usikkert",
                ]
                q4 = st.radio("", options=q4_options, index=0)

                st.write("___")
                # Question 5
                st.write("## 5. De 9 livreddende sikkerhets reglene")
                q5_options = [
                    "Jeg er en aktiv bruker av reglene",
                    "Er ikke sikker på hva disse reglene innebærer",
                    "Disse reglene er lite brukt på vår arbeidsplass",
                    "Jeg kan gjøre mer for å etterleve disse reglene",
                    "Vi i arbeidslaget diskuterer alltid hvilken livreddende regel som er relevant for denne arbeidstillatelsen.",
                ]
                q5 = st.radio("", options=q5_options, index=0)

                if st.form_submit_button("Send inn", use_container_width=True):
                    data_q1 = q1_options.index(q1)
                    data_q2 = q2_options.index(q2)
                    data_q3 = q3_options.index(q3)
                    data_q4 = q4_options.index(q4)
                    data_q5 = q5_options.index(q5)
                    submit_form(data_q1, data_q2, data_q3, data_q4, data_q5)
                    st.success("Dine svar er sendt inn! Lykke til videre!")
                    time.sleep(5)
                    st.session_state.isLoggedIn = False
                    st.session_state.validcode = False
                    st.session_state.chosen_lang = False
                    st.rerun()

            with st.container(height=250, border=False):
                """"""
            if st.button(":red[Logg ut]", use_container_width=True):
                st.session_state.isLoggedIn = False
                st.session_state.validcode = False
                st.session_state.chosen_lang = False
                st.success("Logget ut!")
                time.sleep(2)
                st.rerun()

        else:
            with st.form("topics_form"):
                st.header("Please choose one or two most relevent statements for you.:")

                # Question 1
                st.write("### 1. Work permit (AT)")
                q1_options = [
                    "It happens that I choose to start a job without an approved work permit",
                    "The work permit is not always available at the workplace",
                    "It is not always that I understand everything that is stated and expected in the work permit",
                    "The work permit is too comprehensive and complicated",
                    "I always have the work permit visible at the workplace",
                ]
                q1 = st.radio("", options=q1_options, index=0)

                st.write("_____")
                # Question 2
                st.write("### 2. Work at height and personal protective equipment (PPE)")
                q2_options = [
                    "When working at height, over 2 metres, it happens that I do not use fall protection",
                    "Sometimes I don't choose the right personal protective equipment",
                    "I always ensure that the necessary blocking is in place before I start the job",
                    "I choose to secure myself and all tools that I use at height",
                ]
                q2 = st.radio("", options=q2_options, index=0)

                st.write("____")
                # Question 3
                st.write("### 3. Order and Tidiness")
                q3_options = [
                    "The standard of order and cleanliness at my workplace is satisfactory",
                    "I can do more to maintain the desired standard",
                    "I will always clean up myself or speak up when the standard is not good enough",
                    "There is TOO MUCH focus on Order and Tidiness",
                ]
                q3 = st.radio("", options=q3_options, index=0)

                st.write("___")
                # Question 4
                st.write("### 4. Before Job Conversation/TBT – Tool Box Talk")
                q4_options = [
                    "The conversation before work is little used in our workplace",
                    "The form is far too complicated",
                    "I am an active user of the pre-work conversation",
                    "Not sure what the Before Job Interview entails",
                    "I always choose to stop work that is uncertain",
                ]
                q4 = st.radio("", options=q4_options, index=0)

                st.write("____")
                # Question 5
                st.write("### 5. The 9 life-saving safety rules")
                q5_options = [
                    "I am an active user of the rules",
                    "Not sure what these rules entail",
                    "These rules are rarely used in our workplace",
                    "I can do more to comply with these rules",
                    "We in the work team always discuss which life-saving rule is relevant for this work permit.",
                ]
                q5 = st.radio("", options=q5_options, index=0)

                if st.form_submit_button("Submit", use_container_width=True):
                    data_q1 = q1_options.index(q1)
                    data_q2 = q2_options.index(q2)
                    data_q3 = q3_options.index(q3)
                    data_q4 = q4_options.index(q4)
                    data_q5 = q5_options.index(q5)
                    submit_form(data_q1, data_q2, data_q3, data_q4, data_q5)
                    st.success("Submitted successfully! Logging you out and resetting page now")
                    time.sleep(5)
                    st.session_state.isLoggedIn = False
                    st.session_state.validcode = False
                    st.session_state.chosen_lang = False
                    st.rerun()
            with st.container(height=250, border=False):
                """"""
            if st.button(":red[Log out]", use_container_width=True):
                st.session_state.isLoggedIn = False
                st.session_state.validcode = False
                st.session_state.chosen_lang = False
                st.success("Logged out!")
                st.rerun()
