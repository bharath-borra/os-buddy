import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

print("1. Importing agent...")
try:
    from agent import agent
    print("   Success.")
except Exception as e:
    print(f"   Failed to import agent: {e}")
    sys.exit(1)

print("2. Running agent with test query...")
query = "What are the tax slabs?"
print(f"   Query: {query}")

try:
    response, thoughts = agent(query, [])
    print("\n--- RESPONSE ---")
    print(response)
    print("\n--- THOUGHTS ---")
    print(thoughts)
except Exception as e:
    print(f"\nCRITICAL ERROR during execution: {e}")
    import traceback
    traceback.print_exc()
