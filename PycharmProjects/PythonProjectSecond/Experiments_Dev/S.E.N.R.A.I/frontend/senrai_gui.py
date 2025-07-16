import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from agent.senrai_agent import SENRAIAgent
from tools.command_toolkit import Toolset
import requests


class AgentWorker(QObject):
    finished = Signal(list)

    def __init__(self, agent, goal):
        super().__init__()
        self.agent = agent
        self.goal = goal

    def run(self):
        log = self.agent.run_agent_loop(self.goal, steps=3)
        self.finished.emit(log)


class SENRAIGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("S.E.N.R.A.I. - Self-Evolving Neural Response Assistant Infrastructure")
        self.setStyleSheet("""
            QWidget {
                background-color: #0E1117;
                color: #FFFFFF;
                font-family: Consolas, monospace;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #161B22;
                color: #D1D5DA;
                border: 1px solid #30363D;
                padding: 10px;
            }
            QPushButton {
                background-color: #238636;
                color: white;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2EA043;
            }
            QLabel#title {
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                color: #58A6FF;
            }
        """)

        self.agent = SENRAIAgent()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.title = QLabel("🧠 S.E.N.R.A.I.")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Type a message or command for SENRAI...")
        layout.addWidget(self.input_box)

        button_row = QHBoxLayout()
        self.chat_button = QPushButton("💬 Chat Mode")
        self.agent_button = QPushButton("🧠 Agent Mode")
        self.chat_button.clicked.connect(self.chat_mode)
        self.agent_button.clicked.connect(self.agent_mode)
        button_row.addWidget(self.chat_button)
        button_row.addWidget(self.agent_button)
        layout.addLayout(button_row)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

    def chat_mode(self):
        prompt = self.input_box.toPlainText()
        self.output_area.setPlainText("💬 Thinking...")
        try:
            res = requests.post("http://localhost:5050/query", json={"prompt": prompt})
            reply = res.json().get("response", "[No response]")
        except Exception as e:
            reply = f"[Error] {str(e)}"
        self.output_area.setPlainText(reply)

    def agent_mode(self):
        goal = self.input_box.toPlainText()
        self.output_area.setPlainText("🧠 SENRAI is thinking...\n")

        self.worker = AgentWorker(self.agent, goal)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.display_agent_result)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def display_agent_result(self, log):
        display_text = ""
        for i, (thought, plan, result) in enumerate(log, 1):
            display_text += (
                f"🔹 Step {i}\n"
                f"• Thought: {thought.strip()}\n"
                f"• Plan: {plan.strip()}\n"
                f"• Result: {result.strip()}\n\n"
            )
        self.output_area.setPlainText(display_text)
        self.thread.quit()
        self.thread.wait()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SENRAIGUI()
    gui.resize(800, 700)
    gui.show()
    sys.exit(app.exec())
