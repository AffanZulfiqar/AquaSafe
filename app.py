import os
import sys
import json
import uuid
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional, List

os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
os.environ.setdefault("GLOG_minloglevel", "2")

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

try:
    from chain import water_assessment_chain
    AI_AVAILABLE = True
except Exception as e:
    AI_AVAILABLE = False
    print(f"[WARNING] AI chain unavailable: {e}")

from schemas import WaterAssessment, RiskLevel

app = FastAPI(title="AquaSafe AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

observations_db: List[dict] = []




@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/status")
async def status():
    api_key = os.getenv("GOOGLE_API_KEY", "")
    key_set = bool(api_key and api_key != "your_api_key_here")
    return {"ai_available": AI_AVAILABLE and key_set, "demo_mode": not (AI_AVAILABLE and key_set), "version": "1.0.0"}


@app.post("/api/assess")
async def assess_water(
    image: UploadFile = File(...),
    water_body: str = Form("stream"),
    citizen_observations: str = Form("[]"),
    location_name: str = Form(""),
    latitude: Optional[str] = Form(None),
    longitude: Optional[str] = Form(None),
):
    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(400, "Only JPG, PNG, and WebP images are supported.")

    obs_id = str(uuid.uuid4())[:8]
    ext = Path(image.filename).suffix or ".jpg"
    save_path = UPLOAD_DIR / f"{obs_id}{ext}"
    content = await image.read()
    with open(save_path, "wb") as f:
        f.write(content)

    try:
        citizen_obs = json.loads(citizen_observations)
    except Exception:
        citizen_obs = []

    if AI_AVAILABLE:
        try:
            result: WaterAssessment = water_assessment_chain.invoke(str(save_path))
            assessment = result.dict()
            # Convert enum to string for JSON
            if hasattr(assessment.get("risk_level"), "value"):
                assessment["risk_level"] = assessment["risk_level"].value
        except Exception as e:
            assessment = _demo_assessment(citizen_obs)
            assessment["_fallback_reason"] = str(e)
    else:
        assessment = _demo_assessment(citizen_obs)

    ai_detected = assessment.get("ai_detected_indicators", [])
    matched = [obs for obs in citizen_obs if obs in ai_detected]
    mismatched = [obs for obs in citizen_obs if obs not in ai_detected and obs not in ["nothing unusual", "unsure"]]
    mismatch_detected = len(mismatched) > 0

    mismatch_note = (
        f"The following reported observations could not be confidently verified: {', '.join(mismatched)}. Consider reviewing the image or requesting human verification."
        if mismatch_detected
        else "All citizen observations are consistent with AI findings."
    )

    validation = {
        "matched": matched,
        "mismatched": mismatched,
        "mismatch_detected": mismatch_detected,
        "mismatch_note": mismatch_note
    }

    obs_record = {
        "id": obs_id,
        "location": location_name or "Unknown Location",
        "lat": float(latitude) if latitude else None,
        "lng": float(longitude) if longitude else None,
        "water_body": water_body,
        "citizen_observations": citizen_obs,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "AI_SCREENED",
        "is_demo": False,
        "image_url": f"/uploads/{obs_id}{ext}",
        "assessment": assessment,
        "validation": validation,
        "reviewer_status": "AWAITING_VERIFICATION",
        "reviewer_notes": ""
    }
    observations_db.append(obs_record)

    return JSONResponse({"success": True, "observation_id": obs_id, "assessment": assessment, "validation": validation, "observation": obs_record})


def _demo_assessment(citizen_obs: list) -> dict:
    high_risk = ["foam", "dead fish", "sewage-like appearance", "unusual color"]
    elevated = ["floating waste", "oil/surface film", "algae"]
    detected = [o for o in citizen_obs if o in high_risk + elevated]
    high_count = sum(1 for o in citizen_obs if o in high_risk)

    if high_count >= 2:
        risk, safe, risky, conf = "HIGH", 8.0, 92.0, 88.0
    elif len(detected) >= 2:
        risk, safe, risky, conf = "ELEVATED", 20.0, 78.0, 82.0
    elif len(detected) == 1:
        risk, safe, risky, conf = "MODERATE", 52.0, 44.0, 75.0
    else:
        risk, safe, risky, conf = "LOW", 85.0, 10.0, 90.0

    stress_label = "significant" if risky > 60 else "minimal"
    eco_label = "potential ecosystem stress" if risky > 60 else "minimal visible ecosystem stress"

    return {
        "risk_level": risk,
        "visually_safe": safe,
        "visually_risky": risky,
        "image_quality": 85.0,
        "ai_confidence": conf,
        "visible_evidence": [f"{o} indicators detected" for o in detected[:3]] or ["no obvious visual indicators"],
        "ai_detected_indicators": detected,
        "description": f"Based on visual analysis, this water body shows {stress_label} visual ecosystem stress indicators.",
        "reasoning": "(Demo mode) Image quality was assessed. Citizen observations used to generate this simulated assessment. Add a Gemini API key for real AI analysis.",
        "uncertainty_note": "This is a demo assessment. Visual analysis cannot detect invisible contaminants. Laboratory testing required.",
        "recommended_action": "Request human environmental verification for confirmation.",
        "ecosystem_insight": f"Visual indicators suggest {eco_label}. Further investigation may be warranted.",
        "aquatic_life_note": "Conditions should be assessed by a qualified ecologist to determine impact on aquatic biodiversity.",
        "human_wellbeing_note": "Avoid contact with any water body showing visible stress indicators until verified by environmental authorities."
    }


@app.get("/api/observations")
async def get_observations():
    return JSONResponse({"observations": observations_db, "total": len(observations_db)})


@app.get("/api/observations/{obs_id}")
async def get_observation(obs_id: str):
    obs = next((o for o in observations_db if o["id"] == obs_id), None)
    if not obs:
        raise HTTPException(404, "Observation not found")
    return JSONResponse(obs)


@app.post("/api/observations/{obs_id}/review")
async def review_observation(obs_id: str, body: dict):
    obs = next((o for o in observations_db if o["id"] == obs_id), None)
    if not obs:
        raise HTTPException(404, "Observation not found")
    obs["reviewer_status"] = body.get("status", "AWAITING_VERIFICATION")
    obs["reviewer_notes"] = body.get("notes", "")
    obs["status"] = body.get("status", "AWAITING_VERIFICATION")
    return JSONResponse({"success": True, "observation": obs})


app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
