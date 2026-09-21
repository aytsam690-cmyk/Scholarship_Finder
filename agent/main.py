"""
Orchestrates the opportunity finding pipeline: 
search -> filter -> memory -> notify.
"""
import logging
from agent.config import SOURCES
from agent.search import run_searches
from agent.filter import filter_candidates
from agent.memory import filter_new_opportunities
from agent.notify import send_notification

def main():
    """Main entry point for the agent."""
    print("Starting opportunity finder...")
    print(f"Loaded {len(SOURCES)} sources from configuration.")
    print("Fetching and searching sources. This may take a moment...\n")
    
    candidates = run_searches(SOURCES)
    
    print("\n" + "="*50)
    print(f"Search complete. Found {len(candidates)} candidate opportunities.")
    print("Evaluating relevance and eligibility. This may take some time...\n")
    
    filtered_candidates = filter_candidates(candidates)
    
    print("\n" + "="*50)
    print(f"Filtering complete. Found {len(filtered_candidates)} relevant and eligible opportunities.")
    print("Checking memory to deduplicate already seen opportunities...\n")
    
    new_candidates = filter_new_opportunities(filtered_candidates)
    
    print("\n" + "="*50)
    print(f"Memory check complete. New: {len(new_candidates)}, Already seen: {len(filtered_candidates) - len(new_candidates)}")
    print("="*50 + "\n")
    
    if new_candidates:
        print("Sending email notifications...\n")
        send_notification(new_candidates)
    else:
        print("No new opportunities to notify about.\n")

if __name__ == "__main__":
    main()
