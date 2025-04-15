from flask import Flask, render_template, request, jsonify
import requests
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Load keys from environment or fallback (use your actual keys here if needed)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "your-openai-key"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "your-google-key"
GOOGLE_CX = os.getenv("GOOGLE_CSE_ID") or "your-google-cx"

openai.api_key = OPENAI_API_KEY

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query", "").strip().lower()

    # Simple conversational triggers
    chat_prompts = ["how are you", "what's your name", "who are you", "hello", "hi"]
    if any(prompt in query for prompt in chat_prompts):
        chat_response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": query}]
        )
        answer = chat_response.choices[0].message.content
        return jsonify({"response": answer})

    # Sena/Sana special case
    if "sena" in query or "sana" in query:
        sena_url = f"https://www.googleapis.com/customsearch/v1?q=site:sena.services+{query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}"
        sena_res = requests.get(sena_url).json()

        if sena_res.get("items"):
            return jsonify({"response": sena_res['items'][0]['snippet']})
        else:
            # Fallback to Google search for cricket results
            cricket_url = f"https://www.googleapis.com/customsearch/v1?q=Cricket results from March 09, 2025&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}"
            cricket_res = requests.get(cricket_url).json()
            if cricket_res.get("items"):
                return jsonify({"response": cricket_res['items'][0]['snippet']})
            else:
                return jsonify({"response": "No results found for Sena or cricket."})

    # Default Google search path
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}"
    search_res = requests.get(search_url).json()

    if search_res.get("items"):
        return jsonify({"response": search_res['items'][0]['snippet']})

    # Final fallback to ChatGPT
    fallback_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}]
    )
    fallback_answer = fallback_response.choices[0].message.content
    return jsonify({"response": fallback_answer})


if __name__ == "__main__":
    app.run(debug=True, port=5000)


