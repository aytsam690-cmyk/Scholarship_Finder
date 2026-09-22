import os
import json
import logging
import time
import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

from agent.config import PROFILE

load_dotenv()

# Configure the new google-genai client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

# gemini-3.5-flash-lite: https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite
MODEL = "gemini-3.5-flash-lite"


def evaluate_candidate(candidate):
    """
    Sends the candidate information to the LLM to evaluate relevance, eligibility,
    deadline status, legitimacy, and extract comprehensive details.
    Returns a dictionary with parsed JSON fields or None if evaluation fails.
    """
    if not client:
        logging.error("GEMINI_API_KEY is not set. Cannot evaluate candidate.")
        return None

    title = candidate.get("title", "")
    url = candidate.get("url", "")
    raw_text = candidate.get("raw_text", "")

    # Truncate raw text defensively if extremely large
    truncated_text = raw_text[:25000]

    # Inject today's date so the LLM can check if deadlines have passed
    today_date = datetime.date.today().isoformat()

    prompt = f"""
You are an AI assistant evaluating an opportunity for a Computer Science student.
Today's date is: {today_date}

Here is the candidate's profile:
{PROFILE}

Here is the opportunity to evaluate:
Title: {title}
URL: {url}
Raw Text:
{truncated_text}

Your task: Evaluate this opportunity and extract ALL available details.

=== EVALUATION RULES ===

RELEVANCE RULES:
- AI/ML is the candidate's PRIMARY interest and should receive higher relevance.
- The candidate is a Computer Science student, so other CS fields are valid (e.g., Software Engineering, Computer Science research, Systems, Databases, Cloud Computing, Cybersecurity, Computer Networks, Operating Systems, Distributed Systems, Algorithms, Data Science, Backend development, Open Source, General programming).
- Do NOT reject an opportunity simply because it is not AI/ML.
- Keep relevant=true for legitimate CS opportunities.

ELIGIBILITY RULES:
- Pakistani applicants can apply, OR the program explicitly accepts international applicants.
- Undergraduate students are eligible.
- A 5th-semester CS student can reasonably apply.
- No obvious citizenship/residency restriction that excludes the candidate.
- No obvious university-specific restriction that excludes FAST-NUCES.
- Be conservative when eligibility information is unclear, but don't reject purely because nationality isn't explicitly mentioned if it's generally open to international students.

DEADLINE RULES:
- If you can identify a deadline, report it in YYYY-MM-DD format.
- If the deadline has ALREADY PASSED (before {today_date}), set deadline_passed=true.
- If the opportunity is rolling or always-open, set deadline="Rolling".
- If no deadline is found, set deadline="Not specified".

LEGITIMACY RULES:
- Score "high" for well-known organizations (Google, Microsoft, CERN, MITACS, DAAD, MIT, Stanford, etc.) and programs that have existed for multiple years.
- Score "medium" for less well-known but real academic or industry programs.
- Score "low" for suspicious, unclear, or potentially fake listings (e.g. aggregator pages with no specific program, vague job boards with no company name).

=== REQUIRED OUTPUT ===

You MUST respond ONLY with a valid JSON object. Do not include markdown code fences. The JSON schema:
{{
  "relevant": true or false,
  "eligible": true or false,
  "deadline_passed": true or false,
  "field": "AI/ML|Software Engineering|Research|Cybersecurity|Data Science|Cloud|Systems|Database|Networking|Open Source|General CS|Scholarship|Fellowship|Other",
  "relevance_level": "high|medium|low",
  "reasoning": "one sentence explaining the relevance and eligibility decision",
  "program_name": "official name of the program/opportunity",
  "organization": "hosting organization (e.g. Google, MITACS, Max Planck, CERN)",
  "opportunity_type": "Research Internship|Software Internship|Fellowship|Scholarship|Open Source Program|Summer Research Program|Mentorship|Other",
  "description": "2-3 sentence description of what the program offers and what participants do",
  "funding_details": "stipend amount, travel coverage, accommodation details, or 'Not specified' if unknown",
  "deadline": "YYYY-MM-DD or Rolling or Not specified",
  "duration": "program duration (e.g. '10 weeks', '3 months', 'Summer 2027') or 'Not specified'",
  "location": "country/city or Remote or 'Not specified'",
  "eligibility_summary": "who can apply - nationalities, degree level, year requirements, etc.",
  "how_to_apply": "brief instructions on how to apply or 'See website'",
  "application_url": "direct URL to application portal if found, otherwise same as info page URL",
  "legitimacy_score": "high|medium|low",
  "legitimacy_reasoning": "one sentence explaining why this is considered legitimate or not",
  "urgency": "high|medium|low|unknown"
}}

Interpret urgency as:
- high = deadline within approximately 2 weeks or a rolling opportunity with limited slots
- medium = deadline is approaching but not extremely soon
- low = deadline is comfortably far away
- unknown = deadline cannot be determined
"""
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
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
    and returns a list of enriched candidates that are both relevant, eligible,
    have open deadlines, and pass legitimacy checks.
    Uses gemini-3.5-flash-lite. Waits 5s between calls to stay within rate limits.
    """
    filtered = []

    for i, candidate in enumerate(candidates, 1):
        logging.info(f"Evaluating candidate {i}/{len(candidates)}: {candidate.get('title', 'Unknown')}")

        # Small delay to stay within rate limits (15 RPM = 1 per 4s, using 5s to be safe)
        if i > 1:
            time.sleep(5)

        # Retry up to 3 times on transient errors
        evaluation = None
        for attempt in range(3):
            evaluation = evaluate_candidate(candidate)
            if evaluation is not None:
                break
            logging.warning(f"  Attempt {attempt+1} failed. Waiting 30s before retry...")
            time.sleep(30)

        if not evaluation:
            continue

        # Enrich candidate
        enriched_candidate = candidate.copy()
        enriched_candidate.update(evaluation)

        is_relevant = evaluation.get("relevant", False)
        is_eligible = evaluation.get("eligible", False)
        deadline_passed = evaluation.get("deadline_passed", False)
        legitimacy = evaluation.get("legitimacy_score", "medium")

        # Reject if not relevant or not eligible
        if not is_relevant or not is_eligible:
            logging.info(f"  Rejected: relevant={is_relevant}, eligible={is_eligible}")
            logging.info(f"  Reasoning: {evaluation.get('reasoning', 'None provided')}")
            continue

        # Reject if deadline has already passed
        if deadline_passed:
            logging.info(f"  Rejected: deadline has passed ({evaluation.get('deadline', 'unknown')})")
            continue

        # Reject low-legitimacy opportunities
        if legitimacy == "low":
            logging.info(f"  Rejected: low legitimacy — {evaluation.get('legitimacy_reasoning', 'suspicious listing')}")
            continue

        filtered.append(enriched_candidate)

    return filtered
