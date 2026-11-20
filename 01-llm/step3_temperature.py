# Step 3: Temperature - same request, different randomness

import ollama

MODEL = "qwen2.5:7b"


def ask(question, temperature):
    """Send a question with a given temperature and return the answer text."""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        options={"temperature": temperature},  # 0 = same every time, 1 = more varied
    )
    return response.message.content


# # Quick check
# if __name__ == "__main__":
#     print(ask("Say about India in 10 words", temperature=0))


if __name__ == "__main__":
    question = (
        "Write ONE short user story title for this requirement: "
        "BR-CART-01: Users can add up to 15 different products to the cart."
    )

    for temp in [0, 1]:
        print(f"\n===== Temperature {temp} =====")
        answers = []
        for run in range(1, 6):
            answer = ask(question, temperature=temp).strip()
            answers.append(answer)
            has_fact = "15" in answer
            print(f"Run {run}: {'✅' if has_fact else '❌ missing 15'}  {answer}")

        # after the 5 runs (4 spaces, NOT inside the run loop)
        print(f"--> Unique answers: {len(set(answers))} out of 5")
        passed = sum("15" in a for a in answers)
        print(f"--> Fact check ('15' present): {passed} out of 5")