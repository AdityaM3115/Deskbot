from gemini_ai import ask_gemini

question = "Explain artificial intelligence in simple words."
reply = ask_gemini(question)

print("Gemini says:\n")
print(reply)