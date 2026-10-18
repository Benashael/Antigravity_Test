"""
Command-Line AI Chatbot powered by Google Gemini, OpenAI, or Local Ollama.
Uses standard Python library (zero pip packages required)!
"""

import json
import os
import sys
import urllib.error
import urllib.request


class AIChatbot:
    def __init__(self, provider: str = "gemini", api_key: str | None = None, model: str | None = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") if self.provider == "gemini" else os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.history = []

        if self.provider == "gemini":
            self.model = self.model or "gemini-1.5-flash"
        elif self.provider == "openai":
            self.model = self.model or "gpt-4o-mini"
        elif self.provider == "ollama":
            self.model = self.model or "llama3"

    def chat_gemini(self, user_message: str) -> str:
        if not self.api_key:
            return "Error: GEMINI_API_KEY is not set. Please provide an API key."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        # Build multi-turn context
        contents = []
        for turn in self.history:
            role = "user" if turn["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": turn["text"]}]})
        contents.append({"role": "user", "parts": [{"text": user_message}]})

        payload = {"contents": contents}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                self.history.append({"role": "user", "text": user_message})
                self.history.append({"role": "model", "text": reply})
                return reply
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            return f"Gemini API HTTP Error {e.code}: {error_body}"
        except Exception as e:
            return f"Network Error: {str(e)}"

    def chat_openai(self, user_message: str) -> str:
        if not self.api_key:
            return "Error: OPENAI_API_KEY is not set. Please provide an API key."

        url = "https://api.openai.com/v1/chat/completions"
        messages = [{"role": turn["role"], "content": turn["text"]} for turn in self.history]
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": messages,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data["choices"][0]["message"]["content"].strip()
                self.history.append({"role": "user", "text": user_message})
                self.history.append({"role": "assistant", "text": reply})
                return reply
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            return f"OpenAI API HTTP Error {e.code}: {error_body}"
        except Exception as e:
            return f"Network Error: {str(e)}"

    def chat_ollama(self, user_message: str) -> str:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": self.model,
            "prompt": user_message,
            "stream": False,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data.get("response", "").strip()
                return reply
        except urllib.error.URLError:
            return "Error: Could not connect to local Ollama server at http://localhost:11434. Make sure Ollama is running."
        except Exception as e:
            return f"Error: {str(e)}"

    def send(self, message: str) -> str:
        if self.provider == "gemini":
            return self.chat_gemini(message)
        elif self.provider == "openai":
            return self.chat_openai(message)
        elif self.provider == "ollama":
            return self.chat_ollama(message)
        return "Unknown provider."


def main():
    print("=" * 60)
    print("🧠 Python AI LLM Chatbot")
    print("=" * 60)
    print("Select an AI backend:")
    print("1) Google Gemini (Free tier available)")
    print("2) OpenAI (ChatGPT)")
    print("3) Local Ollama (100% offline, free)")

    choice = input("\nSelect [1-3] (Default: 1): ").strip() or "1"
    provider_map = {"1": "gemini", "2": "openai", "3": "ollama"}
    provider = provider_map.get(choice, "gemini")

    api_key = None
    if provider in ["gemini", "openai"]:
        env_var = "GEMINI_API_KEY" if provider == "gemini" else "OPENAI_API_KEY"
        api_key = os.environ.get(env_var)
        if not api_key:
            api_key = input(f"Enter your {provider.capitalize()} API Key: ").strip()

    bot = AIChatbot(provider=provider, api_key=api_key)
    print(f"\nConnected to {provider.upper()} ({bot.model}). Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Bot: Goodbye!")
                break
            print("\nThinking...")
            reply = bot.send(user_input)
            print(f"\nBot: {reply}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
