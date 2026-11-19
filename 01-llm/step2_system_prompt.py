# Step 2: Same question, with and without a SYSTEM prompt (local Ollama)

import ollama

MODEL = "llama3.2"


def ask(question, system_prompt=None):
    """Send a question (with an optional system prompt) and return the answer text."""
    messages = []

    # The system prompt is just a message with role "system", placed FIRST
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": question})

    response = ollama.chat(model=MODEL, messages=messages)
    return response.message.content


question = "What is regression testing?"

# Run 1: NO system prompt
print("========== WITHOUT system prompt ==========")
print(ask(question))

# Run 2: WITH system prompt
qa_system_prompt = (
    "You are a senior QA engineer with 10 years of experience. "
    "Answer in maximum 3 short bullet points. "
    "Always end with one practical tip for testers."
)
print("\n========== WITH system prompt ==========")
print(ask(question, system_prompt=qa_system_prompt))