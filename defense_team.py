import os
from typing import List, Dict, Callable
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient

class DefenseAttorneyAgent:
    def __init__(self, gemini_api_key: str, tavily_api_key: str, status_callback: Callable[[str], None] = None):
        # Using Gemini (Default Model)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite", 
            google_api_key=gemini_api_key,
            temperature=0.5 # Higher temperature allows for more "creative" justification
        )
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        self.status_callback = status_callback
        
    def find_supporting_precedents(self, feature: str):
        """Search for successful examples or legal precedents that support a feature."""
        query = f"successful examples and benefits of {feature} in court proceedings"
        response = self.tavily_client.search(query=query, search_depth="advanced", max_results=3)
        return response.get('results', [])

    def defend_model(self, model_description: str, critique_points: str = None) -> str:
        """The Advocate's core logic: Defending the accused person."""
        if self.status_callback:
            self.status_callback("🛡️ The Defense is gathering evidence and precedents...")
        
        # Optional: Search for supporting data based on the model description
        support_data = self.find_supporting_precedents("defending an accused person in courtroom") # Example feature
        support_context = "\n".join([f"- {s['content']}" for s in support_data])

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a lead Defense Attorney specializing in protecting the legal rights of the accused.
            Your goal is to defend the accused against charges made by the prosecution.

            CRITICAL CONSTRAINTS:
            1. LENGTH: Your response must be STRICTLY between 300-350 words. Do not be too short, do not be too long.
            2. FOCUS: Discuss ONLY the case in question. Do not veer into generalities.
            3. STYLE: Prioritize FACTS over jargon, but maintain a professional legal tone.
            
            Your responsibilities:
            1. Protecting the legal and constitutional rights of the accused.
            2. Rebut specific prosecution points with logic and evidence (exhibits) if any. Do not make up any information. Work with given data.
            3. Analyse the case and challenge the evidence presented by the prosecution."""),
            ("user", f"""
            EVIDENCE / PRECEDENTS (EXHIBITS):
            {support_context}

            CLIENT'S PROPOSED CASE:
            {model_description}

            PROSECUTION'S CRITIQUE (IF ANY):
            {critique_points if critique_points else "No charges filed yet."}

            Provide a compelling legal defense of this case:""")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({})
            return response.content
        except Exception as e:
            return f"❌ Defense error: {str(e)}"

    def advocate(self, model_data: str, critique: str = None):
        """Main entry point for the agent."""
        if self.status_callback:
            self.status_callback("⚖️ Defense Attorney is preparing the closing statement...")
        
        result = self.defend_model(model_data, critique)
        
        if self.status_callback:
            self.status_callback("✅ Closing arguments ready.")
            
        return result

class DefenseStrategistAgent:
    def __init__(self, groq_api_key: str, tavily_api_key: str, status_callback: Callable[[str], None] = None):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            groq_api_key=groq_api_key,
            temperature=0.4 # Slightly creative to find unique angles
        )
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        self.status_callback = status_callback
        
    def find_legal_loopholes(self, prosecutor_point: str):
        """Search for legal precedents that contradict the prosecutor's claims."""
        query = f"legal exceptions and successful defenses against {prosecutor_point} in criminal law"
        response = self.tavily_client.search(query=query, search_depth="advanced", max_results=3)
        return response.get('results', [])

    def dismantle_prosecution(self, model_description: str, prosecutor_argument: str) -> str:
        """The Strategist's core logic: Destroying the Prosecutor's case."""
        if self.status_callback:
            self.status_callback("🕵️ Defense Strategist is analyzing the Prosecution's case...")
        
        # Step 1: Find counter-evidence against key prosecution points
        # Keep it simple: Assume the prosecutor attacks safety.
        counter_evidence = self.find_legal_loopholes("logic and reasoning of prosecution")
        loophole_context = "\n".join([f"- {s['content']}" for s in counter_evidence])

        # Step 2: Strategic Analysis
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Senior Legal Strategist for the Defense.
            Your ONLY job is to find the flaws, gaps, and legal errors in the Prosecutor's argument.
            You are NOT judging the model. You are attacking the Prosecutor's logic.
            
            Evaluate the Prosecutor's case based on:
            1. Logical Fallacies: Is the prosecutor using prejudiced attacks?
            2. Lack of Precedent: Is their argument purely speculative?
            3. Misinterpretation: Have they misunderstood the accused's intent?
            4. Counter-Strategy: Provide 3 specific legal arguments the Defense Lawyer should use in rebuttal.
            
            Be sharp, cynical, and 100% on the side of the Defense."""),
            ("user", f"""
            LEGAL LOOPHOLES & PRECEDENTS:
            {loophole_context}

            DEFENDANT'S CASE:
            {model_description}

            PROSECUTION'S ARGUMENT:
            {prosecutor_argument}

            Provide a strategic breakdown of the prosecution's weaknesses:""")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({})
            return response.content
        except Exception as e:
            return f"❌ Strategy error: {str(e)}"

    def strategize(self, model_data: str, prosecutor_arg: str):
        """Main entry point for the agent."""
        if self.status_callback:
            self.status_callback("🧠 Formulating defense strategy...")
        
        result = self.dismantle_prosecution(model_data, prosecutor_arg)
        
        if self.status_callback:
            self.status_callback("✅ Strategy briefing ready.")
            
        return result
