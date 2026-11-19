# BRD Assistant - AI Agent
# The LLM decides which tool to call (and in what order) from a plain-English request.

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

import tools as brd   # our 4 functions from tools.py


# ---- 1. Wrap our functions as TOOLS the LLM can see ----
# The docstring is what the LLM reads to decide WHEN to use each tool.

@tool
def search_brd(question: str) -> str:
    """Answer a question about the ShopEasy BRD: business rules, limits, timeouts,
    payment, refund, cart or login requirements. Returns the answer with requirement IDs."""
    return brd.search_brd(question)


@tool
def generate_stories(module: str) -> str:
    """Generate user stories with Given-When-Then acceptance criteria for ONE BRD module.
    module must be one of: Login, Cart, Payment, Refund."""
    brd.generate_stories(module)
    stories = brd._last_generated[module.lower()]["stories"]
    titles = "; ".join(s["title"] for s in stories)
    return f"Generated {len(stories)} stories for {module}: {titles}"   # short summary for the LLM


@tool
def save_stories(module: str) -> str:
    """Save the user stories that were just generated for a module. Call AFTER generate_stories."""
    # Guard: if stories weren't generated yet (e.g. parallel tool calls), generate them first
    if module.lower() not in brd._last_generated:
        brd.generate_stories(module)
    return brd.save_stories(module)


@tool
def list_stories(module: str = "") -> str:
    """List saved user stories. Give a module name (Login, Cart, Payment, Refund) or leave empty for all."""
    return brd.list_stories(module)


# ---- 2. Create the agent: model + tools + rules ----

SYSTEM_PROMPT = """You are the BRD Assistant for the ShopEasy project.
Use the tools to help the user. Rules:
- For questions about requirements or business rules, use search_brd.
- To create user stories, call generate_stories, then save_stories for the same module.
- To show saved stories, use list_stories.
- Valid modules: Login, Cart, Payment, Refund.
- Never invent requirements. Only use what the tools return.
- If the request has several parts, your final reply MUST answer EVERY part, in the same order as asked.
- When you use search_brd, COPY its answer sentence WORD FOR WORD into your final reply (do not rephrase it), and add the requirement ID.
- Keep replies short."""

model = ChatOllama(model="qwen2.5:7b", temperature=0)

agent = create_agent(
    model=model,
    tools=[search_brd, generate_stories, save_stories, list_stories],
    system_prompt=SYSTEM_PROMPT,
)


# Quick check: was the agent created?
if __name__ == "__main__":
    print("Agent created with tools:", [t.name for t in [search_brd, generate_stories, save_stories, list_stories]])



# ---- 3. Run a request and SHOW every step the agent takes ----

def ask_agent(request: str) -> str:
    print(f"\n🧑 USER: {request}")
    result = agent.invoke({"messages": [{"role": "user", "content": request}]})

    for msg in result["messages"]:
        if msg.type == "ai" and msg.tool_calls:
            for call in msg.tool_calls:
                print(f"🔧 AGENT CALLS: {call['name']}({call['args']})")
        elif msg.type == "tool":
            print(f"📥 TOOL RESULT: {msg.content[:150]}...")

    answer = result["messages"][-1].content
    print(f"🤖 AGENT: {answer}")
    return answer


if __name__ == "__main__":
        # ask_agent("Generate user stories for the Refund module and save them.")
        ask_agent(
        "What is the Cash on Delivery limit? Then generate and save user stories "
        "for the Payment module, and list the saved Payment stories."
    )