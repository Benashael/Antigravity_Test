"""
Simple Interactive Chatbot in Python.
No external libraries required - runs with standard Python!
"""

import datetime
import random
import re
import sys


class SimpleChatbot:
    def __init__(self, bot_name="Nova"):
        self.bot_name = bot_name
        self.user_name = None
        self.jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the Python programmer get glasses? Because they couldn't C#!",
            "There are only 10 types of people in the world: those who understand binary and those who don't.",
            "How do you comfort a JavaScript bug? You console it!",
            "Why was the computer cold? It left its Windows open!",
        ]

    def get_greeting(self) -> str:
        name_part = f", {self.user_name}" if self.user_name else ""
        greetings = [
            f"Hello{name_part}! How can I help you today?",
            f"Hi there{name_part}! What's on your mind?",
            f"Hey{name_part}! Great to chat with you.",
        ]
        return random.choice(greetings)

    def extract_name(self, text: str) -> str | None:
        patterns = [
            r"\bmy name is ([a-zA-Z]+)\b",
            r"\bi am ([a-zA-Z]+)\b",
            r"\bi'm ([a-zA-Z]+)\b",
            r"\bcall me ([a-zA-Z]+)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).capitalize()
        return None

    def evaluate_math(self, text: str) -> str | None:
        # Match expressions like "calculate 12 + 4" or "what is 5 * 20"
        match = re.search(r"(?:calculate|what is|solve)\s+([0-9\s\+\-\*\/\.\(\)]+)", text, re.IGNORECASE)
        if match:
            expr = match.group(1).strip()
            # Safety check: allow only digits and basic arithmetic operators
            if re.fullmatch(r"[0-9\s\+\-\*\/\.\(\)]+", expr):
                try:
                    # Safe evaluation with no built-ins
                    result = eval(expr, {"__builtins__": None}, {})
                    return f"The answer to {expr} is {result}."
                except Exception:
                    return "Sorry, I couldn't calculate that expression."
        return None

    def respond(self, message: str) -> str:
        cleaned = message.strip()
        lower_msg = cleaned.lower()

        if not cleaned:
            return "You didn't say anything! Feel free to ask me something."

        # Exit commands
        if lower_msg in ["bye", "goodbye", "exit", "quit", "see you"]:
            return "EXIT"

        # Check for name introduction
        new_name = self.extract_name(cleaned)
        if new_name:
            self.user_name = new_name
            return f"Nice to meet you, {self.user_name}! I'll remember your name."

        # Asking for bot's name
        if "your name" in lower_msg or "who are you" in lower_msg:
            return f"I'm {self.bot_name}, your friendly Python assistant!"

        # Asking for user's name
        if "my name" in lower_msg:
            if self.user_name:
                return f"Your name is {self.user_name}!"
            return "I don't think you've told me your name yet. You can say 'My name is [your name]'."

        # Greetings
        if re.search(r"\b(hi|hello|hey|greetings|howdy)\b", lower_msg):
            return self.get_greeting()

        # How are you
        if "how are you" in lower_msg or "how's it going" in lower_msg:
            return "I'm doing fantastic, thank you for asking! How are you doing?"

        # Help
        if lower_msg in ["help", "what can you do", "commands"]:
            return (
                "Here are a few things you can ask me:\n"
                "  - 'Hello' or 'How are you?'\n"
                "  - 'My name is Alice' (I'll remember it!)\n"
                "  - 'What is the time?' or 'What is today's date?'\n"
                "  - 'Tell me a joke'\n"
                "  - 'Calculate 15 * 8'\n"
                "  - 'Exit' or 'Quit' to leave"
            )

        # Time and date
        if "time" in lower_msg:
            now = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {now}."
        if "date" in lower_msg or "today" in lower_msg:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {today}."

        # Jokes
        if "joke" in lower_msg:
            return random.choice(self.jokes)

        # Math calculations
        math_result = self.evaluate_math(lower_msg)
        if math_result:
            return math_result

        # Thanks
        if "thank" in lower_msg:
            return "You're very welcome!"

        # Fallback responses
        fallbacks = [
            "I'm not sure I understand. Type 'help' to see what I can do!",
            "Interesting! Could you rephrase that, or type 'help' for suggestions?",
            "I'm still learning! Ask me for the time, a joke, or some math.",
        ]
        return random.choice(fallbacks)


def main():
    bot = SimpleChatbot(bot_name="Nova")
    print("=" * 50)
    print(f"🤖 Welcome to {bot.bot_name} Chatbot!")
    print("Type 'help' to see what I can do, or 'quit' to exit.")
    print("=" * 50)

    while True:
        try:
            user_input = input("\nYou: ")
            response = bot.respond(user_input)
            if response == "EXIT":
                farewell = f"Goodbye {bot.user_name}! Have a great day!" if bot.user_name else "Goodbye! Have a great day!"
                print(f"\n{bot.bot_name}: {farewell}")
                break
            print(f"\n{bot.bot_name}: {response}")
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{bot.bot_name}: Goodbye! Exiting session.")
            sys.exit(0)


if __name__ == "__main__":
    main()
