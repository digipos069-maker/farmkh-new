
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QFrame)
from PyQt5.QtCore import Qt
from .styles import get_stylesheet
from .reg_account_page import RegAccountPage
from .device_manager import DeviceManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TikTok Automation Manager")
        self.resize(1200, 800) # Increased size for split view
        self.setStyleSheet(get_stylesheet())
        
        # Main Container (Horizontal Split)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_split_layout = QHBoxLayout(central_widget)
        main_split_layout.setContentsMargins(0, 0, 0, 0)
        main_split_layout.setSpacing(0)
        
        # --- LEFT PANEL: Device Manager ---
        self.device_manager = DeviceManager()
        main_split_layout.addWidget(self.device_manager)
        
        # --- RIGHT PANEL: Content Area (TopBar + Pages) ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Top Navigation Bar
        self.top_bar = QFrame()
        self.top_bar.setObjectName("TopBar")
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(10, 0, 10, 0)
        top_bar_layout.setSpacing(5)
        
        # App Title
        title = QLabel("TikTok Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 0 20px; color: #032EA1;")
        top_bar_layout.addWidget(title)
        
        # Navigation Buttons
        self.nav_buttons = []
        self.create_nav_button("Dashboard", 0)
        self.create_nav_button("Accounts", 1)
        self.create_nav_button("Reg Account", 2)
        self.create_nav_button("Automation", 3)
        self.create_nav_button("Settings", 4)
        
        top_bar_layout.addStretch()
        right_layout.addWidget(self.top_bar)
        
        # Main Content Stack
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("MainContent")
        
        # Pages
        self.content_stack.addWidget(self.create_page("Dashboard Content"))
        self.content_stack.addWidget(self.create_page("Account Management"))
        self.content_stack.addWidget(RegAccountPage())
        self.content_stack.addWidget(self.create_page("Automation Tasks"))
        self.content_stack.addWidget(self.create_page("Settings"))
        
        right_layout.addWidget(self.content_stack)
        
        # Add Right Panel to Main Split
        main_split_layout.addWidget(right_panel)
        
        # Set default page
        self.switch_page(0)

    def create_nav_button(self, text, index):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(60)
        btn.clicked.connect(lambda: self.switch_page(index))
        self.top_bar.layout().addWidget(btn)
        self.nav_buttons.append(btn)

    def switch_page(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        self.content_stack.setCurrentIndex(index)

    def create_page(self, text):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel(text)
        label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(label)
        
        if "Dashboard" in text:
            msg = QLabel("Welcome to TikTok Automation Manager.\nSelect a module from the sidebar to begin.")
            msg.setAlignment(Qt.AlignCenter)
            layout.addWidget(msg)
            btn = QPushButton("Start New Task")
            btn.setObjectName("PrimaryButton")
            btn.setFixedWidth(200)
            layout.addWidget(btn, alignment=Qt.AlignCenter)
            layout.addStretch()
            
        elif "Account" in text:
            from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
            table = QTableWidget(5, 3)
            table.setHorizontalHeaderLabels(["Username", "Status", "Last Activity"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setStyleSheet("""
                QHeaderView::section {
                    background-color: #032EA1;
                    color: white;
                    padding: 5px;
                    border: 1px solid #02268a;
                }
                QTableWidget {
                    gridline-color: #e0e0e0;
                    border: 1px solid #e0e0e0;
                }
            """)
            
            # Sample Data
            accounts = [("user_alpha", "Active", "2 mins ago"), ("bot_test_1", "Idle", "1 hour ago")]
            for i, (user, status, activity) in enumerate(accounts):
                table.setItem(i, 0, QTableWidgetItem(user))
                table.setItem(i, 1, QTableWidgetItem(status))
                table.setItem(i, 2, QTableWidgetItem(activity))
                
            layout.addWidget(table)
            
        else:
            label.setAlignment(Qt.AlignCenter)
            layout.addStretch()
            
        return page

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
