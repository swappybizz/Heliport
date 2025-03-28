import streamlit as st
from pymongo import MongoClient
import time

# MongoDB Atlas URI
MONGO_URI = st.secrets["MONGOURI"]
client = MongoClient(MONGO_URI)
db = client["code_db"]
codes_collection = db["codes"]
submits_collection = db["submits"]

# Hide the sidebar by default
st.set_page_config(initial_sidebar_state="collapsed")

if "validcode" not in st.session_state:
    st.session_state.validcode = False
if "isLoggedIn" not in st.session_state:
    st.session_state.isLoggedIn = False
if "chosen_lang" not in st.session_state:
    st.session_state.chosen_lang = False

# Keys to track survey start time for each language
if "nor_survey_start_time" not in st.session_state:
    st.session_state.nor_survey_start_time = None
if "eng_survey_start_time" not in st.session_state:
    st.session_state.eng_survey_start_time = None

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

# ------------------------------------
# CODE ENTRY & LANGUAGE SELECTION
# ------------------------------------
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
        # ------------------------------------
        # NORWEGIAN SURVEY
        # ------------------------------------
        if st.session_state.chosen_lang == "Norwegian":
            with st.form("topics_form"):
                st.header("Velg den eller de 2 påstandende som er mest relevant for deg")
                # Set survey start time if not already set
                if st.session_state.nor_survey_start_time is None:
                    st.session_state.nor_survey_start_time = time.time()

                # Question 1
                st.write("## 1. Arbeidstillatelse (AT)")
                q1_options = [
                    "Det hender at jeg velger å starte på en jobb uten godkjent arbeidstillatelse",
                    "Arbeidstillatelsen er ikke alltid tilgjengelig på arbeidsplassen",
                    "Det er ikke alltid at jeg forstår alt som står og forventes i arbeidstillatelsen",
                    "Arbeidstillatelsen er for omfattende og kompliser",
                    "Jeg har alltid arbeidstillatelsen synlig på arbeidsplassen",
                ]
                q1_selection = []
                for idx, opt in enumerate(q1_options):
                    if st.checkbox(opt, key=f"nor_q1_{idx}", value=False):
                        q1_selection.append(idx)
                st.write("___")

                # Question 2
                st.write("## 2. Arbeid i høyden og personlig verneutstyr (PVU)")
                q2_options = [
                    "Ved arbeid i høyden, over 2 meter, hender det at jeg ikke bruker fallsikring",
                    "Det hender at jeg ikke velger riktig personlig verneutstyr",
                    "Jeg sikrer alltid at nødvendig sperring er på plass før jeg starter jobben",
                    "Jeg velger å sikre meg og alt verktøy som jeg bruker i høyden",
                ]
                q2_selection = []
                for idx, opt in enumerate(q2_options):
                    if st.checkbox(opt, key=f"nor_q2_{idx}", value=False):
                        q2_selection.append(idx)
                st.write("___")

                # Question 3
                st.write("## 3. Orden og Ryddighet")
                q3_options = [
                    "Standard på Orden og Renhold på min arbeidsplass er tilfredsstillende",
                    "Jeg kan gjøre mer for å opprettholde ønsket standard",
                    "Jeg vil alltid rydde selv eller si ifra når standarden ikke er god nok",
                    "Det er FOR MYE fokus på Orden og Ryddighet",
                ]
                q3_selection = []
                for idx, opt in enumerate(q3_options):
                    if st.checkbox(opt, key=f"nor_q3_{idx}", value=False):
                        q3_selection.append(idx)
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
                q4_selection = []
                for idx, opt in enumerate(q4_options):
                    if st.checkbox(opt, key=f"nor_q4_{idx}", value=False):
                        q4_selection.append(idx)
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
                q5_selection = []
                for idx, opt in enumerate(q5_options):
                    if st.checkbox(opt, key=f"nor_q5_{idx}", value=False):
                        q5_selection.append(idx)

                if st.form_submit_button("Send inn", use_container_width=True):
                    elapsed = time.time() - st.session_state.nor_survey_start_time
                    if elapsed < 180:
                        st.toast("Vennligst bruk minst 180 sekunder på å lese spørsmålene for best mulig forståelse.", icon="❗")
                    elif (len(q1_selection) == 0 or len(q2_selection) == 0 or 
                          len(q3_selection) == 0 or len(q4_selection) == 0 or 
                          len(q5_selection) == 0):
                        st.error("Vennligst velg minst ett alternativ for hvert spørsmål.")
                    elif (len(q1_selection) > 2 or len(q2_selection) > 2 or 
                          len(q3_selection) > 2 or len(q4_selection) > 2 or 
                          len(q5_selection) > 2):
                        st.error("Velg maks to alternativer per spørsmål.")
                    else:
                        submit_form(q1_selection, q2_selection, q3_selection, q4_selection, q5_selection)
                        st.success("Dine svar er sendt inn! Lykke til videre!")
                        time.sleep(5)
                        # Reset survey state
                        st.session_state.isLoggedIn = False
                        st.session_state.validcode = False
                        st.session_state.chosen_lang = False
                        st.session_state.nor_survey_start_time = None
                        st.rerun()

            with st.container(height=250, border=False):
                """"""
            if st.button(":red[Logg ut]", use_container_width=True):
                st.session_state.isLoggedIn = False
                st.session_state.validcode = False
                st.session_state.chosen_lang = False
                st.session_state.nor_survey_start_time = None
                st.success("Logget ut!")
                time.sleep(2)
                st.rerun()

        # ------------------------------------
        # ENGLISH SURVEY
        # ------------------------------------
        else:
            with st.form("topics_form"):
                st.header("Please choose one or two most relevant statements for you:")
                if st.session_state.eng_survey_start_time is None:
                    st.session_state.eng_survey_start_time = time.time()

                # Question 1
                st.write("### 1. Work permit (AT)")
                q1_options = [
                    "It happens that I choose to start a job without an approved work permit",
                    "The work permit is not always available at the workplace",
                    "It is not always that I understand everything that is stated and expected in the work permit",
                    "The work permit is too comprehensive and complicated",
                    "I always have the work permit visible at the workplace",
                ]
                q1_selection = []
                for idx, opt in enumerate(q1_options):
                    if st.checkbox(opt, key=f"eng_q1_{idx}", value=False):
                        q1_selection.append(idx)
                st.write("_____")

                # Question 2
                st.write("### 2. Work at height and personal protective equipment (PPE)")
                q2_options = [
                    "When working at height, over 2 metres, it happens that I do not use fall protection",
                    "Sometimes I don't choose the right personal protective equipment",
                    "I always ensure that the necessary blocking is in place before I start the job",
                    "I choose to secure myself and all tools that I use at height",
                ]
                q2_selection = []
                for idx, opt in enumerate(q2_options):
                    if st.checkbox(opt, key=f"eng_q2_{idx}", value=False):
                        q2_selection.append(idx)
                st.write("_____")

                # Question 3
                st.write("### 3. Order and Tidiness")
                q3_options = [
                    "The standard of order and cleanliness at my workplace is satisfactory",
                    "I can do more to maintain the desired standard",
                    "I will always clean up myself or speak up when the standard is not good enough",
                    "There is TOO MUCH focus on Order and Tidiness",
                ]
                q3_selection = []
                for idx, opt in enumerate(q3_options):
                    if st.checkbox(opt, key=f"eng_q3_{idx}", value=False):
                        q3_selection.append(idx)
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
                q4_selection = []
                for idx, opt in enumerate(q4_options):
                    if st.checkbox(opt, key=f"eng_q4_{idx}", value=False):
                        q4_selection.append(idx)
                st.write("_____")

                # Question 5
                st.write("### 5. The 9 life-saving safety rules")
                q5_options = [
                    "I am an active user of the rules",
                    "Not sure what these rules entail",
                    "These rules are rarely used in our workplace",
                    "I can do more to comply with these rules",
                    "We in the work team always discuss which life-saving rule is relevant for this work permit.",
                ]
                q5_selection = []
                for idx, opt in enumerate(q5_options):
                    if st.checkbox(opt, key=f"eng_q5_{idx}", value=False):
                        q5_selection.append(idx)

                if st.form_submit_button("Submit", use_container_width=True):
                    elapsed = time.time() - st.session_state.eng_survey_start_time
                    if elapsed < 180:
                        st.toast("Please spend at least 180 seconds reviewing the questions for best understanding.", icon="❗")
                    elif (len(q1_selection) == 0 or len(q2_selection) == 0 or 
                          len(q3_selection) == 0 or len(q4_selection) == 0 or 
                          len(q5_selection) == 0):
                        st.error("Please select at least one option per question.")
                    elif (len(q1_selection) > 2 or len(q2_selection) > 2 or 
                          len(q3_selection) > 2 or len(q4_selection) > 2 or 
                          len(q5_selection) > 2):
                        st.error("Please select a maximum of two options per question.")
                    else:
                        submit_form(q1_selection, q2_selection, q3_selection, q4_selection, q5_selection)
                        st.success("Submitted successfully! Logging you out and resetting page now")
                        time.sleep(5)
                        st.session_state.isLoggedIn = False
                        st.session_state.validcode = False
                        st.session_state.chosen_lang = False
                        st.session_state.eng_survey_start_time = None
                        st.rerun()
            with st.container(height=250, border=False):
                """"""
            if st.button(":red[Log out]", use_container_width=True):
                st.session_state.isLoggedIn = False
                st.session_state.validcode = False
                st.session_state.chosen_lang = False
                st.session_state.eng_survey_start_time = None
                st.success("Logged out!")
                st.rerun()
