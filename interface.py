import streamlit as st
import time
import os
from dotenv import load_dotenv

# Import the actual agent teams
from defense_team import DefenseAttorneyAgent, DefenseStrategistAgent
from prosecution_team import ProsecutorAgent, ProsecutionStrategistAgent
from judge import JudgeAgent
from utils import generate_content # Keep for CaseManager initial summary

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="AI Legal Debate Simulation", layout="wide", page_icon="⚖️")

# --- INITIALIZATION ---
def get_api_keys():
    """Retrieve API keys from environment variables."""
    keys = {
        "gemini_1": os.getenv("GEMINI_API_KEY1"), # Defense Attorney
        "gemini_2": os.getenv("GEMINI_API_KEY2"), # Prosecutor
        "groq_1": os.getenv("GROQ_API_KEY1"),    # Defense Strategist
        "groq_2": os.getenv("GROQ_API_KEY2"),    # Prosecution Strategist
        "groq_3": os.getenv("GROQ_API_KEY3"),    # Judge
        "tavily": os.getenv("TAVILY_API_KEY")    # Judge & Teams
    }
    
    # Check for missing keys
    missing = [k for k, v in keys.items() if not v]
    if missing:
        st.error(f"Missing API Keys in .env: {', '.join(missing)}")
        st.stop()
    return keys

# Initialize Agents
@st.cache_resource
def initialize_agents():
    keys = get_api_keys()
    
    # st.toast("Initializing Legal Teams...", icon="⚖️") # Removed to fix CacheReplayClosureError
    
    # Defense Team (Gemini for Advocate, Groq for Strategist)
    defense_attorney = DefenseAttorneyAgent(gemini_api_key=keys["gemini_1"], tavily_api_key=keys["tavily"])
    defense_strategist = DefenseStrategistAgent(groq_api_key=keys["groq_1"], tavily_api_key=keys["tavily"])
    
    # Prosecution Team (Gemini for Prosecutor, Groq for Strategist)
    prosecutor = ProsecutorAgent(gemini_api_key=keys["gemini_2"], tavily_api_key=keys["tavily"])
    prosecution_strategist = ProsecutionStrategistAgent(groq_api_key=keys["groq_2"], tavily_api_key=keys["tavily"])
    
    # Judge (Groq + Tavily)
    judge = JudgeAgent(groq_api_key=keys["groq_3"], tavily_api_key=keys["tavily"])
    
    return defense_attorney, defense_strategist, prosecutor, prosecution_strategist, judge

# Helper for Case Summary (using simple utility function)
class CaseManager:
    def __init__(self, case_description):
        self.case_description = case_description

    def summarize_case(self):
        prompt = f"""
        Analyze the following legal case description and extract key facts. 
        Provide a structured summary suitable for a legal debate.
        
        Case Description:
        {self.case_description}
        """
        # Fallback to utils.generate_content (which uses a default key/model)
        # Ideally this should also use one of the specific keys, but keeping as is for now
        # assuming utils.py is configured correctly.
        return generate_content(prompt)

# --- MAIN INTERFACE ---
st.title("⚖️ AI Courtroom: Prosecution vs Defense")
st.markdown("### Agentic Workflow with Strategists & Judicial Oversight")

# Sidebar Configuration
st.sidebar.title("Configuration")
# num_rounds = st.sidebar.slider("Number of Rounds", 1, 3, 1) # Removed for interactive rounds

# Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "case_summary" not in st.session_state:
    st.session_state.case_summary = None
if "run_simulation" not in st.session_state:
    st.session_state.run_simulation = False

# Input Area
case_input = st.text_area("Enter Case Details / Facts", height=150, placeholder="Describe the legal case, crime, or dispute here...")

if st.button("Start Court Session", type="primary"):
    if not case_input:
        st.warning("Please enter a case description.")
    else:
        st.session_state.run_simulation = True
        with st.spinner("Clerk is summarizing the case..."):
            case_manager = CaseManager(case_input)
            summary = case_manager.summarize_case()
            st.session_state.case_summary = summary
            st.session_state.history = []

if st.session_state.run_simulation and st.session_state.case_summary:
    st.success("Case Docket Created")
    with st.expander("View Case Summary", expanded=True):
        st.write(st.session_state.case_summary)
    
    # Load Agents
    defense_attorney, defense_strategist, prosecutor, prosecution_strategist, judge = initialize_agents()
    
    # Initialize Session State for Rounds
    if "rounds" not in st.session_state:
        st.session_state.rounds = []
    if "verdict_ready" not in st.session_state:
        st.session_state.verdict_ready = False
    if "verdict_text" not in st.session_state:
        st.session_state.verdict_text = None

    # Helper: Accumulate Briefs
    def get_briefs():
        defense_brief = ""
        prosecution_brief = ""
        defense_strategy = ""
        prosecution_strategy = ""
        
        for r in st.session_state.rounds:
            defense_brief += f"\nRound {r['round']}: {r['defense_arg']}\n"
            prosecution_brief += f"\nRound {r['round']}: {r['prosecution_arg']}\n"
            defense_strategy += f"\nRound {r['round']}: {r['defense_strat']}\n"
            prosecution_strategy += f"\nRound {r['round']}: {r['prosecution_strat']}\n"
            
        return defense_brief, prosecution_brief, defense_strategy, prosecution_strategy

    # --- RENDER EXISTING ROUNDS ---
    for r_data in st.session_state.rounds:
        st.markdown("---")
        st.subheader(f"Session Round {r_data['round']}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏛️ Prosecution")
            with st.expander("View Prosecution Strategy (Internal)", expanded=False):
                st.info(r_data['prosecution_strat'])
            st.chat_message("assistant", avatar="⚖️").write(r_data['prosecution_arg'])
            
        with col2:
            st.markdown("### 🛡️ Defense")
            with st.expander("View Defense Strategy (Internal)", expanded=False):
                st.info(r_data['defense_strat'])
            st.chat_message("user", avatar="🛡️").write(r_data['defense_arg'])
            
        st.caption(f"End of Round {r_data['round']}.")

    # --- CONTROL FLOW ---
    
    # 1. Check if Verdict is Ready (Auto-Trigger)
    if not st.session_state.verdict_ready and st.session_state.rounds:
        d_brief, p_brief, _, _ = get_briefs()
        if judge.has_sufficient_evidence(d_brief, p_brief):
            st.session_state.verdict_ready = True
            st.info("🧑‍⚖️ The Judge has heard enough evidence to render a verdict.")
            st.rerun()

    # 2. Action Buttons
    if not st.session_state.verdict_ready:
        col_next, col_verdict = st.columns([1, 4])
        
        with col_next:
            if st.button("Next Round ➡️", type="primary"):
                round_num = len(st.session_state.rounds) + 1
                
                # Get previous context
                d_brief, p_brief, _, _ = get_briefs()
                
                # Run Agents
                with st.spinner(f"Running Round {round_num}..."):
                    # Prosecution Turn
                    if round_num == 1:
                        p_strat = prosecution_strategist.strategize(st.session_state.case_summary, "Initial Opening Strategy")
                        p_arg = prosecutor.prosecute(st.session_state.case_summary, "Opening Statement")
                    else:
                        p_strat = prosecution_strategist.strategize(st.session_state.case_summary, d_brief)
                        p_arg = prosecutor.prosecute(st.session_state.case_summary, d_brief)
                    
                    # Defense Turn
                    d_strat = defense_strategist.strategize(st.session_state.case_summary, p_arg)
                    d_arg = defense_attorney.advocate(st.session_state.case_summary, p_arg)
                    
                    # Save Round Data
                    st.session_state.rounds.append({
                        "round": round_num,
                        "prosecution_strat": p_strat,
                        "prosecution_arg": p_arg,
                        "defense_strat": d_strat,
                        "defense_arg": d_arg
                    })
                    st.rerun()
                    
        with col_verdict:
            if st.button("Show Verdict 🧑‍⚖️"):
                st.session_state.verdict_ready = True
                st.rerun()

    # --- FINAL VERDICT ---
    if st.session_state.verdict_ready:
        st.markdown("---")
        st.header("🧑‍⚖️ Final Verdict")
        
        if not st.session_state.verdict_text:
            d_brief, p_brief, d_strat, p_strat = get_briefs()
            with st.spinner("The Judge is deliberating (checking facts with Tavily)..."):
                verdict = judge.deliberate(
                    defense_brief=d_brief,
                    prosecution_brief=p_brief,
                    defense_strategy=d_strat,
                    prosecution_strategy=p_strat
                )
                st.session_state.verdict_text = verdict
                
        st.markdown(st.session_state.verdict_text)
        
        if st.button("Start New Session"):
            st.session_state.clear()
            st.rerun()
