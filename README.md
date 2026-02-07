# ⚖️ AI Courtroom: Prosecution vs Defense

An interactive AI-powered simulation where intelligent agents debate legal cases, strategize, and receive verdicts from an AI Judge with real-time fact-checking.

## 🌟 Overview

This project simulates a courtroom trial where specialized AI agents take on the roles of:
-   **Defense Attorney**: Advocates for the accused/defendant using persuasive arguments and legal precedents.
-   **Prosecutor**: Represents the state/public interest, cross-examining the defense and presenting charges.
-   **Strategists**: Specialized agents for both sides that analyze the opponent's arguments and formulate counter-strategies.
-   **Judge**: An impartial arbiter that synthesizes arguments, fact-checks claims using Tavily Search, and renders a final verdict.

The simulation is built with **Streamlit** for the interface and uses **LangChain** to orchestrate agents powered by **Google Gemini** (Advocates) and **Groq Llama-3** (Strategists & Judge).

## ✨ Key Features

-   **Interactive Rounds**: Step through the trial round-by-round.
-   **Automatic Verdict**: The Judge automatically halts the debate if sufficient evidence is gathered.
-   **Real-time Fact-Checking**: The Judge uses Tavily (web search) to verify claims made by both sides.
-   **Strategic Depth**: Strategist agents analyze the opponent's case to brief the advocates before they speak.
-   **Role-Specific Personas**: Agents adhere to strict legal personas, terminology, and constraints.

## 🚀 Getting Started

### Prerequisites

-   Python 3.10+
-   API Keys for:
    -   Google Gemini (x2)
    -   Groq (x3)
    -   Tavily Search

### Installation

1.  **Clone the repository** (if applicable) or navigate to the project folder.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables**:
    Create a `.env` file in the root directory and add your API keys:
    ```env
    GEMINI_API_KEY1=your_key_here
    GEMINI_API_KEY2=your_key_here
    GROQ_API_KEY1=your_key_here
    GROQ_API_KEY2=your_key_here
    GROQ_API_KEY3=your_key_here
    TAVILY_API_KEY=your_key_here
    ```

### Usage

1.  **Run the Streamlit App**:
    ```bash
    streamlit run interface.py
    ```

2.  **Start a Session**:
    -   Enter a case description or legal dispute in the text area.
    -   Click **Start Court Session**.

3.  **Control the Trial**:
    -   Click **Next Round ➡️** to proceed with arguments and rebuttals.
    -   The Judge will check for sufficiency after each round.
    -   Click **Show Verdict 🧑‍⚖️** to force a judgment at any time.

## 📂 Project Structure

-   `interface.py`: Main application logic and UI.
-   `judge.py`: Implementation of the `JudgeAgent` (Llama-3 + Tavily).
-   `defense_team.py`: `DefenseAttorneyAgent` (Gemini) and `DefenseStrategistAgent` (Groq).
-   `prosecution_team.py`: `ProsecutorAgent` (Gemini) and `ProsecutionStrategistAgent` (Groq).
-   `utils.py`: Helper functions for model interaction.
-   `.env`: Configuration file for API keys.

## 🤖 Models Used

-   **Advocates**: `gemini-2.5-flash-lite` (Chosen for speed and creativity)
-   **Strategists & Judge**: `llama-3.3-70b-versatile` (Chosen for reasoning capability)
