# Step 2: Same question, with and without a SYSTEM prompt (local Ollama)

import ollama

MODEL = "qwen2.5:7b"


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
question2 = "Explain smoke, sanity and regression testing?"

# Run 1: NO system prompt
print("========== WITHOUT system prompt ==========")
print(ask(question))

# Run 2: WITH system prompt (Senior QA)
qa_system_prompt = (
    "You are a senior QA engineer with 10 years of experience. "
    "Answer in maximum 3 short bullet points. "
    "Always end with one practical tip for testers."
)
print("\n========== WITH system prompt ==========")
print(ask(question, system_prompt=qa_system_prompt))

# Run 3: TEACHER persona (Exercise 1)
teacher_system_prompt = (
    "You are a teacher explaining to a 10-year-old child. "
    "Use a simple real-life example."
)
print("\n========== TEACHER (10-year-old) ==========")
print(ask(question, system_prompt=teacher_system_prompt))

#Run 4: Force a table format
table_format_system_prompt = ( "Answer ONLY as a markdown table with exactly 3 columns: Term | Meaning | Example. "
                               "Do not write anything before or after the table." )

print("\n========== Force table format =============")
print(ask(question2,system_prompt=table_format_system_prompt))