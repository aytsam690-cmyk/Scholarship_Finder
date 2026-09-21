import os
import logging
import smtplib
from email.message import EmailMessage
import requests
from dotenv import load_dotenv

from agent.config import NOTIFY_EMAIL as CONFIG_NOTIFY_EMAIL

load_dotenv()


def format_opportunity(opp):
    """Format a single opportunity into a text block."""
    lines = []
    field_tag = f"[{opp.get('field', 'UNKNOWN FIELD').upper()}]"
    
    lines.append(f"{field_tag}")
    lines.append(f"Opportunity: {opp.get('title', 'No Title')}")
    lines.append(f"Source: {opp.get('source_name', 'Unknown')}")
    
    deadline = opp.get('deadline_found')
    if deadline and str(deadline).lower() not in ["null", "none"]:
        lines.append(f"Deadline: {deadline} (Urgency: {opp.get('urgency', 'unknown')})")
        
    lines.append(f"Match: {opp.get('reasoning', 'No reasoning provided')} (Relevance: {opp.get('relevance_level', 'unknown')})")
    lines.append(f"URL: {opp.get('url', 'No URL')}")
    
    return "\n".join(lines)

def generate_email_body(urgent, rest):
    """Generate the full email body string."""
    body_parts = []
    
    if urgent:
        body_parts.append("===============================")
        body_parts.append("      URGENT OPPORTUNITIES     ")
        body_parts.append("===============================\n")
        
        for opp in urgent:
            body_parts.append(format_opportunity(opp))
            body_parts.append("\n" + "-"*40 + "\n")
            
    if rest:
        body_parts.append("===============================")
        body_parts.append("        OTHER MATCHES          ")
        body_parts.append("===============================\n")
        
        for opp in rest:
            body_parts.append(format_opportunity(opp))
            body_parts.append("\n" + "-"*40 + "\n")
            
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
    # For Resend, if using a verified domain it usually requires matching sender.
    # Otherwise onboarding@resend.dev is allowed for sending to the registered address.
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
    from_email = os.getenv("EMAIL_ADDRESS", "no-reply@opportunity-finder.local")
    
    if not api_key:
        logging.error("Brevo API key missing (BREVO_API_KEY). Cannot send email.")
        return False
        
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "sender": {"email": from_email, "name": "Opportunity Finder"},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body
    }
    
    try:
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        response.raise_for_status()
        logging.info(f"Email sent successfully to {to_email} via Brevo API.")
        return True
    except Exception as e:
        logging.error(f"Failed to send email via Brevo: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Brevo error detail: {e.response.text}")
        return False

def send_notification(new_opportunities):
    """
    Given a list of new opportunities, formats them and sends an email.
    """
    if not new_opportunities:
        logging.info("No new opportunities. Skipping notification.")
        return
        
    to_email = os.getenv("NOTIFY_EMAIL")
    if not to_email:
        to_email = CONFIG_NOTIFY_EMAIL
        
    urgent = [opp for opp in new_opportunities if str(opp.get("urgency", "")).lower() == "high"]
    rest = [opp for opp in new_opportunities if str(opp.get("urgency", "")).lower() != "high"]
    
    total = len(new_opportunities)
    urgent_count = len(urgent)
    
    subject = f"{total} new opportunities found"
    if urgent_count > 0:
        subject += f" ({urgent_count} urgent)"
        
    body = generate_email_body(urgent, rest)
    
    # We always print the generated output to the console for visibility
    print("\n--- NOTIFICATION PREVIEW ---")
    print(f"To: {to_email}")
    print(f"Subject: {subject}\n")
    print(body)
    print("----------------------------\n")
    
    if to_email == "[[YOUR_EMAIL]]":
        logging.warning("Recipient email is not set (still placeholder). Email sending skipped.")
        return
        
    email_method = os.getenv("EMAIL_METHOD", "smtp").strip().lower()
    # Support "gmail" for backwards compatibility
    if email_method == "gmail":
        email_method = "smtp"
        
    if email_method == "resend":
        logging.info("Attempting to send email via Resend API...")
        send_via_resend(subject, body, to_email)
    elif email_method == "brevo":
        logging.info("Attempting to send email via Brevo API...")
        send_via_brevo(subject, body, to_email)
    else:
        logging.info("Attempting to send email via SMTP...")
        send_via_smtp(subject, body, to_email)
