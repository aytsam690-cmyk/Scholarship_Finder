# Opportunity Finder

This project is a daily automated agent that searches for research internships, software engineering roles, fellowships, and other opportunities relevant to a Computer Science undergraduate. It fetches candidate opportunities from various sources and filters them for genuine relevance and eligibility using an LLM. Finally, it keeps track of seen opportunities and emails any new matches directly to the user.

## Search Philosophy & Eligibility

**Search Scope:**  
While **AI/ML** is the preferred area of interest, the agent is configured to search broadly across Computer Science. Legitimate non-AI/ML opportunities are heavily welcomed. The agent actively seeks opportunities in fields such as:
- AI/ML
- Software Engineering
- Research
- Data Science
- Cybersecurity
- Cloud
- Systems
- Databases
- Networking
- Operating Systems
- Algorithms
- Open Source
- General CS

**Eligibility Checks:**  
The LLM evaluates each opportunity strictly for eligibility. It verifies that the opportunity is genuinely open to a **Pakistani undergraduate student** (e.g. specifically checking for international student acceptance). If eligibility is unclear from the text, the agent acts conservatively to avoid false positives, rather than assuming it is open.

## Local Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/opportunity-finder.git
   cd opportunity-finder
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your environment variables:**
   - Copy the example config file:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and fill in your actual credentials (e.g., `GEMINI_API_KEY`, `EMAIL_METHOD`, `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `NOTIFY_EMAIL`).

5. **Run the agent:**
   ```bash
   python -m agent.main
   ```

## GitHub Actions Automated Setup

The repository is configured to run automatically every day at 08:00 UTC using GitHub Actions.

### 1. Adding Required Secrets
To enable the automated workflow, you need to add your environment variables as **GitHub Secrets**.

**Where to add them:**
Navigate to your **GitHub repository → Settings → Secrets and variables → Actions**. Add a "New repository secret" for each of the following that your setup requires:
- `GEMINI_API_KEY` (Required for the LLM)
- `SERPER_API_KEY` (Required for Google Search)
- `EMAIL_METHOD` (Set to `brevo`, `smtp`, or `resend`)
- `BREVO_API_KEY` (Required for Brevo)
- `EMAIL_ADDRESS` (For SMTP / sender display name)
- `EMAIL_PASSWORD` (App Password if using SMTP)
- `RESEND_API_KEY` (If using Resend)
- `NOTIFY_EMAIL` (The email address that will receive the notifications)

*Note: Never hardcode these credentials into the codebase!*

### 2. Manually Triggering the Workflow
You don't have to wait for the daily schedule to test it:
1. Navigate to your **GitHub repository → Actions**.
2. Select **Daily Opportunity Finder** (or `daily-run`) from the left sidebar.
3. Click the **Run workflow** dropdown on the right side and click the green **Run workflow** button.

### How Deduplication Works
The agent keeps track of opportunities it has already emailed you in `data/seen.json`. During a GitHub Actions run, if new opportunities are found, the workflow will automatically commit and push only the updated `data/seen.json` file back to the repository so you don't receive duplicate emails on subsequent days.
