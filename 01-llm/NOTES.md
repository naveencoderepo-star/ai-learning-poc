# POC 1 – LLM: Talk to an LLM from Code

## Goal
Understand prompts, tokens, temperature, system prompts and hallucination
by calling an LLM from Python.

## Setup Used
| Item | Value |
|---|---|
| Machine | MacBook Air M5 |
| Python | 3.13 (managed by uv) |
| LLM runner | Ollama 0.40.16 (local, free, no API key) |
| Model | llama3.2 (3.2B parameters, Q4_K_M quantization, ~2 GB) |
| Library | `ollama` Python package |

---

## Step 1 – Simple Prompt
**File:** `step1_simple_prompt.py`
**What it does:** Sends one question to the local model and prints the answer, token usage and time taken.

### Observations
- Question: "Explain the difference between smoke testing and sanity testing in 3 lines."
- Input tokens: 40 | Output tokens: 71 | Time: 1.37 seconds
- Input tokens (40) are higher than the word count (~15) because Ollama adds hidden
  **chat template tokens** (markers for who is speaking).
- The answer was **partly wrong**: smoke testing was correct, but sanity testing was
  described as "data validation", which is wrong. Sanity testing = narrow check of
  specific functionality after a bug fix or small change.
- Lesson: a small local model is fast and free but less accurate.

---

## Step 2A – System Prompt
**File:** `step2_system_prompt.py`
**What it does:** Asks "What is regression testing?" twice: without and with a system prompt.

### Observations
| | Without system prompt | With system prompt |
|---|---|---|
| Length | Very long (~350 words) | Short (~100 words) |
| Format | Paragraphs + numbered lists | Exactly 3 bullets |
| Ended with a tip? | No | Yes |
| Extra text? | – | Added an intro line I didn't ask for |

- The system prompt controls the model's **role, format, length and tone**.
- llama3.2 followed the main rules but added extra filler text.
  Small models follow instructions less strictly than big ones.

---

Exercise 1 (Teacher persona): The model switched to a story style with a video game analogy and simple words. Persona changes tone, structure, examples and vocabulary. But a simpler tone slightly changed the meaning (blamed regression on carelessness). Always check accuracy, not just style.

## Hallucinations I Found Myself
1. **Jira alternatives (ollama run, terminal):** The model confidently listed TestRail and
   TestLink as "bug tracking systems" (they are test management tools) and said Bamboo
   "has a bug tracking feature" (it's a CI/CD tool). Zapier was listed as a Jira alternative
   (it's an integration tool).
2. **Step 2 answer:** Called Selenium and Appium "regression testing frameworks" (they are
   general automation tools) and listed "CodeCoverage" as a tool name (not a real tool).
3. **Step 1 answer:** Wrong definition of sanity testing.

**Lesson:** Hallucinations hide inside mostly-correct answers and are written confidently.
Domain knowledge (like QA experience) is needed to catch them.

### Private data questions (no hallucination – good behaviour)
- "What is the password rule in our login module?" → Model said it doesn't know. ✅
- Leading question asking for the exact lockout attempts/minutes → Model still said it
  doesn't know, and only gave generic examples clearly labelled as "common policies". ✅
- My real rules (in `data/login-module.md`): 4 attempts, 23-minute lockout.
  → In POC 3 (RAG), the model should answer this exactly.

---

## Gemini → Ollama Migration (Why I Switched)
- Started with Gemini free tier (gemini-3.8-flash).
- Problems faced:
  - Frequent **503 UNAVAILABLE** (model overloaded), even on lighter models.
  - `gemini-2.5-flash-lite` returned **404**: listed in `models.list()` but
    "no longer available to new users".
  - Needed a fallback model list + retry-with-wait logic just to get one answer.
  - Free-tier data may be used by Google, so no real data could be used.
- Switched to **Ollama (local)**: no API key, no rate limits, no 503, data stays on my Mac.
- Trade-off: smaller model = less accurate answers.

### Cleanup done after migration
- Removed `google-genai` library (`uv remove google-genai`)
- Removed `GEMINI_API_KEY` from `.env` (kept the `.env` file + `python-dotenv` for future use)
- Deleted the API key in Google AI Studio
- Deleted `list_models.py` (Gemini-only helper)
- Rewrote `step1_simple_prompt.py` and `step2_system_prompt.py` to use `ollama.chat()`

### QA lessons from the Gemini phase
- LLM APIs can fail with **429 (rate limit)** and **503 (overloaded)**: real AI apps need
  retry + fallback handling, and this must be tested.
- `models.list()` showing a model doesn't guarantee your account can use it.
  Always test with real calls.
- Never paste or screenshot a full API key. If exposed, delete it and create a new one.

---

## Key Terms Learned
| Term | Meaning |
|---|---|
| **LLM** | Large Language Model: predicts the next word/token to generate text |
| **Token** | A chunk of text (~¾ of a word). Usage and cost are counted in tokens |
| **Prompt** | The input/question sent to the model |
| **System prompt** | Rules and persona for the model; applies to every answer |
| **User prompt** | What the person asks right now |
| **Message roles** | `system` (rules), `user` (question), `assistant` (model's reply) |
| **Hallucination** | Model confidently gives wrong or made-up information |
| **Parameters** | The model's learned weights (llama3.2 = 3.2 billion). More = usually smarter but slower |
| **Quantization** | Compressing the model (e.g. 4-bit Q4_K_M) so it runs on a laptop, with a small quality loss |
| **Knowledge cutoff** | The model only knows information up to its training date |

---

## Still To Do in POC 1
- [ ] Step 2B – Exercise 1: Teacher persona (10-year-old)
- [ ] Step 2B – Exercise 2: Force table format
- [ ] Step 2B – Exercise 3: Restrict topic + prompt injection test (PASS/FAIL)
- [ ] Step 3 – Temperature (0 vs 1)
- [ ] Step 4 – JSON output + parsing
- [ ] Step 5 – Hallucination with fake app data
- [ ] QA twist – pytest check for required JSON fields

QA lessons:

For business answers (RAG, BRD rules) → use temperature 0. That’s why tools.py uses temperature=0.
Even at temperature 0, never use exact-match assertions in AI tests. A model update or another machine can change the wording. Check meaning or key facts instead (e.g. “contains below ₹3,000”).

