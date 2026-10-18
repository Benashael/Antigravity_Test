"""
Modern Graphical Chatbot Interface using Python's built-in Tkinter.
Zero installation required - works out of the box!
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import urllib.error
import json

from chatbot import SimpleChatbot


class ModernChatbotGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Nova - Python AI Chatbot")
        self.root.geometry("520x650")
        self.root.minsize(400, 500)

        # Initialize local chatbot engine
        self.local_bot = SimpleChatbot(bot_name="Nova")

        # LLM settings
        self.api_provider = tk.StringVar(value="Local (Offline)")
        self.api_key = tk.StringVar(value=os.environ.get("GEMINI_API_KEY", os.environ.get("OPENAI_API_KEY", "")))

        # Color Palette (Modern Dark Theme)
        self.bg_color = "#1e1e2e"
        self.panel_color = "#252538"
        self.user_bubble_color = "#3b82f6"
        self.bot_bubble_color = "#313244"
        self.text_color = "#cdd6f4"
        self.accent_color = "#89b4fa"

        self.root.configure(bg=self.bg_color)
        self._setup_ui()

    def _setup_ui(self):
        # Header Frame
        header = tk.Frame(self.root, bg=self.panel_color, height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_label = tk.Label(
            header,
            text="🤖 Nova AI Assistant",
            font=("Segoe UI", 14, "bold"),
            fg=self.accent_color,
            bg=self.panel_color,
        )
        title_label.pack(side=tk.LEFT, padx=16, pady=12)

        # Mode indicator / Settings button
        settings_btn = tk.Button(
            header,
            text="⚙️ Settings",
            font=("Segoe UI", 9),
            bg="#45475a",
            fg="#ffffff",
            activebackground="#585b70",
            activeforeground="#ffffff",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._open_settings_dialog,
        )
        settings_btn.pack(side=tk.RIGHT, padx=16, pady=12)

        self.mode_label = tk.Label(
            header,
            text="Mode: Local",
            font=("Segoe UI", 9, "italic"),
            fg="#a6adc8",
            bg=self.panel_color,
        )
        self.mode_label.pack(side=tk.RIGHT, padx=8, pady=12)

        # Chat History Display Area
        chat_frame = tk.Frame(self.root, bg=self.bg_color)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.chat_display = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            bg=self.bg_color,
            fg=self.text_color,
            font=("Segoe UI", 10),
            bd=0,
            padx=10,
            pady=10,
            state=tk.DISABLED,
            cursor="arrow",
        )
        scrollbar = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure Text Tags for Bubble-like formatting
        self.chat_display.tag_configure("user", foreground="#89b4fa", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_configure("bot", foreground="#a6e3a1", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_configure("system", foreground="#f38ba8", font=("Segoe UI", 9, "italic"))
        self.chat_display.tag_configure("body", foreground=self.text_color, font=("Segoe UI", 10))

        # Bottom Input Area
        input_frame = tk.Frame(self.root, bg=self.panel_color, padx=12, pady=10)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.entry_box = tk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            bg="#313244",
            fg="#ffffff",
            insertbackground="#ffffff",
            bd=0,
            relief=tk.FLAT,
        )
        self.entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 8))
        self.entry_box.bind("<Return>", lambda event: self._send_message())
        self.entry_box.focus_set()

        send_btn = tk.Button(
            input_frame,
            text="Send ➤",
            font=("Segoe UI", 10, "bold"),
            bg=self.user_bubble_color,
            fg="#ffffff",
            activebackground="#2563eb",
            activeforeground="#ffffff",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._send_message,
        )
        send_btn.pack(side=tk.RIGHT)

        # Welcome message
        self._append_message(
            "Nova",
            "Hello! I am your interactive Python chatbot. You can ask me questions, for jokes, math, or time. Type 'help' to see more!",
            "bot",
        )

    def _append_message(self, sender: str, text: str, tag: str):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}:\n", tag)
        self.chat_display.insert(tk.END, f"{text}\n\n", "body")
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def _send_message(self):
        user_text = self.entry_box.get().strip()
        if not user_text:
            return

        self.entry_box.delete(0, tk.END)
        self._append_message("You", user_text, "user")

        # Exit check
        if user_text.lower() in ["exit", "quit", "bye"]:
            self._append_message("Nova", "Goodbye! Have a wonderful day ahead!", "bot")
            self.root.after(1200, self.root.destroy)
            return

        provider = self.api_provider.get()

        if provider == "Local (Offline)":
            response = self.local_bot.respond(user_text)
            self._append_message(self.local_bot.bot_name, response, "bot")
        elif provider == "Google Gemini":
            self._append_message("Nova", "Thinking...", "system")
            threading.Thread(target=self._query_gemini, args=(user_text,), daemon=True).start()
        elif provider == "OpenAI":
            self._append_message("Nova", "Thinking...", "system")
            threading.Thread(target=self._query_openai, args=(user_text,), daemon=True).start()

    def _query_gemini(self, prompt: str):
        key = self.api_key.get().strip()
        if not key:
            self._update_last_bot_response("Error: Please set your Gemini API key in Settings!")
            return

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                self._update_last_bot_response(text)
        except Exception as e:
            self._update_last_bot_response(f"Gemini API Error: {str(e)}")

    def _query_openai(self, prompt: str):
        key = self.api_key.get().strip()
        if not key:
            self._update_last_bot_response("Error: Please set your OpenAI API key in Settings!")
            return

        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["choices"][0]["message"]["content"].strip()
                self._update_last_bot_response(text)
        except Exception as e:
            self._update_last_bot_response(f"OpenAI API Error: {str(e)}")

    def _update_last_bot_response(self, text: str):
        def _update():
            # Remove "Thinking..." and display result
            self.chat_display.configure(state=tk.NORMAL)
            # Find the last system message and replace it
            content = self.chat_display.get("1.0", tk.END)
            if "Nova:\nThinking...\n\n" in content:
                idx = content.rfind("Nova:\nThinking...\n\n")
                # Clear and rewrite or append
                self.chat_display.delete("end - 3 lines", "end")
            self.chat_display.insert(tk.END, "Nova:\n", "bot")
            self.chat_display.insert(tk.END, f"{text}\n\n", "body")
            self.chat_display.configure(state=tk.DISABLED)
            self.chat_display.see(tk.END)
        self.root.after(0, _update)

    def _open_settings_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Bot Settings")
        dialog.geometry("380x260")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()

        lbl_provider = tk.Label(dialog, text="Chatbot Engine:", fg=self.text_color, bg=self.bg_color, font=("Segoe UI", 10, "bold"))
        lbl_provider.pack(anchor=tk.W, padx=20, pady=(15, 5))

        combo = ttk.Combobox(
            dialog,
            textvariable=self.api_provider,
            values=["Local (Offline)", "Google Gemini", "OpenAI"],
            state="readonly",
            font=("Segoe UI", 10),
        )
        combo.pack(fill=tk.X, padx=20, pady=5)

        lbl_key = tk.Label(dialog, text="API Key (Required for Gemini/OpenAI):", fg=self.text_color, bg=self.bg_color, font=("Segoe UI", 10, "bold"))
        lbl_key.pack(anchor=tk.W, padx=20, pady=(15, 5))

        key_entry = tk.Entry(dialog, textvariable=self.api_key, show="*", font=("Segoe UI", 10), bg="#313244", fg="#ffffff", insertbackground="#ffffff")
        key_entry.pack(fill=tk.X, padx=20, pady=5)

        def save():
            self.mode_label.config(text=f"Mode: {self.api_provider.get().split()[0]}")
            dialog.destroy()

        save_btn = tk.Button(dialog, text="Save & Close", font=("Segoe UI", 10, "bold"), bg=self.user_bubble_color, fg="#ffffff", bd=0, padx=12, pady=6, cursor="hand2", command=save)
        save_btn.pack(pady=20)


def main():
    root = tk.Tk()
    app = ModernChatbotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
