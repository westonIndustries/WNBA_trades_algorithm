def calculate_historical_baseline(years_exp, rev_history, draft_slot=None):
    """
    years_exp: Total years in WNBA
    rev_history: List of commercial revenue [t-1, t-2, t-3]
    draft_slot: Integer (1-36) for rookies
    """
    # Expected Revenue Baseline for Rookies (Draft-Slot Proxy)
    # Slot 1 gets $5M baseline, Slot 12 gets $1M, etc.
    if years_exp < 1:
        return max(5.0 - (draft_slot * 0.3), 0.5) 
    
    # Weighted Baseline for Veterans
    if len(rev_history) >= 3:
        return (rev_history[0] * 0.5) + (rev_history[1] * 0.3) + (rev_history[2] * 0.2)
    elif len(rev_history) == 2:
        return (rev_history[0] * 0.6) + (rev_history[1] * 0.4)
    else:
        return rev_history[0]

# --- Testing the Logic ---
# Rookie #1 Pick (Hype Catalyst)
ch_rookie = calculate_historical_baseline(0, [], draft_slot=1) # Returns 4.7

# 10-Year Vet (Legacy Icon)
ch_vet = calculate_historical_baseline(10, [15, 14.5, 14]) # Returns 14.65