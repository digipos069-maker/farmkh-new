from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit, 
                             QPushButton, QHBoxLayout, QGroupBox)
from PyQt5.QtCore import Qt

class NameDialog(QDialog):
    def __init__(self, parent=None, first_names=None, last_names=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Name Configuration")
        self.resize(400, 500)
        self.first_names = first_names if first_names else []
        self.last_names = last_names if last_names else []
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Instructions
        lbl = QLabel("Enter Custom Names (One per line)")
        lbl.setStyleSheet("font-weight: bold; color: #555; font-size: 14px;")
        layout.addWidget(lbl)
        
        # Inputs Group
        gb = QGroupBox()
        gb.setStyleSheet("border: 1px solid #cccccc; border-radius: 4px; background-color: white;")
        gb_layout = QVBoxLayout(gb)
        
        # First Names
        gb_layout.addWidget(QLabel("First Names:"))
        self.first_name_input = QTextEdit()
        self.first_name_input.setPlaceholderText("John\nAlice\nBob")
        self.first_name_input.setText("\n".join(self.first_names))
        self.first_name_input.setStyleSheet("padding: 5px; border: none; border-radius: 3px;")
        gb_layout.addWidget(self.first_name_input)
        
        # Last Names
        gb_layout.addWidget(QLabel("Last Names:"))
        self.last_name_input = QTextEdit()
        self.last_name_input.setPlaceholderText("Doe\nSmith\nJohnson")
        self.last_name_input.setText("\n".join(self.last_names))
        self.last_name_input.setStyleSheet("padding: 5px; border: none; border-radius: 3px;")
        gb_layout.addWidget(self.last_name_input)
        
        layout.addWidget(gb)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            background-color: #032EA1;
            color: white;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
        """)
        save_btn.clicked.connect(self.save_data)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            background-color: #f5f5f5;
            color: #333;
            padding: 8px 15px;
            border-radius: 4px;
            border: 1px solid #cccccc;
        """)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def save_data(self):
        # Helper to clean and split lines
        def get_lines(text_edit):
            text = text_edit.toPlainText().strip()
            if not text: return []
            return [line.strip() for line in text.split('\n') if line.strip()]

        self.first_names = get_lines(self.first_name_input)
        self.last_names = get_lines(self.last_name_input)
        self.accept()