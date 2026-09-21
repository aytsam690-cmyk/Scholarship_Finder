from agent.notify import send_notification
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

mock_candidates = [
    {
        "title": "Summer ML Research Intern",
        "url": "http://example.com/ml",
        "source_name": "MIT Labs",
        "field": "AI/ML",
        "relevance_level": "high",
        "reasoning": "Directly matches AI/ML preference.",
        "deadline_found": "2026-10-01",
        "urgency": "high"
    },
    {
        "title": "SWE Core Intern",
        "url": "http://example.com/swe",
        "source_name": "Google",
        "field": "Software Engineering",
        "relevance_level": "medium",
        "reasoning": "Excellent general SWE role for a CS student.",
        "deadline_found": "2027-01-15",
        "urgency": "low"
    },
    {
        "title": "Open Source Systems Mentorship",
        "url": "http://example.com/oss",
        "source_name": "Linux Foundation",
        "field": "Open Source",
        "relevance_level": "medium",
        "reasoning": "Great exposure to open-source systems architecture.",
        "deadline_found": "Rolling",
        "urgency": "medium"
    }
]

print("Testing notify module with mock opportunities...")
send_notification(mock_candidates)
