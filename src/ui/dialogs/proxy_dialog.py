from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit, 
                             QPushButton, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt

class ProxyDialog(QDialog):
    def __init__(self, parent=None, current_proxies=""):
        super().__init__(parent)
        self.setWindowTitle("Proxy Configuration")
        self.resize(500, 400)
        self.proxies = []
        
        layout = QVBoxLayout(self)
        
        # Instructions
        lbl = QLabel("Enter Proxies (One per line)\nFormat: ip:port:user:pass")
        lbl.setStyleSheet("font-weight: bold; color: #555; margin-bottom: 5px;")
        layout.addWidget(lbl)
        
        # Text Area
        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("192.168.1.1:8080:user:pass\n192.168.1.2:8080:user:pass")
        self.text_area.setText(current_proxies)
        self.text_area.setStyleSheet("""
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 5px;
            font-family: Consolas, monospace;
        """)
        layout.addWidget(self.text_area)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Proxies")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            background-color: #032EA1;
            color: white;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
        """)
        save_btn.clicked.connect(self.save_proxies)
        
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

    def save_proxies(self):
        text = self.text_area.toPlainText().strip()
        if not text:
            self.proxies = []
            self.accept()
            return

        lines = text.split('\n')
        valid_proxies = []
        for line in lines:
            line = line.strip()
            if not line: continue
            # Basic validation
            parts = line.split(':')
            if len(parts) >= 2: # At least IP:Port
                valid_proxies.append(line)
        
        self.proxies = valid_proxies
        self.accept()

    def get_proxy_text(self):
        return self.text_area.toPlainText()
