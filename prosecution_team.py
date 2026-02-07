import os
from typing import List, Dict, Callable
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient

class ProsecutorAgent:
    def __init__(self, gemini_api_key: str, tavily_api_key: str, status_callback: Callable[[str], None] = None):
        # Using Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=gemini_api_key,
            temperature=0.5 # Higher temperature for creative prosecution
        )
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        self.status_callback = status_callback
        
    def find_legal_precedents(self, feature: str):
        """Search for legal precedents or regulations that might be violated."""
        query = f"legal risks and failure cases of {feature} in courthouses"
        response = self.tavily_client.search(query=query, search_depth="advanced", max_results=3)
        return response.get('results', [])

    def prosecute_model(self, model_description: str, defense_arguments: str = None) -> str:
        """The Prosecutor's core logic: attacking the accused of being guilty of the crime."""
        if self.status_callback:
            self.status_callback("⚖️ The Prosecution is preparing the indictment...")
        
        # Optional: Search for damaging data
        damage_data = self.find_legal_precedents("modern open-plan") 
        damage_context = "\n".join([f"- {s['content']}" for s in damage_data])

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Chief Prosecutor representing the Public Interest and Judicial Safety.
            Your goal is to cross-examine the defence's plea and explose flaws in the arguments being made.

            CRITICAL CONSTRAINTS:
            1. LENGTH: Your response must be STRICTLY between 300-350 words. Do not be too short, do not be too long.
            2. FOCUS: Discuss ONLY the case in question. Do not veer into generalities.
            3. STYLE: Be accusatory, sharp, and authoritative, but stick to the facts of the case.

            Your responsibilities:
            1. Opening Statement: Declare the defendend "guilty" of the accused crimes.
            2. Cross-Examination: Tear apart Defense arguments with logic.
            3. Cite Violations: Use provided context (exhibits) to show failures."""),
            ("user", f"""
            EVIDENCE OF FAILURES (EXHIBIT B):
            {damage_context}

            DEFENDANT'S PROPOSED CASE:
            {model_description}

            DEFENSE ARGUMENTS (IF ANY):
            {defense_arguments if defense_arguments else "The Defense has remained silent."}

            Prosecute this case immediately:""")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({})
            return response.content
        except Exception as e:
            return f"❌ Prosecution error: {str(e)}"

    def prosecute(self, model_data: str, defense: str = None):
        """Main entry point for the agent."""
        if self.status_callback:
            self.status_callback("📜 Prosecutor is filing charges...")
        
        result = self.prosecute_model(model_data, defense)
        
        if self.status_callback:
            self.status_callback("✅ Indictment filed.")
            
        return result

class ProsecutionStrategistAgent:
    def __init__(self, groq_api_key: str, tavily_api_key: str, status_callback: Callable[[str], None] = None):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            groq_api_key=groq_api_key,
            temperature=0.3 # Sharp, factual, and ruthless
        )
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        self.status_callback = status_callback
        
    def find_counter_evidence(self, defense_claim: str):
        """Search for evidence that disproves or weakens the defense's claim."""
        query = f"evidence against {defense_claim} and failures in construction"
        response = self.tavily_client.search(query=query, search_depth="advanced", max_results=3)
        return response.get('results', [])

    def shred_defense(self, model_description: str, defense_argument: str) -> str:
        """The Strategist's core logic: Dismantling the Defense's case."""
        if self.status_callback:
            self.status_callback("🕵️ Prosecution Strategist is reviewing the Defense's lies...")
        
        # Step 1: Find weakness in Defense
        # Assume Defense praises "innovation". Search for failures of that innovation.
        rebuttal_evidence = self.find_counter_evidence("unproven architectural innovations")
        rebuttal_context = "\n".join([f"- {s['content']}" for s in rebuttal_evidence])

        # Step 2: Ruthless Strategic Analysis
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Chief Prosecution Strategist.
            Your ONLY job is to destroy the credibility of the Defense Attorney.
            You are NOT judging the model. You are attacking the Defense's Argument.
            
            Evaluate the Defense's case based on:
            1. Emotional Manipulation: Is the defense using sob stories instead of facts?
            2. Safety Violations: Does the defense ignore public safety regulations?
            3. Cost: Is the defense hiding the true intents of the accused?
            4. Attack Plan: Provide 3 lethal questions the Prosecutor should ask on cross-examination.
            
            Be ruthless, precise, and completely intolerant of vague "visionary" talk."""),
            ("user", f"""
            DAMNING EVIDENCE (REBUTTAL):
            {rebuttal_context}

            DEFENDANT'S CASE:
            {model_description}

            DEFENSE ARGUMENT:
            {defense_argument}

            Provide a plan to crush the defense:""")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({})
            return response.content
        except Exception as e:
            return f"❌ Strategy error: {str(e)}"

    def strategize(self, model_data: str, defense_arg: str):
        """Main entry point for the agent."""
        if self.status_callback:
            self.status_callback("🧠 Formulating prosecution strategy...")
        
        result = self.shred_defense(model_data, defense_arg)
        
        if self.status_callback:
            self.status_callback("✅ Attack plan ready.")
            
        return result
