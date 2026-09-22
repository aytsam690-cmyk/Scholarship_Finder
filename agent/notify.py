import os
import logging
import smtplib
from email.message import EmailMessage
import requests
from dotenv import load_dotenv

from agent.config import NOTIFY_EMAIL as CONFIG_NOTIFY_EMAIL

load_dotenv()


def format_opportunity(opp):
    """Format a single opportunity into a detailed, comprehensive text block."""
    lines = []

    # Header bar
    lines.append("━" * 50)
    program_name = opp.get("program_name", opp.get("title", "Unknown Program"))
    lines.append(f"📌 {program_name}")
    lines.append("━" * 50)

    # Organization
    org = opp.get("organization", "Not specified")
    lines.append(f"🏢 Organization:   {org}")

    # Type
    opp_type = opp.get("opportunity_type", opp.get("field", "Unknown"))
    lines.append(f"📋 Type:           {opp_type}")

    # Description
    desc = opp.get("description", "No description available.")
    lines.append(f"📝 Description:    {desc}")

    # Funding
    funding = opp.get("funding_details", "Not specified")
    lines.append(f"💰 Funding:        {funding}")

    # Deadline with urgency indicator
    deadline = opp.get("deadline")
    urgency = opp.get("urgency", "unknown")
    if deadline and str(deadline).lower() not in ["null", "none", "not specified"]:
        urgency_tag = ""
        if urgency == "high":
            urgency_tag = " ⚠️  URGENT!"
        elif urgency == "medium":
            urgency_tag = " (approaching)"
        lines.append(f"📅 Deadline:       {deadline}{urgency_tag}")
    else:
        lines.append(f"📅 Deadline:       Not specified")

    # Duration
    duration = opp.get("duration", "Not specified")
    lines.append(f"⏱  Duration:       {duration}")

    # Location
    location = opp.get("location", "Not specified")
    lines.append(f"📍 Location:       {location}")

    # Eligibility
    eligibility = opp.get("eligibility_summary", "See website for details")
    lines.append(f"✅ Eligibility:    {eligibility}")

    # How to Apply
    how_to_apply = opp.get("how_to_apply", "See website")
    lines.append(f"📝 How to Apply:   {how_to_apply}")

    # URLs
    info_url = opp.get("url", "No URL")
    apply_url = opp.get("application_url", info_url)
    lines.append(f"🔗 Info Page:      {info_url}")
    if apply_url and apply_url != info_url:
        lines.append(f"🔗 Apply Here:     {apply_url}")

    # Legitimacy
    legit_score = opp.get("legitimacy_score", "unknown")
    legit_reason = opp.get("legitimacy_reasoning", "")
    legit_icon = "🟢" if legit_score == "high" else "🟡"
    lines.append(f"🛡  Verified:       {legit_icon} {legit_score.capitalize()} — {legit_reason}")

    # Field & Relevance
    field = opp.get("field", "Unknown")
    relevance = opp.get("relevance_level", "unknown")
    lines.append(f"🎯 Field:          {field} (Relevance: {relevance})")

    # Match reasoning
    reasoning = opp.get("reasoning", "")
    if reasoning:
        lines.append(f"💡 Why it matches: {reasoning}")

    lines.append("━" * 50)

    return "\n".join(lines)


def generate_email_body(urgent, rest):
    """Generate the full email body string with comprehensive details."""
    body_parts = []

    body_parts.append("=" * 50)
    body_parts.append("  🎓 OPPORTUNITY FINDER — DAILY DIGEST")
    body_parts.append("=" * 50)
    body_parts.append("")

    total = len(urgent) + len(rest)
    body_parts.append(f"Found {total} new opportunities for you today!")
    body_parts.append("")

    if urgent:
        body_parts.append("🔴 URGENT — DEADLINE APPROACHING SOON")
        body_parts.append("=" * 50)
        body_parts.append("")

        for opp in urgent:
            body_parts.append(format_opportunity(opp))
            body_parts.append("")

    if rest:
        body_parts.append("🟢 OTHER OPPORTUNITIES")
        body_parts.append("=" * 50)
        body_parts.append("")

        for opp in rest:
            body_parts.append(format_opportunity(opp))
            body_parts.append("")

    body_parts.append("—" * 50)
    body_parts.append("This is an automated email from your Scholarship Finder bot.")
    body_parts.append("All opportunities have been verified for legitimacy and open deadlines.")
    body_parts.append("Expired opportunities are automatically filtered out.")
    body_parts.append("")

    return "\n".join(body_parts)


def send_via_smtp(subject, body, to_email):
    email_addr = os.getenv("EMAIL_ADDRESS")
    email_pass = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not email_addr or not email_pass:
        logging.error("SMTP credentials missing (EMAIL_ADDRESS, EMAIL_PASSWORD). Cannot send email.")
        return False

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = email_addr
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_addr, email_pass)
        server.send_message(msg)
        server.quit()
        logging.info(f"Email sent successfully to {to_email} via SMTP ({smtp_server}).")
        return True
    except Exception as e:
        logging.error(f"Failed to send email via SMTP ({smtp_server}): {e}")
        return False


def send_via_resend(subject, body, to_email):
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("EMAIL_ADDRESS", "onboarding@resend.dev")

    if not api_key:
        logging.error("Resend API key missing (RESEND_API_KEY). Cannot send email.")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": f"Opportunity Finder <{from_email}>",
        "to": [to_email],
        "subject": subject,
        "text": body
    }

    try:
        response = requests.post("https://api.resend.com/emails", json=payload, headers=headers)
        response.raise_for_status()
        logging.info(f"Email sent successfully to {to_email} via Resend API.")
        return True
    except Exception as e:
        logging.error(f"Failed to send email via Resend: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Resend error detail: {e.response.text}")
        return False


def send_via_brevo(subject, body, to_email):
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = "aytsamullah5@gmail.com"
    recipient_email = "aytsamullah5@gmail.com"

    if not api_key:
        logging.error("Brevo API key missing (BREVO_API_KEY). Cannot send email.")
        return False

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "sender": {"email": sender_email, "name": "Scholarship Finder"},
        "replyTo": {"email": sender_email},
        "to": [{"email": recipient_email}],
        "subject": subject,
        "textContent": body
    }

    try:
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        logging.info(f"Brevo API response status: {response.status_code}")
        logging.info(f"Brevo API full response: {response.text}")
        response.raise_for_status()
        logging.info(f"Email sent successfully to {recipient_email} via Brevo API.")
        return True
    except requests.exceptions.HTTPError as e:
        logging.error(f"Failed to send email via Brevo HTTP error: {e}")
        logging.error(f"Brevo error detail: {response.text}")
        return False
    except Exception as e:
        logging.error(f"Failed to send email via Brevo: {e}")
        return False


def send_notification(new_opportunities):
    """
    Given a list of new opportunities, formats them with comprehensive details
    and sends an email digest.
    """
    if not new_opportunities:
        logging.info("No new opportunities. Skipping notification.")
        return

    to_email = "aytsamullah5@gmail.com"

    urgent = [opp for opp in new_opportunities if str(opp.get("urgency", "")).lower() == "high"]
    rest = [opp for opp in new_opportunities if str(opp.get("urgency", "")).lower() != "high"]

    total = len(new_opportunities)
    urgent_count = len(urgent)

    subject = f"🎓 {total} New CS Opportunities Found"
    if urgent_count > 0:
        subject += f" — {urgent_count} URGENT!"

    body = generate_email_body(urgent, rest)

    # Print preview to console
    print("\n--- NOTIFICATION PREVIEW ---")
    print(f"To: {to_email}")
    print(f"Subject: {subject}\n")
    print(body)
    print("----------------------------\n")

    # Default to brevo if EMAIL_METHOD is not set or is empty
    email_method = (os.getenv("EMAIL_METHOD", "") or "brevo").strip().lower()

    if email_method == "resend":
        logging.info("Attempting to send email via Resend API...")
        send_via_resend(subject, body, to_email)
    elif email_method == "brevo":
        logging.info("Attempting to send email via Brevo API...")
        send_via_brevo(subject, body, to_email)
    else:
        logging.info("Attempting to send email via SMTP...")
        send_via_smtp(subject, body, to_email)
