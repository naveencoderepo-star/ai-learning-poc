# BRD Assistant tools
# Tool 1: search_brd       -> RAG (Retrieve + Augment + Generate)
# Tool 2: generate_stories -> User stories with Given-When-Then as JSON
# Tool 3: save_stories     -> Save generated stories to output/stories.json
# Tool 4: list_stories     -> List saved stories

import json
from pathlib import Path
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma

BASE_DIR = Path(__file__).parent
DB_DIR = BASE_DIR / "chroma_db"
LLM_MODEL = "qwen2.5:7b"

# Connect to the EXISTING vector DB (built by build_vector_db.py)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_db = Chroma(
    persist_directory=str(DB_DIR),
    embedding_function=embeddings,
    collection_name="shopeasy_brd",
)

# temperature=0 -> consistent, factual answers (no creativity needed here)
llm = ChatOllama(model=LLM_MODEL, temperature=0)

# Same model, but Ollama FORCES the output to be valid JSON
json_llm = ChatOllama(model=LLM_MODEL, temperature=0, format="json")

# Where saved stories go + memory of the last generated stories per module
STORIES_FILE = BASE_DIR / "output" / "stories.json"
_last_generated = {}


# ---------------- Tool 1: search_brd (RAG) ----------------

RAG_SYSTEM_PROMPT = """You are a Business Analyst assistant for the ShopEasy project.
Answer using ONLY the BRD context provided.

Rules:
1. Find the requirement line(s) that answer the question, even if the question uses different words
   (e.g. "maximum order value" can be answered by "only for orders below ₹3,000").
2. Answer in 1-2 sentences. Keep the exact wording for limits and rules from the BRD
   (e.g. "below ₹3,000", "within 7 working days", "maximum 3 times") - never change "below" to "is".
3. Then add a "Source:" line that QUOTES the exact requirement line(s) you used, copied word for word,
   including the ID (e.g. BR-LOGIN-03).
4. Only if NO requirement line in the context answers the question, reply exactly:
   "I don't know - this is not in the BRD."
"""


def search_brd(question: str, k: int = 2) -> str:
    """Answer a question using only the ShopEasy BRD."""
    # 1. RETRIEVE: find the k most relevant chunks
    docs = vector_db.similarity_search(question, k=k)
    print("   [retrieved sections:", [d.metadata.get("section") for d in docs], "]")

    # 2. AUGMENT: put those chunks into the prompt as context
    context = "\n\n".join(
        f"[Section: {doc.metadata.get('section')}]\n{doc.page_content}" for doc in docs
    )
    messages = [
        ("system", RAG_SYSTEM_PROMPT),
        ("human", f"BRD context:\n{context}\n\nQuestion: {question}"),
    ]

    # 3. GENERATE: the LLM answers using only that context
    return llm.invoke(messages).content


# ---------------- Tool 2: generate_stories (JSON) ----------------

STORY_SYSTEM_PROMPT = """You are a senior Business Analyst. Convert BRD requirements into Agile user stories.
Use ONLY the BRD context provided.
Return ONLY valid JSON in exactly this shape:
{
  "module": "<module name>",
  "stories": [
    {
      "story_id": "US-1",
      "title": "<short title>",
      "as_a": "<type of user>",
      "i_want": "<goal>",
      "so_that": "<benefit>",
      "requirement_ids": ["BR-..."],
      "acceptance_criteria": [
        {"given": "...", "when": "...", "then": "..."}
      ]
    }
  ]
}
Rules:
- One story per requirement ID.
- Each story must have at least 2 acceptance criteria: one positive and one negative or edge case.
- Use the exact numbers from the BRD (limits, times, amounts)."""


def generate_stories(module: str) -> str:
    """Generate user stories with Given-When-Then acceptance criteria for one BRD module."""
    # 1. RETRIEVE: the chunk for this module
    docs = vector_db.similarity_search(f"{module} module requirements", k=1)
    print("   [retrieved section:", docs[0].metadata.get("section"), "]")

    # 2. AUGMENT + GENERATE as JSON
    messages = [
        ("system", STORY_SYSTEM_PROMPT),
        ("human", f"BRD context:\n{docs[0].page_content}\n\nModule: {module}"),
    ]
    response = json_llm.invoke(messages).content

    # 3. VALIDATE: fails loudly if the LLM returned broken JSON
    data = json.loads(response)
    _last_generated[module.lower()] = data   # remember for save_stories
    return json.dumps(data, indent=2, ensure_ascii=False)


def _load_all_stories() -> dict:
    """Read stories.json safely: missing or empty file -> {} (no crash)."""
    if not STORIES_FILE.exists():
        return {}
    text = STORIES_FILE.read_text(encoding="utf-8").strip()
    return json.loads(text) if text else {}



# ---------------- Tool 3: save_stories ----------------

def save_stories(module: str) -> str:
    """Save the last generated user stories for a module to output/stories.json."""
    key = module.lower()
    if key not in _last_generated:
        return f"No generated stories for '{module}'. Run generate_stories first."

    prefix = key.upper()   # e.g. LOGIN
    stories = []
    for story in _last_generated[key]["stories"]:
        story = dict(story)
        story["story_id"] = f"{prefix}-{story['story_id']}"   # unique ID: LOGIN-US-1
        story["status"] = "Draft"                             # needs human review
        stories.append(story)

        # Load existing file (if any), replace this module's stories, save
    all_stories = _load_all_stories()
    all_stories[prefix] = stories
    STORIES_FILE.parent.mkdir(exist_ok=True)
    STORIES_FILE.write_text(json.dumps(all_stories, indent=2, ensure_ascii=False), encoding="utf-8")

    return f"Saved {len(stories)} stories for {module} to {STORIES_FILE.name}"


# ---------------- Tool 4: list_stories ----------------

def list_stories(module: str = "") -> str:
    """List saved user stories. Give a module name, or leave empty for all modules."""
    if not STORIES_FILE.exists():
        return "No stories saved yet."

    all_stories = _load_all_stories()
    modules = [module.upper()] if module else list(all_stories.keys())

    lines = []
    for m in modules:
        for s in all_stories.get(m, []):
            lines.append(f"{s['story_id']} | {s['title']} | {', '.join(s['requirement_ids'])} | {s['status']}")
    return "\n".join(lines) if lines else f"No stories saved for '{module}'."


# ---------------- Quick tests ----------------
#   uv run python brd-assistant/tools.py                -> RAG questions
#   uv run python brd-assistant/tools.py stories Login  -> generate stories (print only)
#   uv run python brd-assistant/tools.py save Login     -> generate + save + list
#   uv run python brd-assistant/tools.py list           -> list all saved stories
if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    module = sys.argv[2] if len(sys.argv) > 2 else "Login"

    if mode == "stories":
        print(generate_stories(module))
    elif mode == "save":
        generate_stories(module)
        print(save_stories(module))
        print(list_stories(module))
    elif mode == "list":
        print(list_stories())
    else:
        test_questions = [
            "After how many failed attempts is an account locked, and for how long?",
            "What is the maximum order value for Cash on Delivery?",
            "How many working days does a card refund take?",
            "What is the delivery charge for an order?",   # NOT in the BRD
        ]
        for q in test_questions:
            print("Q:", q)
            print("A:", search_brd(q))
            print("-" * 60)