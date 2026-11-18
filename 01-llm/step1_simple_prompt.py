from dotenv import load_dotenv   # reads the .env file
from google import genai          # official Google Gemini SDK
from google.genai import errors   # NEW: to catch API errors

# 1. Load GEMINI_API_KEY from .env into environment variables
load_dotenv()

# 2. Create the Gemini client (it reads GEMINI_API_KEY automatically)
client = genai.Client()

# 3. Send the question to the model (with fallback if a model is busy)
question = "Can i get the detials of Founder of Coherent Pixels System private limited IT Company located in Chennai & Coimbatore?"

models_to_try = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemma-4-31b-it",
]

response = None
for model_name in models_to_try:
    try:
        print(f"Trying model: {model_name}")
        response = client.models.generate_content(
            model=model_name,
            contents=question,
        )
        print(f"Success with: {model_name}")
        break                                   # got an answer, stop trying
    except errors.APIError as e:
        if e.code in (429, 500, 503):           # busy / rate limit -> try next model
            print(f"  {model_name} failed ({e.code}), trying next...")
        else:
            raise                               # real error (bad key, wrong name) -> stop

if response is None:
    raise SystemExit("All models are busy. Try again in a few minutes.")

# 4. Print the answer
print("\n--- Question ---")
print(question)
print("\n--- Answer ---")
print(response.text)

# 5. Print token usage
usage = response.usage_metadata
print("\n--- Token usage ---")
print("Input tokens   :", usage.prompt_token_count)
print("Output tokens  :", usage.candidates_token_count)
print("Thinking tokens:", usage.thoughts_token_count)   # may be None
print("Total tokens   :", usage.total_token_count)