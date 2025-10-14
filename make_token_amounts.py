#!/usr/bin/env python3
import json

FRACTIONS_FILE = "split-example.json"
NONVESTED_OUTPUT = "split-nonvested.json"
VESTED_OUTPUT = "split-vested.json"
TOTAL = 11_250_000 * 10**18 // 2  # Season 1
VEST_CUTOFF = 5000 * 10**18  # Give up to this amount with no vesting

with open(FRACTIONS_FILE, 'r') as f:
    f_splits = json.load(f)

biggest_addr, biggest_f = max(list(f_splits.items()), key=lambda kv: kv[1])
t_splits = {addr: int(f * TOTAL) for addr, f in f_splits.items()}
t_splits[biggest_addr] += (TOTAL - sum(t_splits.values()))  # Fix rounding errors
print(sum(t_splits.values()))

# Now save two things: vests and distributions
t_distributions = {addr: min(t, VEST_CUTOFF) for addr, t in t_splits.items()}
t_vests = {addr: (t - VEST_CUTOFF) for addr, t in t_splits.items() if t > VEST_CUTOFF}
print(sum(t_distributions.values()))
print(sum(t_vests.values()))

with open(NONVESTED_OUTPUT, 'w') as f:
    json.dump(t_distributions, f)

with open(VESTED_OUTPUT, 'w') as f:
    json.dump(t_vests, f)
