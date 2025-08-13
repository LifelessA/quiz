import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime, timedelta
import time

# Create folder for uploaded tests
os.makedirs("uploaded_tests", exist_ok=True)

# Initialize session state
def init_session_state():
    if "current_screen" not in st.session_state:
        st.session_state.current_screen = "home"
    if "selected_test" not in st.session_state:
        st.session_state.selected_test = None
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "test_started" not in st.session_state:
        st.session_state.test_started = False
    if "test_submitted" not in st.session_state:
        st.session_state.test_submitted = False
    if "timer" not in st.session_state:
        st.session_state.timer = 0
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "test_data" not in st.session_state:
        st.session_state.test_data = None
    if "available_tests" not in st.session_state:
        st.session_state.available_tests = ["Paper 10 (Default)"]
        # Load default test
        try:
            df = pd.read_csv("questions.csv")
            df.to_csv("uploaded_tests/Paper 10 (Default).csv", index=False)
        except:
            st.error("Default questions.csv file not found")
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True  # Default to dark mode

init_session_state()

# Helper function to map full answers to option letters
def map_answer_to_option(row, answer):
    # If answer is already A,B,C,D
    if answer in ['A', 'B', 'C', 'D']:
        return answer
    
    # Check all options to find match
    for option in ['A', 'B', 'C', 'D']:
        option_text = row.get(f'Option {option} (English)', '')
        if pd.notna(option_text) and str(option_text).strip() == str(answer).strip():
            return option
    
    # If no match, return original answer
    return answer

# Function to load available tests
def load_available_tests():
    test_files = [f for f in os.listdir("uploaded_tests") if f.endswith('.csv')]
    return ["Paper 10 (Default)"] + [f.replace('.csv', '') for f in test_files if f != "Paper 10 (Default).csv"]

# Function to save uploaded file
def save_uploaded_file(uploaded_file, custom_name):
    if uploaded_file is not None:
        file_path = os.path.join("uploaded_tests", f"{custom_name}.csv")
        df = pd.read_csv(uploaded_file)
        df.to_csv(file_path, index=False)
        return True
    return False

# Function to delete test
def delete_test(test_name):
    try:
        if test_name != "Paper 10 (Default)":
            os.remove(f"uploaded_tests/{test_name}.csv")
            return True
    except:
        pass
    return False

# Timer component
def timer_component():
    if st.session_state.timer > 0 and not st.session_state.test_submitted:
        elapsed = (datetime.now() - st.session_state.start_time).seconds
        remaining = max(0, st.session_state.timer * 60 - elapsed)
        
        if remaining <= 0:
            st.session_state.test_submitted = True
            return 0
        
        mins, secs = divmod(remaining, 60)
        st.progress(remaining / (st.session_state.timer * 60))
        st.caption(f"⏳ Time remaining: {mins:02d}:{secs:02d}")
        return remaining
    return None

# Home Screen
def home_screen():
    st.title("✈️ Airport Test Prep")
    
    # Theme toggle in sidebar
    with st.sidebar:
        st.subheader("App Settings")
        if st.toggle("☀️ Light Mode", value=not st.session_state.dark_mode, key="light_mode_toggle"):
            st.session_state.dark_mode = False
        else:
            st.session_state.dark_mode = True
        
        st.divider()
        st.subheader("Add New Test")
        custom_name = st.text_input("Test Name", "Paper")
        uploaded_file = st.file_uploader("Upload CSV Test File", type="csv")
        if st.button("📤 Add Test", use_container_width=True):
            if uploaded_file is not None and custom_name:
                if save_uploaded_file(uploaded_file, custom_name):
                    st.success("Test added successfully!")
                    st.session_state.available_tests = load_available_tests()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Error adding test")
    
    # Main content
    st.subheader("Available Tests")
    st.session_state.available_tests = load_available_tests()
    
    if not st.session_state.available_tests:
        st.info("No tests available. Upload a test using the sidebar.")
        return
    
    # Create responsive grid (2 columns on mobile)
    cols = st.columns(2)
    col_index = 0
    
    for test in st.session_state.available_tests:
        with cols[col_index]:
            with st.container(border=True):
                st.subheader(test)
                
                if st.button(f"▶️ Start Test", key=f"start_{test}", use_container_width=True):
                    st.session_state.selected_test = test
                    st.session_state.current_screen = "setup"
                    st.rerun()
                
                if test != "Paper 10 (Default)":
                    if st.button("🗑️ Delete", key=f"del_{test}", use_container_width=True):
                        if delete_test(test):
                            st.session_state.available_tests = load_available_tests()
                            st.rerun()
        
        col_index = (col_index + 1) % 2

# Test Setup Screen
def setup_screen():
    st.title("Test Setup")
    
    try:
        test_path = f"uploaded_tests/{st.session_state.selected_test}.csv"
        df = pd.read_csv(test_path)
        total_questions = len(df)
        
        with st.container(border=True):
            st.subheader(f"Configure: {st.session_state.selected_test}")
            
            with st.form("test_setup"):
                # Timer option
                enable_timer = st.checkbox("Enable Timer?", value=True)
                timer_minutes = 0
                if enable_timer:
                    timer_minutes = st.number_input("Test Duration (minutes)", 
                                                  min_value=1, max_value=120, value=20)
                
                # Questions selection
                num_questions = st.slider("Number of Questions", 
                                         min_value=10, 
                                         max_value=min(100, total_questions),
                                         value=min(20, total_questions))
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.form_submit_button("🚀 Start Test", use_container_width=True):
                        # Preprocess answers to ensure they're A,B,C,D format
                        for idx, row in df.iterrows():
                            answer = row['Correct Answer (English)']
                            df.at[idx, 'Correct Answer (English)'] = map_answer_to_option(row, answer)
                        
                        st.session_state.test_data = df.sample(n=num_questions).reset_index(drop=True)
                        st.session_state.user_answers = {i: None for i in range(num_questions)}
                        st.session_state.test_started = True
                        st.session_state.test_submitted = False
                        st.session_state.current_screen = "test"
                        st.session_state.current_question = 0
                        st.session_state.timer = timer_minutes if enable_timer else 0
                        st.session_state.start_time = datetime.now()
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("🏠 Back to Home", use_container_width=True):
                        st.session_state.current_screen = "home"
                        st.rerun()
        
    except Exception as e:
        st.error(f"Error loading test: {str(e)}")
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.current_screen = "home"
            st.rerun()

# Test Screen
def test_screen():
    if st.session_state.test_data is not None and not st.session_state.test_data.empty:
        df = st.session_state.test_data
        current = st.session_state.current_question
        total = len(df)
        
        # Mobile-friendly top bar
        top_cols = st.columns([2,1])
        with top_cols[0]:
            st.subheader(f"Question: {current+1}/{total}")
        with top_cols[1]:
            if st.session_state.timer > 0:
                remaining = timer_component()
                if remaining == 0:
                    st.session_state.test_submitted = True
        
        # Display question
        with st.container(border=True):
            st.markdown(f"**{df.iloc[current]['Question (English)']}**")
            st.caption(df.iloc[current]['Question (Hindi)'])
        
        # Display options
        options = ['A', 'B', 'C', 'D']
        option_texts = []
        for option in options:
            eng_text = df.iloc[current].get(f'Option {option} (English)', '')
            hin_text = df.iloc[current].get(f'Option {option} (Hindi)', '')
            display_text = f"{option}: {eng_text}"
            if hin_text and pd.notna(hin_text):
                display_text += f" ({hin_text})"
            option_texts.append(display_text)
        
        user_answer = st.radio("Select your answer:", 
                              option_texts,
                              index=options.index(st.session_state.user_answers[current]) 
                              if st.session_state.user_answers.get(current) in options else 0,
                              key=f"question_{current}")
        
        selected_option = user_answer[0]
        st.session_state.user_answers[current] = selected_option
        
        # Navigation buttons
        col1, col2 = st.columns([1,1])
        with col1:
            if current > 0:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.current_question -= 1
                    st.rerun()
            else:
                st.button("⬅️ Previous", disabled=True, use_container_width=True)
        
        with col2:
            if current < total - 1:
                if st.button("Next ➡️", use_container_width=True):
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("✅ Submit Test", use_container_width=True, type="primary"):
                    st.session_state.test_submitted = True
        
        # Auto-submit when time expires
        if st.session_state.test_submitted:
            st.session_state.current_screen = "results"
            st.rerun()
    else:
        st.error("No test data available")
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.current_screen = "home"
            st.rerun()

# Results Screen
def results_screen():
    st.title("📊 Test Results")
    df = st.session_state.test_data
    
    # Calculate score
    correct = 0
    for i, row in df.iterrows():
        user_ans = st.session_state.user_answers.get(i)
        correct_ans = row['Correct Answer (English)']
        
        # Map full answers to letters for comparison
        mapped_user_ans = map_answer_to_option(row, user_ans) if user_ans else None
        mapped_correct_ans = map_answer_to_option(row, correct_ans)
        
        if mapped_user_ans == mapped_correct_ans:
            correct += 1
    
    score = f"{correct}/{len(df)}"
    percentage = (correct / len(df)) * 100 if len(df) > 0 else 0
    
    # Score summary
    st.subheader("Test Summary")
    
    score_cols = st.columns(3)
    score_cols[0].metric("Total Questions", len(df))
    score_cols[1].metric("Correct Answers", correct)
    score_cols[2].metric("Your Score", f"{percentage:.1f}%")
    
    st.progress(percentage/100)
    
    # Performance visualization
    with st.expander("📈 Performance Analysis", expanded=True):
        chart_data = pd.DataFrame({
            'Result': ['Correct', 'Incorrect'],
            'Count': [correct, len(df) - correct]
        })
        st.bar_chart(chart_data.set_index('Result'))
    
    # Detailed review
    st.subheader("Detailed Review")
    
    for i, row in df.iterrows():
        with st.container(border=True):
            # Question
            st.markdown(f"**Q{i+1}: {row['Question (English)']}**")
            st.caption(row['Question (Hindi)'])
            
            user_answer = st.session_state.user_answers.get(i, "Not answered")
            correct_answer = row['Correct Answer (English)']
            
            # Map answers to letters if needed
            mapped_user_ans = map_answer_to_option(row, user_answer)
            mapped_correct_ans = map_answer_to_option(row, correct_answer)
            
            # Get option texts
            user_option_text = ""
            correct_option_text = ""
            
            if mapped_user_ans in ['A', 'B', 'C', 'D']:
                user_option_text = row.get(f'Option {mapped_user_ans} (English)', '')
            else:
                user_option_text = mapped_user_ans
                
            if mapped_correct_ans in ['A', 'B', 'C', 'D']:
                correct_option_text = row.get(f'Option {mapped_correct_ans} (English)', '')
            else:
                correct_option_text = mapped_correct_ans
            
            # User answer
            if mapped_user_ans == mapped_correct_ans:
                st.success(f"✔️ Your Answer: {mapped_user_ans} - {user_option_text}")
            else:
                st.error(f"❌ Your Answer: {mapped_user_ans} - {user_option_text if user_option_text else 'Not answered'}")
                st.info(f"💡 Correct Answer: {mapped_correct_ans} - {correct_option_text}")
    
    if st.button("🏠 Take Another Test", use_container_width=True, type="primary"):
        st.session_state.current_screen = "home"
        st.session_state.test_submitted = False
        st.session_state.test_started = False
        st.rerun()

# Main App Controller
def main():
    # Android-friendly settings
    st.set_page_config(
        page_title="Airport Test",
        page_icon="✈️",
        layout="centered",
        initial_sidebar_state="auto"
    )
    
    # Apply dark theme by default
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        /* Dark theme */
        :root {
            --primary: #2E7D32;
            --background: #121212;
            --secondary-background: #1E1E1E;
            --text: #FFFFFF;
            --accent: #4CAF50;
            --border: #424242;
        }
        html, body, .stApp {
            background-color: var(--background) !important;
            color: var(--text) !important;
        }
        .stContainer, .st-expander, .st-emotion-cache-1jicfl2 {
            background-color: var(--secondary-background) !important;
            border-color: var(--border) !important;
            color: var(--text) !important;
        }
        h1, h2, h3, h4, h5, h6, .stMarkdown, .stRadio > label, .stButton > button, .stTextInput > label, .stNumberInput > label, .stSlider > label, .stCheckbox > label, .stSelectbox > label {
            color: var(--text) !important;
        }
        .stButton > button {
            background-color: var(--primary) !important;
            border-color: var(--primary) !important;
            color: white !important;
        }
        .stButton > button:hover {
            background-color: #1B5E20 !important;
            border-color: #1B5E20 !important;
        }
        .stProgress > div > div > div {
            background-color: var(--primary) !important;
        }
        .stRadio [role=radiogroup] {
            background-color: var(--secondary-background);
        }
        .stRadio [role=radio] {
            color: var(--text);
        }
        .st-bb, .st-at, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al, .st-am, .st-an, .st-ao, .st-ap, .st-aq, .st-ar, .st-as {
            border-color: var(--border) !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        /* Light theme */
        :root {
            --primary: #2196F3;
            --background: #F5F5F5;
            --secondary-background: #FFFFFF;
            --text: #333333;
            --accent: #FF9800;
            --border: #E0E0E0;
        }
        html, body, .stApp {
            background-color: var(--background) !important;
            color: var(--text) !important;
        }
        .stContainer, .st-expander, .st-emotion-cache-1jicfl2 {
            background-color: var(--secondary-background) !important;
            border-color: var(--border) !important;
            color: var(--text) !important;
        }
        h1, h2, h3, h4, h5, h6, .stMarkdown, .stRadio > label, .stButton > button, .stTextInput > label, .stNumberInput > label, .stSlider > label, .stCheckbox > label, .stSelectbox > label {
            color: var(--text) !important;
        }
        .stButton > button {
            background-color: var(--primary) !important;
            border-color: var(--primary) !important;
            color: white !important;
        }
        .stButton > button:hover {
            background-color: #0D47A1 !important;
            border-color: #0D47A1 !important;
        }
        .stProgress > div > div > div {
            background-color: var(--primary) !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Hide streamlit branding
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        .stDeployButton {display: none !important;}
        .stRadio > div {flex-direction:column;}
        .stButton > button {
            transition: all 0.3s ease;
            border-radius: 8px;
            font-weight: bold;
        }
        .stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        @media (max-width: 768px) {
            .stButton > button {
                padding: 10px 5px;
                font-size: 14px;
            }
            .stRadio > label {
                padding: 10px 5px;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Screen routing
    if st.session_state.current_screen == "home":
        home_screen()
    elif st.session_state.current_screen == "setup":
        setup_screen()
    elif st.session_state.current_screen == "test":
        test_screen()
    elif st.session_state.current_screen == "results":
        results_screen()

if __name__ == "__main__":
    main()