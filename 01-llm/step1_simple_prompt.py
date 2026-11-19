# Step 1: Send a simple question to a LOCAL LLM (Ollama) and print the answer + token usage

import ollama   # official Ollama Python library (talks to localhost:11434)

MODEL = "qwen2.5:7b"

# 1. The question
question = "Explain the difference between smoke testing and sanity testing in 3 lines."

# 2. Send it to the local model
response = ollama.chat(
    model=MODEL,
    messages=[
        {"role": "user", "content": question},
    ],
)

# 3. Print the answer
print("--- Question ---")
print(question)
print("\n--- Answer ---")
print(response.message.content)

# 4. Print token usage + time taken
print("\n--- Token usage ---")
print("Input tokens :", response.prompt_eval_count)
print("Output tokens:", response.eval_count)
print("Total time   :", round(response.total_duration / 1_000_000_000, 2), "seconds")