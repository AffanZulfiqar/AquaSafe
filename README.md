# AquaSafe AI

**AquaSafe AI** is a lightweight Python computer-vision application that analyzes photographs of water bodies and samples to provide a **visual-only water safety risk assessment** using **Google Gemini** through **LangChain LCEL Runnables**.

---

## ⚠️ Critical Safety Notice & Scope Limitations

> **IMPORTANT DISCLAIMER**: AquaSafe AI evaluates **visible environmental indicators only**.
> An image **CANNOT** detect:
> - Microorganisms, bacteria (e.g., *E. coli*), viruses, or parasites
> - Dissolved heavy metals (lead, arsenic, mercury)
> - Colorless or odorless chemical pollutants and pesticides
> - pH, salinity, or mineral toxicity
>
> A high `visually_safe` score **DOES NOT** mean the water is drinkable, potable, or safe for human consumption.
> This system is an **exploratory visual risk screening tool**, **NOT** a certified laboratory water quality test.

---

## Architecture

The entire inference pipeline is built strictly using **LangChain Expression Language (LCEL)** Runnables:

```text
Local Image (file path)
          ↓
   Image Processing
(Validation & Base64 Data URL)
          ↓
  Multimodal Prompt
(Environmental guidelines & image)
          ↓
  Google Gemini
(Multimodal LLM)
          ↓
  Structured Output
(Pydantic Schema Validation)
          ↓
   WaterAssessment
(Pydantic Object)
```

### Composable LCEL Pipeline
```python
water_assessment_chain = (
    image_processing_runnable
    | prompt_runnable
    | structured_llm_runnable
)
```

---

## Pydantic Output Schema

The output is strictly typed as a Pydantic object `WaterAssessment` containing **exactly three numeric percentage confidence scores (0.0 to 100.0)**:

| Field | Type | Description |
| :--- | :--- | :--- |
| `visually_safe` | `float` | Percentage confidence (0-100) that the water shows no obvious visible contamination indicators. *(Does NOT imply potability)* |
| `visually_risky` | `float` | Percentage confidence (0-100) that visible indicators suggest environmental contamination or poor water quality. |
| `image_quality` | `float` | Percentage confidence (0-100) that the image resolution, lighting, and focus are sufficient for meaningful visual assessment. |

*Note: Scores represent distinct confidence dimensions and do not artificially sum to 100.*

---

## Project Structure

```text
aquasafe-ai/
│
├── main.py              # CLI entry point to run inference
├── chain.py             # LCEL runnable pipeline and Gemini setup
├── schemas.py           # Pydantic output model (WaterAssessment)
├── image_utils.py       # Image validation & base64 encoding
├── requirements.txt     # Minimal dependencies
├── .env                 # API keys (ignored by git)
├── .env.example         # Template for environment configuration
├── .gitignore           # Git ignore rules
├── sample_water.jpg     # Sample test image
└── README.md            # Documentation and usage guide
```

---

## Installation

### 1. Clone or navigate to the directory
```bash
cd "d:/AI LABRATORY/AquaSafe AI/aquasafe-ai"
```

### 2. Activate your environment
If using Conda:
```bash
conda activate erly
```
Or create a standard virtual environment:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Environment Variable Setup

Copy `.env.example` to `.env` and insert your Google Gemini API key:

```bash
cp .env.example .env
```

Edit `.env`:
```ini
GOOGLE_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

---

## How to Run

### Run on the default sample image:
```bash
python main.py
```

### Run on a custom local image:
```bash
python main.py "path/to/your/water_image.jpg"
```

### Programmatic Python Usage:
```python
from chain import water_assessment_chain
from schemas import WaterAssessment

# Invoke with image path
result: WaterAssessment = water_assessment_chain.invoke("sample_water.jpg")

print(result)
# WaterAssessment(visually_safe=88.5, visually_risky=8.0, image_quality=94.0)

print(type(result))
# <class 'schemas.WaterAssessment'>

print(f"Safe Confidence: {result.visually_safe}%")
print(f"Risky Confidence: {result.visually_risky}%")
print(f"Image Quality:   {result.image_quality}%")
```

---

## Example Inputs & Outputs

### Example 1: Clear Mountain Stream (`sample_water.jpg`)
```json
{
  "visually_safe": 88.0,
  "visually_risky": 8.0,
  "image_quality": 95.0
}
```
*Interpretation: Water appears clear without visible debris or algae, but laboratory testing is still required before drinking.*

### Example 2: Polluted Industrial Drainage Canal
```json
{
  "visually_safe": 2.0,
  "visually_risky": 96.0,
  "image_quality": 90.0
}
```
*Interpretation: Strong visible indicators of pollution (oil slick, discoloration, sludge).*

### Example 3: Blurry or Underexposed Photo
```json
{
  "visually_safe": 0.0,
  "visually_risky": 0.0,
  "image_quality": 18.0
}
```
*Interpretation: Image quality is insufficient to draw reliable conclusions.*
