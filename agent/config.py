"""
Contains profile information and the list of sources to scrape or fetch from.
"""

PROFILE = """
Candidate Profile:
- 5th semester Computer Science undergraduate as of Fall 2026
- FAST-NUCES, Pakistan
- Pakistani national
- Interested primarily in AI/ML, Deep Learning, NLP, LLMs and Computer Vision
- Also interested in broader Computer Science opportunities, including:
  - Software Engineering
  - Computer Science research
  - Data Science
  - Databases
  - Cloud Computing
  - Distributed Systems
  - Operating Systems
  - Computer Networks
  - Cybersecurity
  - Algorithms and Data Structures
  - Backend/Web Development
  - Systems
  - Open Source
  - General programming
- Studied ML fundamentals, logistic regression, backpropagation and from-scratch implementations
- Building AI/ML and software projects

Seeking Opportunities:
- research internships
- software engineering internships
- summer research programs
- fellowships
- mentorship programs
- open-source programs
- scholarships related to CS/technology
- remote research opportunities
- international undergraduate opportunities
- other legitimate opportunities useful for a CS undergraduate

Eligibility Requirements (CRITICAL):
The agent must determine whether an opportunity is genuinely open to:
- Pakistani applicants
- international students
- undergraduate students
- a 5th-semester CS student

It should flag restrictions such as:
- citizenship requirements
- residency requirements
- enrollment at a specific university
- graduate-only requirements
- PhD-only requirements
- age restrictions
- restricted geographic regions
- requirements for work authorization
- requirements that clearly exclude the candidate

IMPORTANT:
AI/ML is a preference, NOT a hard requirement.
A strong Software Engineering, Systems, Cybersecurity, Database, Cloud, Open Source, or general CS opportunity should still be returned if the candidate is eligible.
"""

SOURCES = [
    # Official Program Pages
    {
        "name": "MLH Fellowship",
        "url": "https://fellowship.mlh.io/",
        "type": "fixed_page"
    },
    {
        "name": "Google Summer of Code (GSoC)",
        "url": "https://summerofcode.withgoogle.com/",
        "type": "fixed_page"
    },
    {
        "name": "LFX Mentorship",
        "url": "https://lfx.linuxfoundation.org/tools/mentorship/",
        "type": "fixed_page"
    },
    {
        "name": "Outreachy",
        "url": "https://www.outreachy.org/",
        "type": "fixed_page"
    },
    {
        "name": "MITACS Globalink Research Internship",
        "url": "https://www.mitacs.ca/en/programs/globalink/globalink-research-internship",
        "type": "fixed_page"
    },
    {
        "name": "DAAD RISE Germany",
        "url": "https://www.daad.de/rise/en/rise-germany/",
        "type": "fixed_page"
    },
    
    # Broad Search Queries
    {
        "name": "computer science undergraduate internship international students 2027",
        "url": "computer science undergraduate internship international students 2027",
        "type": "search_query"
    },
    {
        "name": "CS research internship international students 2027",
        "url": "CS research internship international students 2027",
        "type": "search_query"
    },
    {
        "name": "AI ML research internship international students 2027",
        "url": "AI ML research internship international students 2027",
        "type": "search_query"
    },
    {
        "name": "software engineering internship international students 2027",
        "url": "software engineering internship international students 2027",
        "type": "search_query"
    },
    {
        "name": "computer science summer research program undergraduate 2027",
        "url": "computer science summer research program undergraduate 2027",
        "type": "search_query"
    },
    {
        "name": "undergraduate research fellowship computer science international students",
        "url": "undergraduate research fellowship computer science international students",
        "type": "search_query"
    },
    {
        "name": "remote computer science research internship undergraduate",
        "url": "remote computer science research internship undergraduate",
        "type": "search_query"
    },
    {
        "name": "open source internship students 2027",
        "url": "open source internship students 2027",
        "type": "search_query"
    },
    {
        "name": "cybersecurity internship international students undergraduate 2027",
        "url": "cybersecurity internship international students undergraduate 2027",
        "type": "search_query"
    },
    {
        "name": "data science internship international students undergraduate 2027",
        "url": "data science internship international students undergraduate 2027",
        "type": "search_query"
    },
    {
        "name": "cloud computing internship undergraduate international students 2027",
        "url": "cloud computing internship undergraduate international students 2027",
        "type": "search_query"
    }
]

NOTIFY_EMAIL = "aytsamullah690@gmail.com"
