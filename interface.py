import streamlit as st
import time
import os
import random
from utils import generate_content

# Page Config
st.set_page_config(page_title="Legal Debate Simulation", layout="wide")

# Classes
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
        return generate_content(prompt)

class Debater:
    def __init__(self, role, case_summary):
        self.role = role # "Advocate" or "Prosecutor"
        self.case_summary = case_summary

    def generate_argument(self, history, round_num):
        prompt = f"""
        You are the {self.role} in a legal debate. 
        Case Summary: {self.case_summary}
        
        Previous Debate History:
        {history}
        
        This is Round {round_num}. Present your arguments to support your side.
        Be persuasive, logical, and cite legal principles if applicable.
        """
        return generate_content(prompt)

    def revise_argument(self, original_argument, critic_report):
        prompt = f"""
        You are the {self.role}. 
        Your original argument was: 
        {original_argument}
        
        The Critic found the following flaws:
        {critic_report}
        
        Please revise your argument to address these flaws and strengthen your position.
        """
        return generate_content(prompt)

class Critic:
    def __init__(self, side):
        self.side = side # Critic for Side A or Side B

    def analyze_argument(self, opponent_argument, case_summary):
        prompt = f"""
        You are a legal critic for {self.side}.
        Case Summary: {case_summary}
        
        Opponent's Argument:
        {opponent_argument}
        
        Analyze this argument for logical fallacies, weak evidence, and legal gaps.
        Output a structured flaw report.
        """
        return generate_content(prompt)

class Judge:
    def __init__(self, case_summary):
        self.case_summary = case_summary

    def evaluate_round(self, round_history):
        prompt = f"""
        You are the Judge in this legal debate.
        Case Summary: {self.case_summary}
        
        Review the following debate round:
        {round_history}
        
        Provide:
        1. Confidence Score for Side A (0-100)
        2. Confidence Score for Side B (0-100)
        3. Agreement Level (Low/Medium/High) - how close the sides are to a resolution or if one side is clearly winning.
        4. Brief commentary on the arguments.
        
        Output in JSON format: {{ "side_a_score": int, "side_b_score": int, "agreement_level": "str", "commentary": "str" }}
        """
        # Note: In a real app, you'd want to parse this JSON strictly. 
        # For this prototype, we'll trust the LLM or basic parsing.
        return generate_content(prompt)

    def final_decision(self, full_history):
        prompt = f"""
        You are the Judge. The debate has concluded.
        Case Summary: {self.case_summary}
        
        Full Debate History:
        {full_history}
        
        Make a final decision. 
        If there is a clear winner, declare the verdict and reasons.
        If the disagreement is too high or evidence is insufficient, refuse to decide and issue a warning.
        """
        return generate_content(prompt)

# Sidebar
st.sidebar.title("Configuration")
num_rounds = st.sidebar.slider("Number of Debate Rounds", 1, 5, 3)
confidence_threshold = st.sidebar.slider("Confidence Threshold for Verdict", 50, 100, 80)

# Main Interface
st.title("⚖️ AI Legal Debate Simulation")
st.markdown("### Agentic Workflow: Advocate vs. Prosecutor with Critics and Judge")

if "history" not in st.session_state:
    st.session_state.history = []
if "case_summary" not in st.session_state:
    st.session_state.case_summary = None

case_input = st.text_area("Enter Case Description / Facts", height=200, placeholder="Type the case details here...")

if st.button("Start Simulation"):
    if not case_input:
        st.warning("Please enter a case description.")
    else:
        with st.spinner("Analyzing Case..."):
            case_manager = CaseManager(case_input)
            summary = case_manager.summarize_case()
            st.session_state.case_summary = summary
            st.session_state.history = [] # Reset history
            
        st.subheader("Case Summary")
        st.write(summary)
        
        # Initialize Agents
        advocate = Debater("Advocate (Side A)", summary)
        prosecutor = Debater("Prosecutor (Side B)", summary)
        critic_for_a = Critic("Side A's Critic") # Critiques B
        critic_for_b = Critic("Side B's Critic") # Critiques A
        judge = Judge(summary)
        
        debate_history_text = ""
        
        progress_bar = st.progress(0)
        
        for r in range(num_rounds):
            st.markdown(f"---")
            st.subheader(f"Round {r+1}")
            
            # 1. Advocate Argues
            with st.spinner(f"Round {r+1}: Advocate is arguing..."):
                adv_arg = advocate.generate_argument(debate_history_text, r+1)
            
            # 2. Critic for B analyzes Advocate
            with st.spinner(f"Round {r+1}: Prosecutor's Critic is analyzing..."):
                crit_b_report = critic_for_b.analyze_argument(adv_arg, summary)
            
            # 3. Advocate Revises (Optional step based on prompt, let's keep it simple: Critic output is shown)
            # In the prompt description: "critiques convey their info to the agent and the agent prepares revised arguments"
            # So let's implement the revision step immediately for a better flow.
            with st.spinner(f"Round {r+1}: Advocate is revising based on critique..."):
               adv_arg_revised = advocate.revise_argument(adv_arg, crit_b_report)

            st.chat_message("user", avatar="🧑‍⚖️").write(f"**Advocate (Side A):**\n\n{adv_arg_revised}")
            with st.expander("Show Critic Report against Advocate"):
                st.info(crit_b_report)
            
            debate_history_text += f"\nRound {r+1} - Advocate: {adv_arg_revised}\nCritic to Advocate: {crit_b_report}\n"

            # 4. Prosecutor Argues
            with st.spinner(f"Round {r+1}: Prosecutor is arguing..."):
                pros_arg = prosecutor.generate_argument(debate_history_text, r+1)
            
            # 5. Critic for A analyzes Prosecutor
            with st.spinner(f"Round {r+1}: Advocate's Critic is analyzing..."):
                crit_a_report = critic_for_a.analyze_argument(pros_arg, summary)

            # 6. Prosecutor Revises
            with st.spinner(f"Round {r+1}: Prosecutor is revising based on critique..."):
                pros_arg_revised = prosecutor.revise_argument(pros_arg, crit_a_report)
                
            st.chat_message("assistant", avatar="👮").write(f"**Prosecutor (Side B):**\n\n{pros_arg_revised}")
            with st.expander("Show Critic Report against Prosecutor"):
                st.info(crit_a_report)
                
            debate_history_text += f"\nRound {r+1} - Prosecutor: {pros_arg_revised}\nCritic to Prosecutor: {crit_a_report}\n"

            # 7. Judge Evaluates
            with st.spinner(f"Round {r+1}: Judge is evaluating..."):
                judge_eval = judge.evaluate_round(debate_history_text)
            
            st.success(f"**Judge's Evaluation (Round {r+1}):**\n\n{judge_eval}")
            debate_history_text += f"\nJudge's Eval: {judge_eval}\n"
            
            progress_bar.progress((r + 1) / num_rounds)

        # Final Decision
        st.markdown("---")
        st.subheader("Final Verdict")
        with st.spinner("Judge is making the final decision..."):
            final_verdict = judge.final_decision(debate_history_text)
        st.error(final_verdict)
