import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# --- INITIAL SETUP & CONFIGURATION ---

# Create a folder for uploaded test files if it doesn't exist
os.makedirs("uploaded_tests", exist_ok=True)

# Set the page configuration for the Streamlit app. This should be the first Streamlit command.
st.set_page_config(
    page_title="AirPort Quest Prep",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- SESSION STATE INITIALIZATION ---

def init_session_state():
    """
    Initializes session state variables if they don't exist.
    This ensures that the app's state is preserved across reruns.
    """
    # Core app state
    if "current_screen" not in st.session_state:
        st.session_state.current_screen = "home"
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True

    # Test-related state
    if "selected_test" not in st.session_state:
        st.session_state.selected_test = None
    if "test_data" not in st.session_state:
        st.session_state.test_data = None
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "test_started" not in st.session_state:
        st.session_state.test_started = False
    if "test_submitted" not in st.session_state:
        st.session_state.test_submitted = False
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
        
    # Timer state
    if "timer_minutes" not in st.session_state:
        st.session_state.timer_minutes = 0
    if "start_time" not in st.session_state:
        st.session_state.start_time = None

    # Notes Mode state
    if "revealed_answers" not in st.session_state:
        st.session_state.revealed_answers = {}

    # Load the default test on first run
    if "available_tests" not in st.session_state:
        st.session_state.available_tests = []
        try:
            default_test_path = "questions.csv"
            target_path = "uploaded_tests/Mission Alpha (Default).csv"
            if os.path.exists(default_test_path):
                if not os.path.exists(target_path):
                    df = pd.read_csv(default_test_path)
                    df.to_csv(target_path, index=False)
            elif not os.path.exists(target_path):
                pd.DataFrame({
                    'Question (English)': ["What is the closest planet to the Sun?"], 
                    'Question (Hindi)': ["सूर्य के सबसे निकट का ग्रह कौन सा है?"],
                    'Option A (English)': ["Venus"], 'Option A (Hindi)': ["शुक्र"],
                    'Option B (English)': ["Mars"], 'Option B (Hindi)': ["मंगल"],
                    'Option C (English)': ["Mercury"], 'Option C (Hindi)': ["बुध"],
                    'Option D (English)': ["Earth"], 'Option D (Hindi)': ["पृथ्वी"],
                    'Correct Answer (English)': ["Mercury"]
                }).to_csv(target_path, index=False)

        except Exception as e:
            st.error(f"Could not load or create default mission file: {e}")

# Call the initialization function at the start of the script
init_session_state()


# --- HELPER & UTILITY FUNCTIONS ---

def load_available_tests():
    """Scans the 'uploaded_tests' directory and returns a list of available test names."""
    test_files = [f for f in os.listdir("uploaded_tests") if f.endswith('.csv')]
    test_names = sorted([f.replace('.csv', '') for f in test_files])
    default_test = "Mission Alpha (Default)"
    if default_test in test_names:
        test_names.remove(default_test)
        test_names.insert(0, default_test)
    return test_names

def save_uploaded_file(uploaded_file, custom_name):
    """Saves an uploaded CSV file to the 'uploaded_tests' directory."""
    if uploaded_file and custom_name:
        try:
            file_path = os.path.join("uploaded_tests", f"{custom_name}.csv")
            df = pd.read_csv(uploaded_file)
            df.to_csv(file_path, index=False)
            return True
        except Exception:
            return False
    return False

def delete_test(test_name):
    """Deletes a test file, preventing deletion of the default test."""
    if test_name != "Mission Alpha (Default)":
        try:
            os.remove(f"uploaded_tests/{test_name}.csv")
            return True
        except OSError:
            return False
    return False

def map_answer_to_option(row, answer):
    """Maps a full answer text to its corresponding option letter (A, B, C, D)."""
    if pd.isna(answer) or answer is None: return None
    answer_str = str(answer).strip()
    if answer_str in ['A', 'B', 'C', 'D']: return answer_str
    
    for option in ['A', 'B', 'C', 'D']:
        col = f'Option {option} (English)'
        if col in row and pd.notna(row[col]) and str(row[col]).strip() == answer_str:
            return option
    return answer

# --- UI & STYLING ---

def load_css():
    """Injects the custom CSS for the 'AirPort Quest' theme."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Exo+2:wght@400;600&display=swap');

        :root {
            --font-main: 'Exo 2', sans-serif;
            --font-title: 'Orbitron', sans-serif;
            --glow-primary: #00BFFF; /* DeepSkyBlue */
            --glow-secondary: #FF1493; /* DeepPink */
            --glow-success: #39FF14; /* Neon Green */
            --glow-error: #FF4500; /* OrangeRed */
            --bg-color: #000015;
            --text-color: #E0E0E0;
            --border-radius: 15px;
            --transition-speed: 0.4s;
        }

        @keyframes cosmic-background {
            0% { background-position: 0% 50%; }
            25% { background-position: 50% 100%; }
            50% { background-position: 100% 50%; }
            75% { background-position: 50% 0%; }
            100% { background-position: 0% 50%; }
        }

        .stApp {
            background: var(--bg-color);
            background-image: linear-gradient(135deg, #000015 0%, #020024 25%, #0b094e 50%, #FF1493 75%, #00BFFF 100%);
            background-size: 400% 400%;
            animation: cosmic-background 20s ease infinite;
            color: var(--text-color);
            font-family: var(--font-main);
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-title) !important;
            color: #FFFFFF !important;
            text-shadow: 0 0 5px var(--glow-primary);
        }

        /* Increase base font size for better readability */
        .stMarkdown, .stRadio > label, p, div, span {
            font-size: 1.1rem !important;
            /* Add text shadow for readability against bright backgrounds */
            text-shadow: 0 0 5px rgba(0,0,0,0.7);
        }
        
        .st-emotion-cache-1g6gooi { /* Metric value */
             font-size: 2rem !important;
        }
        
        #MainMenu, footer, .stDeployButton { visibility: hidden; }

        /* Glassmorphism Card Style */
        .glass-card {
            background: rgba(22, 27, 34, 0.6);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: var(--border-radius);
            padding: 25px;
            margin-bottom: 20px;
            transition: all var(--transition-speed);
        }
        .glass-card:hover {
            border: 1px solid rgba(0, 191, 255, 0.5);
            transform: scale(1.02);
        }
        .glass-card h3 {
            color: var(--glow-primary) !important;
            text-shadow: 0 0 8px var(--glow-primary);
        }

        /* Custom Button Styles with Glow */
        .stButton > button {
            width: 100%;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-family: var(--font-title);
            border: 1px solid var(--glow-primary) !important;
            background-color: rgba(0, 191, 255, 0.1) !important;
            color: var(--glow-primary) !important;
            transition: all var(--transition-speed) ease !important;
            box-shadow: 0 0 5px var(--glow-primary), inset 0 0 5px rgba(0, 191, 255, 0.5);
        }
        .stButton > button:hover {
            color: #FFFFFF !important;
            background-color: rgba(0, 191, 255, 0.3) !important;
            box-shadow: 0 0 15px var(--glow-primary), inset 0 0 10px rgba(0, 191, 255, 0.5);
            transform: scale(1.05);
        }
        
        /* Study Notes Button Style */
        .stButton > button.study-btn {
            border-color: var(--glow-success) !important;
            color: var(--glow-success) !important;
            background-color: rgba(57, 255, 20, 0.1) !important;
            box-shadow: 0 0 5px var(--glow-success), inset 0 0 5px rgba(57, 255, 20, 0.5);
        }
        .stButton > button.study-btn:hover {
            color: #000015 !important;
            background-color: var(--glow-success) !important;
            box-shadow: 0 0 15px var(--glow-success), inset 0 0 10px rgba(57, 255, 20, 0.5);
        }
        
        /* Styling for st.radio to look like our buttons */
        div[role="radiogroup"] {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        div[role="radiogroup"] > label {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: var(--text-color) !important;
            padding: 15px 20px !important;
            border-radius: 10px !important;
            transition: all var(--transition-speed) ease !important;
            cursor: pointer;
            font-family: var(--font-main);
        }
        div[role="radiogroup"] > label:hover {
            border-color: var(--glow-primary) !important;
            background-color: rgba(0, 191, 255, 0.2) !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
            transform: scale(1.02); /* Added scaling effect on hover */
        }
        /* Style for the selected radio button's label */
        div[data-baseweb="radio"] > div:first-child {
            display: none; /* Hide the default radio dot */
        }
        .st-emotion-cache-1f4bdo8:has(input:checked) {
            border-color: var(--glow-primary) !important;
            background-color: var(--glow-primary) !important;
            color: #000015 !important;
            font-weight: bold;
            box-shadow: 0 0 15px var(--glow-primary);
        }
        .st-emotion-cache-1f4bdo8:has(input:checked) span {
             text-shadow: none !important; /* Remove shadow from selected option for clarity */
        }

        /* Progress Bar */
        .stProgress > div > div > div {
            background-image: linear-gradient(90deg, var(--glow-secondary), var(--glow-primary));
        }
        
        /* Sidebar styling */
        .st-emotion-cache-16txtl3 {
            background: rgba(14, 17, 23, 0.8);
            backdrop-filter: blur(5px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)


# --- UI SCREENS ---

def home_screen():
    """Displays the main home screen with available missions."""
    st.title("🚀 AirPort Quest Prep")
    st.markdown("Welcome, Explorer! Choose your mission below to start your journey through the Destiny.")
    
    with st.sidebar:
        st.header("🌌 Mission Control")
        st.divider()
        st.header("Upload New Mission")
        with st.form("upload_form", border=False):
            custom_name = st.text_input("Enter Mission Name", "New Mission")
            uploaded_file = st.file_uploader("Upload Mission CSV File", type="csv")
            submitted = st.form_submit_button("🛰️ Add Mission", use_container_width=True)
            
            if submitted and uploaded_file and custom_name:
                if save_uploaded_file(uploaded_file, custom_name):
                    st.success("Mission data received!")
                    time.sleep(1); st.rerun()
                else:
                    st.error("Transmission error. Check data file.")

    st.header("Available Missions")
    available_tests = load_available_tests()
    
    if not available_tests:
        st.info("No missions available. Upload mission data via Mission Control.")
        return

    for test_name in available_tests:
        with st.container():
            st.markdown(f'<div class="glass-card"><h3>{test_name}</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Take Quiz", key=f"start_{test_name}"):
                    st.session_state.selected_test = test_name
                    st.session_state.current_screen = "setup"
                    st.rerun()
            with col2:
                if st.button("📖 Study Notes", key=f"notes_{test_name}"):
                    st.session_state.selected_test = test_name
                    st.session_state.current_screen = "notes"
                    st.session_state.revealed_answers = {} # Reset for new study session
                    st.rerun()
            
            if test_name != "Mission Alpha (Default)":
                st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
                if st.button("🗑️ Decommission", key=f"del_{test_name}", help="Permanently delete this mission"):
                    if delete_test(test_name):
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)


def setup_screen():
    """Displays the configuration screen for a selected mission."""
    st.title(f"⚙️ Mission Briefing: {st.session_state.selected_test}")
    
    try:
        test_path = f"uploaded_tests/{st.session_state.selected_test}.csv"
        df = pd.read_csv(test_path)
        total_questions = len(df)
    except Exception as e:
        st.error(f"Could not load mission data: {e}")
        if st.button("⬅️ Return to Hangar"): st.session_state.current_screen = "home"; st.rerun()
        return

    with st.container(border=False):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("test_setup_form"):
            st.subheader("Set Mission Parameters")
            
            num_questions = st.slider("Number of Questions", min_value=5, max_value=min(100, total_questions), value=min(20, total_questions), step=5)
            
            enable_timer = st.checkbox("Enable Mission Timer?", value=True)
            timer_minutes = 0
            if enable_timer:
                timer_minutes = st.number_input("Mission Duration (minutes)", min_value=1, max_value=120, value=20)

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🚀 Launch Mission!", use_container_width=True):
                    df_sampled = df.sample(n=num_questions).reset_index(drop=True)
                    st.session_state.test_data = df_sampled
                    st.session_state.user_answers = {i: None for i in range(num_questions)}
                    st.session_state.test_started = True
                    st.session_state.test_submitted = False
                    st.session_state.current_screen = "test"
                    st.session_state.current_question = 0
                    st.session_state.timer_minutes = timer_minutes if enable_timer else 0
                    st.session_state.start_time = datetime.now()
                    st.rerun()
            
            with col2:
                if st.form_submit_button("⬅️ Return to Hangar", use_container_width=True):
                    st.session_state.current_screen = "home"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def update_answer():
    """Callback function to update the user's answer in session state."""
    q_index = st.session_state.current_question
    widget_key = f"q_radio_{q_index}"
    selected_option_text = st.session_state.get(widget_key)
    if selected_option_text:
        selected_letter = selected_option_text.split(':')[0]
        st.session_state.user_answers[q_index] = selected_letter

def test_screen():
    """Displays the active test screen with questions and options."""
    if not st.session_state.get("test_started", False) or st.session_state.get("test_data") is None:
        st.error("Mission not initialized. Returning to hangar.")
        st.session_state.current_screen = "home"
        st.session_state.test_started = False
        time.sleep(2)
        st.rerun()
        return

    st.warning("Do not refresh this page, or your mission progress will be lost!", icon="⚠️")

    df = st.session_state.test_data
    current_idx = st.session_state.current_question
    total_questions = len(df)
    question_row = df.iloc[current_idx]

    if st.session_state.timer_minutes > 0:
        elapsed = (datetime.now() - st.session_state.start_time).seconds
        remaining = max(0, st.session_state.timer_minutes * 60 - elapsed)
        if remaining == 0 and not st.session_state.test_submitted:
            st.session_state.test_submitted = True; st.rerun()
        mins, secs = divmod(remaining, 60)
        st.caption(f"⏳ Time Warp Stabilizer: {mins:02d}:{secs:02d}")
        st.progress(remaining / (st.session_state.timer_minutes * 60))
    
    st.subheader(f"Log Entry {current_idx + 1} of {total_questions}")
    
    with st.container(border=True):
        st.markdown(f"**{question_row.get('Question (English)', 'N/A')}**")
        if pd.notna(question_row.get('Question (Hindi)')):
            st.caption(question_row['Question (Hindi)'])

    st.markdown("<br>", unsafe_allow_html=True)

    options_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    options_list = ['A', 'B', 'C', 'D']
    
    formatted_options = []
    for option in options_list:
        eng_text = question_row.get(f'Option {option} (English)', '')
        hin_text = question_row.get(f'Option {option} (Hindi)', '')
        display_text = f"{option}: {eng_text}"
        if pd.notna(hin_text) and hin_text:
            display_text += f" ({hin_text})"
        formatted_options.append(display_text)
    
    current_answer = st.session_state.user_answers.get(current_idx)
    current_index = options_map.get(current_answer)

    st.radio(
        "Select your response:", 
        formatted_options, 
        index=current_index, 
        label_visibility="collapsed",
        key=f"q_radio_{current_idx}",
        on_change=update_answer
    )
            
    st.markdown("<br>", unsafe_allow_html=True)

    nav_cols = st.columns([1, 1, 1])
    with nav_cols[0]:
        if st.button("⬅️ Previous Log", use_container_width=True, disabled=(current_idx == 0)):
            st.session_state.current_question -= 1; st.rerun()
    
    with nav_cols[1]:
        if st.button("🛑 Abort Mission", use_container_width=True):
            st.session_state.test_submitted = True
            st.rerun()

    with nav_cols[2]:
        if current_idx < total_questions - 1:
            if st.button("Next Log ➡️", use_container_width=True):
                st.session_state.current_question += 1; st.rerun()
        else:
            if st.button("✅ Transmit Logs", use_container_width=True):
                st.session_state.test_submitted = True; st.rerun()

    if st.session_state.test_submitted:
        st.session_state.current_screen = "results"; st.rerun()

def notes_screen():
    """Displays the notes/study mode screen."""
    st.title(f"📖 Study Notes: {st.session_state.selected_test}")

    if st.button("⬅️ Return to Hangar"):
        st.session_state.current_screen = "home"
        st.rerun()

    try:
        test_path = f"uploaded_tests/{st.session_state.selected_test}.csv"
        df = pd.read_csv(test_path)
    except Exception as e:
        st.error(f"Could not load mission data: {e}")
        return

    st.markdown("---")
    st.info("Click on any option to reveal the correct answer for that question.", icon="💡")
    st.markdown("---")

    for i, row in df.iterrows():
        with st.container(border=True):
            st.markdown(f"**Q{i+1}: {row.get('Question (English)', 'N/A')}**")
            if pd.notna(row.get('Question (Hindi)')):
                st.caption(f"({row.get('Question (Hindi)')})")

            st.markdown("<br>", unsafe_allow_html=True)

            cols = st.columns(2)
            options = ['A', 'B', 'C', 'D']
            for j, option in enumerate(options):
                with cols[j % 2]:
                    eng_text = row.get(f'Option {option} (English)', '')
                    hin_text = row.get(f'Option {option} (Hindi)', '')
                    display_text = f"{option}: {eng_text}"
                    if pd.notna(hin_text) and hin_text:
                        display_text += f" ({hin_text})"
                    
                    if st.button(display_text, key=f"note_q{i}_opt{option}", use_container_width=True):
                        st.session_state.revealed_answers[i] = True
                        st.rerun() 

            if st.session_state.revealed_answers.get(i):
                correct_ans_letter = map_answer_to_option(row, row.get('Correct Answer (English)'))
                
                correct_eng = row.get(f'Option {correct_ans_letter} (English)', 'N/A')
                correct_hin = row.get(f'Option {correct_ans_letter} (Hindi)', '')
                correct_display = f"{correct_eng}"
                if pd.notna(correct_hin) and str(correct_hin).strip(): 
                    correct_display += f" ({correct_hin})"
                
                st.success(f"💡 Correct Answer: {correct_ans_letter} - {correct_display}")

def results_screen():
    """Displays the test results, score, and detailed review."""
    st.title("📊 Mission Debriefing")
    df = st.session_state.test_data
    
    correct_count = 0
    for i, row in df.iterrows():
        user_ans = st.session_state.user_answers.get(i)
        correct_ans_text = row.get('Correct Answer (English)')
        correct_ans_letter = map_answer_to_option(row, correct_ans_text)
        if user_ans == correct_ans_letter: correct_count += 1
            
    total = len(df)
    percentage = (correct_count / total) * 100 if total > 0 else 0

    st.subheader("Performance Analysis")
    score_cols = st.columns(3)
    score_cols[0].metric("Total Logs", total)
    score_cols[1].metric("Correct Logs", correct_count)
    score_cols[2].metric("Mission Success", f"{percentage:.1f}%")
    st.progress(percentage / 100)
    
    if percentage >= 80:
        st.balloons(); st.success("Stellar performance, Explorer! You've conquered this sector.")
    elif percentage >= 50:
        st.warning("Good navigation. Some asteroid fields were tricky, but you made it.")
    else:
        st.error("Mission requires more training. Review the logs to prepare for the next attempt.")
        
    st.divider()

    st.subheader("Detailed Log Review")
    for i, row in df.iterrows():
        with st.container(border=True):
            st.markdown(f"**Log {i+1}: {row.get('Question (English)', 'N/A')}**")
            if pd.notna(row.get('Question (Hindi)')):
                st.caption(f"({row.get('Question (Hindi)')})")
            
            user_ans_letter = st.session_state.user_answers.get(i)
            correct_ans_letter = map_answer_to_option(row, row.get('Correct Answer (English)'))
            is_correct = (user_ans_letter == correct_ans_letter)
            
            if user_ans_letter:
                user_eng = row.get(f'Option {user_ans_letter} (English)', 'N/A')
                user_hin = row.get(f'Option {user_ans_letter} (Hindi)', '')
                user_display = f"{user_eng}"
                if pd.notna(user_hin) and str(user_hin).strip(): 
                    user_display += f" ({user_hin})"

                if is_correct:
                    st.success(f"✔️ Your Log: {user_ans_letter} - {user_display}")
                else:
                    st.error(f"❌ Your Log: {user_ans_letter} - {user_display}")
            else:
                st.warning("Log entry missing.")

            if not is_correct:
                correct_eng = row.get(f'Option {correct_ans_letter} (English)', 'N/A')
                correct_hin = row.get(f'Option {correct_ans_letter} (Hindi)', '')
                correct_display = f"{correct_eng}"
                if pd.notna(correct_hin) and str(correct_hin).strip(): 
                    correct_display += f" ({correct_hin})"
                st.info(f"💡 Correct Log: {correct_ans_letter} - {correct_display}")

    st.divider()
    if st.button("🚀 Start New Mission", use_container_width=True):
        for key in ["current_screen", "test_started", "test_submitted", "test_data", "user_answers", "revealed_answers"]:
            if key == "current_screen":
                st.session_state[key] = "home"
            else:
                st.session_state[key] = None if key in ["test_data"] else {}
        st.rerun()


# --- MAIN APP CONTROLLER ---

def main():
    """The main function that controls the app flow."""
    load_css()
    
    screen = st.session_state.current_screen
    if screen == "home": home_screen()
    elif screen == "setup": setup_screen()
    elif screen == "test": test_screen()
    elif screen == "notes": notes_screen()
    elif screen == "results": results_screen()

if __name__ == "__main__":
    main()
