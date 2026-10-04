# AquaSafe AI

**"Responsible AI for citizen-powered freshwater ecosystem assessment."**

AquaSafe AI is an explainable AI-assisted citizen-science platform that helps validate freshwater observations, assess visible ecosystem risks, and connect citizens with human environmental verification.

This project was built for the **IEEE OneAquaHealth Global Hackathon 2026**.

## Primary Track

**TRACK 3 — AI-SUPPORTED ASSESSMENT**

**Core Focus:** Using AI responsibly to support stream assessment without replacing human judgment.

Citizen observations of freshwater ecosystems can be inconsistent and error-prone. AquaSafe AI solves this by introducing a human-in-the-loop workflow:
1. **AI Prompts & Validation:** AI compares its own visual assessment against citizen reports to flag mismatches.
2. **Explainable AI:** AI produces a detailed breakdown of visible evidence, reasoning, and uncertainty.
3. **Human-in-the-Loop:** Every AI assessment is flagged for human environmental verification. AI provides decision support, but humans make the final judgment.

*Supporting Features:* The platform includes secondary features like a community dashboard and emerging concern pattern detection to prioritize verification (Track 2 / Track 6 elements), but the core product is built to address Track 3.

## Safety & Positioning

**CRITICAL LIMITATION:** AquaSafe AI is an **environmental screening tool**, not a drinking water safety tester.
- It evaluates **Visual Ecosystem Risk**.
- Visual AI **cannot** detect bacteria, viruses, heavy metals, pesticides, pH, salinity, or other invisible contaminants.
- The AI explicitly communicates this uncertainty and recommends appropriate human/laboratory verification.

## Architecture

1. **Citizen Input:** Citizen uploads an image and simple observations (e.g., "foam", "unusual color").
2. **Gemini Multimodal AI:** The image is processed through Google's Gemini 1.5 Flash multimodal model.
3. **Structured Output (Pydantic):** The AI outputs a strict structured assessment including independent risk scores, evidence lists, and reasoning.
4. **Validation Check:** The system cross-references citizen observations against AI-detected indicators, flagging mismatches (e.g., citizen reported oil, AI didn't detect it).
5. **Human Review:** The assessment enters a dashboard where environmental experts can confirm, dismiss, or request field testing based on the AI's evidence.
6. **One Health Insight:** The system generates insights connecting the visual state to ecosystem health, aquatic life, and human well-being.

## Technology Stack

- **Backend:** FastAPI, Python, LangChain
- **AI Model:** Google Gemini 1.5 Flash (via `langchain-google-genai`)
- **Validation:** Pydantic (Strict structured outputs)
- **Frontend:** Vanilla HTML/CSS/JavaScript (No complex build step, lightweight and fast)
- **Mapping:** Leaflet.js

## Installation

1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install fastapi uvicorn python-multipart
   ```
3. Copy `.env.example` to `.env` and add your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Running the Application

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

Then open your browser to `http://127.0.0.1:8000`.

## Demo Mode

If the application is run without a valid Google Gemini API key, it will automatically fall back to **Demo Mode**. 
In Demo Mode, the application uses local synthetic demonstration data and simulated AI assessments based on the citizen's input to demonstrate the platform's UI and human-in-the-loop workflows.
