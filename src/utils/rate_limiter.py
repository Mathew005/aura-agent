import time
import re
import logging

def handle_rate_limit(e):
    """
    Checks if the exception is a rate limit error (429).
    If so, parses the retry delay and sleeps.
    Returns True if it was a rate limit error and we slept, False otherwise.
    """
    error_str = str(e)
    if "429" in error_str or "quota" in error_str.lower():
        wait_time = 5.0 # Default fallback
        
        # Pattern 1: "Please retry in 37.912305187s."
        match1 = re.search(r"Please retry in ([0-9.]+)\s*s", error_str)
        if match1:
            wait_time = float(match1.group(1))
            
        # Pattern 2: "retry_delay { seconds: 37 }"
        if not match1:
            match2 = re.search(r"retry_delay\s*{\s*seconds:\s*([0-9]+)", error_str)
            if match2:
                wait_time = float(match2.group(1))

        # Add a small buffer to be safe
        sleep_time = wait_time + 1.5
        print(f"[Rate Limit] Quota exceeded. Sleeping for {sleep_time:.2f}s...")
        time.sleep(sleep_time)
        return True
    
    return False
