import os
import subprocess
import webbrowser
import pyautogui
import time

class Toolset:
    def __init__(self):
        pass

    def run_tool(self, command):
        command = command.lower().strip()

        responses = []

        # Split instructions by 'and'
        steps = [part.strip() for part in command.split(" and ")]

        for step in steps:
            if "open notepad" in step:
                responses.append(self.open_notepad())

            elif "type" in step and "hello" in step:
                responses.append(self.type_in_notepad("Hello"))

            elif "close notepad" in step and "don't save" in step:
                responses.append(self.close_notepad_without_saving())

            elif "search" in step:
                query = step.split("search", 1)[-1].strip()
                responses.append(self.search_web(query))

            elif "open browser" in step:
                responses.append(self.open_browser("https://google.com"))

            elif "launch" in step:
                exe_name = self.extract_exe_name(step)
                responses.append(self.launch_program(exe_name))

            else:
                responses.append(f"❓ Could not understand: '{step}'")

        return "\n".join(responses)

    def open_notepad(self):
        try:
            subprocess.Popen("notepad.exe")
            time.sleep(1.5)  # Wait for window to come into focus
            return "📝 Notepad opened."
        except Exception as e:
            return f"❌ Failed to open Notepad: {e}"

    def type_in_notepad(self, text):
        try:
            time.sleep(1)  # Ensure Notepad is ready for typing
            pyautogui.write(text, interval=0.1)
            return f"⌨️ Typed: {text}"
        except Exception as e:
            return f"❌ Typing failed: {e}"

    def close_notepad_without_saving(self):
        try:
            pyautogui.hotkey('alt', 'f4')
            time.sleep(0.5)
            pyautogui.press('n')  # 'N' for "Don't Save"
            return "🛑 Notepad closed without saving."
        except Exception as e:
            return f"❌ Failed to close Notepad: {e}"

    def open_browser(self, url):
        try:
            webbrowser.open(url)
            return f"🌐 Browser opened: {url}"
        except Exception as e:
            return f"❌ Failed to open browser: {e}"

    def search_web(self, query):
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            return f"🔎 Searching Google for: {query}"
        except Exception as e:
            return f"❌ Failed to search the web: {e}"

    def launch_program(self, exe_name):
        try:
            subprocess.Popen(exe_name)
            return f"🚀 Launched {exe_name}"
        except Exception as e:
            return f"❌ Error launching {exe_name}: {e}"

    def extract_exe_name(self, command):
        # Basic heuristic to find .exe reference in the input
        words = command.split()
        for word in words:
            if word.endswith(".exe"):
                return word
        return "chrome.exe"  # Fallback default
