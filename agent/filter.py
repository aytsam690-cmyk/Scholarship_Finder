import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv

from agent.config import PROFILE

load_dotenv()

# Configure the LLM API (Google Generative AI / Gemini)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def evaluate_candidate(candidate):
    """
    Sends the candidate information to the LLM to evaluate relevance and eligibility.
    Returns a dictionary with parsed JSON fields or None if evaluation fails.
    """
    if not GEMINI_API_KEY:
        logging.error("GEMINI_API_KEY is not set. Cannot evaluate candidate.")
        return None

    try:
        # Default to standard model
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        logging.error(f"Failed to initialize Gemini model: {e}")
        return None

    title = candidate.get("title", "")
    url = candidate.get("url", "")
    raw_text = candidate.get("raw_text", "")
    
    # Truncate raw text defensively if extremely large
    truncated_text = raw_text[:25000]

    prompt = f"""
You are an AI assistant evaluating an opportunity for a Computer Science student.

Here is the candidate's profile:
{PROFILE}

Here is the opportunity to evaluate:
Title: {title}
URL: {url}
Raw Text:
{truncated_text}

Evaluate this opportunity across TWO dimensions: Relevance and Eligibility.

RELEVANCE RULES:
- AI/ML is the candidate's PRIMARY interest and should receive higher relevance.
- The candidate is a Computer Science student, so other CS fields are valid (e.g., Software Engineering, Computer Science research, Systems, Databases, Cloud Computing, Cybersecurity, Computer Networks, Operating Systems, Distributed Systems, Algorithms, Data Science, Backend development, Open Source, General programming).
- Do NOT reject an opportunity simply because it is not AI/ML.
- Keep relevant=true for legitimate CS opportunities even when the field is not AI/ML, provided the opportunity makes sense for a CS undergraduate.

ELIGIBILITY RULES:
- Pakistani applicants can apply, OR the program explicitly accepts international applicants.
- Undergraduate students are eligible.
- A 5th-semester CS student can reasonably apply.
- No obvious citizenship/residency restriction that excludes the candidate.
- No obvious university-specific restriction that excludes FAST-NUCES.
- Be conservative when eligibility information is unclear, but don't reject purely because nationality isn't explicitly mentioned if it's generally open to international students.

You MUST respond ONLY with a valid JSON object. Do not include markdown code fences (like ```json), just output the raw JSON. The JSON schema is:
{{
  "relevant": true or false,
  "eligible": true or false,
  "field": "AI/ML|Software Engineering|Research|Cybersecurity|Data Science|Cloud|Systems|Database|Networking|Open Source|General CS|Other",
  "relevance_level": "high|medium|low",
  "reasoning": "one sentence explaining the decision",
  "deadline_found": "date string or null",
  "urgency": "high|medium|low|unknown"
}}

Interpret relevance_level as:
- high: Strongly related to AI/ML or a major CS interest and useful for the candidate.
- medium: A legitimate CS opportunity that is relevant but not directly aligned with the candidate's primary AI/ML interests.
- low: Only weakly connected to the candidate's CS background.

Interpret urgency as:
- high = deadline within approximately 2 weeks or a rolling opportunity with limited slots
- medium = deadline is approaching but not extremely soon
- low = deadline is comfortably far away
- unknown = deadline cannot be determined
"""
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
            )
        )
        
        response_text = response.text.strip()
        
        # Parse defensively: strip markdown fences
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
            
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        response_text = response_text.strip()
        
        parsed_data = json.loads(response_text)
        return parsed_data
        
    except json.JSONDecodeError as e:
        logging.warning(f"Malformed JSON from LLM for candidate '{title}': {e}. Response was: {response_text}")
        return None
    except Exception as e:
        logging.warning(f"Error calling LLM for candidate '{title}': {e}")
        return None

def filter_candidates(candidates):
    """
    Takes a list of raw candidates, evaluates each with the LLM, 
    and returns a list of enriched candidates that are both relevant and eligible.
    """
    filtered = []
    
    for i, candidate in enumerate(candidates, 1):
        logging.info(f"Evaluating candidate {i}/{len(candidates)}: {candidate.get('title', 'Unknown')}")
        evaluation = evaluate_candidate(candidate)
        
        if not evaluation:
            continue
            
        # Enrich candidate
        enriched_candidate = candidate.copy()
        enriched_candidate.update(evaluation)
        
        is_relevant = evaluation.get("relevant", False)
        is_eligible = evaluation.get("eligible", False)
        
        if is_relevant and is_eligible:
            filtered.append(enriched_candidate)
        else:
            logging.info(f"  Rejected: relevant={is_relevant}, eligible={is_eligible}")
            logging.info(f"  Reasoning: {evaluation.get('reasoning', 'None provided')}")
            
    return filtered
