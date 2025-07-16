from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PySide6.QtCore import Qt
import requests
import sys

class AetheriusGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aetherius Assistant")
        self.setStyleSheet("background-color: #0F111A; color: white; font-family: Consolas;")

        layout = QVBoxLayout()

        self.title = QLabel("🤖 Aetherius Assistant")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.title)

        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Type your question or command here...")
        self.input_box.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.input_box)

        self.response_box = QTextEdit()
        self.response_box.setReadOnly(True)
        self.response_box.setStyleSheet("font-size: 14px; background-color: #1A1C25; padding: 10px;")
        layout.addWidget(self.response_box)

        self.ask_button = QPushButton("Ask Aetherius")
        self.ask_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #1F8AC0;")
        self.ask_button.clicked.connect(self.ask_llm)
        layout.addWidget(self.ask_button)

        self.setLayout(layout)

    def ask_llm(self):
        user_input = self.input_box.toPlainText()
        try:
            res = requests.post("http://localhost:5050/query", json={"prompt": user_input})
            reply = res.json().get("response", "[Error in response]")
        except Exception as e:
            reply = f"[Error] {str(e)}"
        self.response_box.setText(reply)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AetheriusGUI()
    gui.resize(700, 600)
    gui.show()
    sys.exit(app.exec())
