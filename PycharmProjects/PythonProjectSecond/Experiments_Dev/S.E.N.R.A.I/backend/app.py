from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Correct endpoint for OpenAI-compatible API from LM Studio
LMSTUDIO_API = "http://localhost:1234/v1/chat/completions"

@app.route("/query", methods=["POST"])
def query_llm():
    user_prompt = request.json.get("prompt", "")
    payload = {
        "model": "nous-hermes-2-mistral-7b-dpo",  # Match exactly what LM Studio shows
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }

    try:
        res = requests.post(LMSTUDIO_API, json=payload)
        res.raise_for_status()
        data = res.json()
        print("[DEBUG] LM Studio response:", data)  # Optional for debugging

        # Properly extract message content
        return jsonify({
            "response": data["choices"][0]["message"]["content"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5050)
