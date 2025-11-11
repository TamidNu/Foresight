"""
Experimental Pricing Engine package.
Contains:
- utils: date helpers and simple JSON caching
- perplexity_adapter: fetches external events and maps to daily impact scores
- heuristics: baseline rules to compute price recommendations
- engine: orchestration over a date range with optional baseline rates
"""


