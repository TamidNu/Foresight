from perplexity import Perplexity
import os
from dotenv import load_dotenv



load_dotenv()


client = Perplexity()

# Search for results from a specific country
search = client.search.create(
    query="government policies on renewable energy",
    country="US",  # ISO country code
    max_results=5
)

for result in search.results:
    print(f"{result.title}: {result.url}")

