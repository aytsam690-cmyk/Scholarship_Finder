import os
import json
import logging
import hashlib

DATA_FILE = "data/seen.json"

def normalize_url(url):
    """Normalize a URL to remove transient query parameters if needed, or simply return as-is for hashing."""
    return url.strip().rstrip('/')

def generate_id(candidate):
    """Generate a stable unique identifier for a candidate."""
    url = normalize_url(candidate.get("url", ""))
    source_name = candidate.get("source_name", "").strip()
    
    # Hash the combination of URL and source name
    stable_string = f"{url}|{source_name}"
    return hashlib.sha256(stable_string.encode('utf-8')).hexdigest()

def load_memory():
    """Load previously seen candidate identifiers from JSON."""
    if not os.path.exists(DATA_FILE):
        return []
        
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                logging.warning(f"{DATA_FILE} does not contain a list. Resetting to [].")
                return []
    except json.JSONDecodeError as e:
        logging.warning(f"{DATA_FILE} is corrupted: {e}. Resetting to [].")
        return []
    except Exception as e:
        logging.warning(f"Error reading {DATA_FILE}: {e}. Resetting to [].")
        return []

def save_memory(seen_list):
    """Save the updated list of seen identifiers to JSON."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(seen_list, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save {DATA_FILE}: {e}")

def filter_new_opportunities(candidates):
    """
    Given a list of candidates, filter out those that have been seen before.
    Returns only new candidates and updates the memory file.
    """
    seen_ids = set(load_memory())
    
    new_candidates = []
    already_seen_count = 0
    
    new_ids = set()
    
    for candidate in candidates:
        candidate_id = generate_id(candidate)
        
        if candidate_id in seen_ids:
            already_seen_count += 1
            logging.info(f"Skipping already seen opportunity: {candidate.get('title', 'Unknown')} ({candidate.get('url', '')})")
        else:
            new_candidates.append(candidate)
            new_ids.add(candidate_id)
            
    if new_ids:
        # Update memory with new IDs
        updated_seen = list(seen_ids.union(new_ids))
        save_memory(updated_seen)
        
    logging.info(f"Memory filter complete. New: {len(new_candidates)}, Already seen: {already_seen_count}")
    return new_candidates
