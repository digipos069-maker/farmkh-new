from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHBoxLayout, 
                             QHeaderView, QFrame, QRadioButton, QComboBox, QButtonGroup, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from src.core.adb_manager import ADBManager
import os
import threading

class DeviceManager(QWidget):
    device_selected = pyqtSignal(object)
    config_changed = pyqtSignal(object)
    refresh_requested = pyqtSignal()
    devices_loaded = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.setFixedWidth(320) # Slightly wider for table
        self.apk_folder = "config/apk"
        self._scan_thread = None
        self.init_ui()
        self.refresh_requested.connect(self.refresh_devices_async)
        self.devices_loaded.connect(self._apply_device_list)
        self.scan_and_refresh_async() # Initial load

    def toggle_delay_inputs(self, button):
        id = self.delay_group.id(button)
        # 0 = Delay Device, 1 = Delay Click
        self.dd_input.setEnabled(id == 0)
        self.dc_input.setEnabled(id == 1)
        self.emit_config()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Device Manager")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # --- App Management Options ---
        app_mgmt_layout = QHBoxLayout()
        app_mgmt_layout.setSpacing(10)
        
        self.mgmt_group = QButtonGroup(self)
        
        # Option 1: Clear Cache
        rb_clear = QRadioButton("Clear Cache")
        rb_clear.setCursor(Qt.PointingHandCursor)
        rb_clear.setChecked(True)
        self.mgmt_group.addButton(rb_clear, 0)
        app_mgmt_layout.addWidget(rb_clear)
        
        # Option 2: Re-install
        # We need a small container for radio + combo to keep them together in the HBox
        reinstall_container = QWidget()
        reinstall_layout = QHBoxLayout(reinstall_container)
        reinstall_layout.setContentsMargins(0, 0, 0, 0)
        reinstall_layout.setSpacing(5)
        
        rb_reinstall = QRadioButton("Re-install")
        rb_reinstall.setCursor(Qt.PointingHandCursor)
        self.mgmt_group.addButton(rb_reinstall, 1)
        
        self.apk_combo = QComboBox()
        self.apk_combo.setCursor(Qt.PointingHandCursor)
        self.apk_combo.setPlaceholderText("Select APK")
        self.apk_combo.setFixedWidth(100) # Limit width to fit
        self.apk_combo.setEnabled(False) 
        
        reinstall_layout.addWidget(rb_reinstall)
        reinstall_layout.addWidget(self.apk_combo)
        
        app_mgmt_layout.addWidget(reinstall_container)
        app_mgmt_layout.addStretch()
        
        self.mgmt_group.buttonClicked.connect(self.toggle_mgmt_mode)

        
        # Wrap in VBox to add Separator below
        top_container = QVBoxLayout()
        top_container.addLayout(app_mgmt_layout)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        top_container.addWidget(line)
        
        # --- Delay Options ---
        delay_layout = QHBoxLayout()
        delay_layout.setSpacing(5)
        
        self.delay_group = QButtonGroup(self)
        self.delay_group.setExclusive(False) # Allow unchecking if needed, or maybe treat as checkboxes? 
        # User said "radio box", usually implies exclusive. Let's make them exclusive for configuration focus.
        self.delay_group.setExclusive(True)

        # Delay Device
        rb_dd = QRadioButton("Delay Device")
        rb_dd.setCursor(Qt.PointingHandCursor)
        self.delay_group.addButton(rb_dd, 0)
        
        self.dd_input = QSpinBox()
        self.dd_input.setRange(0, 60)
        self.dd_input.setSuffix("s")
        self.dd_input.setFixedWidth(50)
        self.dd_input.setEnabled(False)
        
        # Delay Click
        rb_dc = QRadioButton("Delay Click")
        rb_dc.setCursor(Qt.PointingHandCursor)
        self.delay_group.addButton(rb_dc, 1)
        
        self.dc_input = QSpinBox()
        self.dc_input.setRange(0, 60)
        self.dc_input.setSuffix("s")
        self.dc_input.setFixedWidth(50)
        self.dc_input.setEnabled(False)
        
        delay_layout.addWidget(rb_dd)
        delay_layout.addWidget(self.dd_input)
        delay_layout.addSpacing(10)
        delay_layout.addWidget(rb_dc)
        delay_layout.addWidget(self.dc_input)
        delay_layout.addStretch()
        
        self.delay_group.buttonClicked.connect(self.toggle_delay_inputs)
        top_container.addLayout(delay_layout)
        
        layout.addLayout(top_container)
        self.refresh_apks() # Load APKs
        
        # Device Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Status"])
        
        # Table Styling
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False) # Hide row numbers
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.MultiSelection)
        
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 4px;
                border: none;
                border-bottom: 1px solid #ddd;
                font-weight: bold;
                color: #555;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        layout.addWidget(self.table)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemClicked.connect(self.on_item_clicked)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        refresh_btn.clicked.connect(self.refresh_devices_async)
        
        connect_btn = QPushButton("Connect")
        connect_btn.setCursor(Qt.PointingHandCursor)
        connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #032EA1;
                color: white;
                border-radius: 4px;
                padding: 6px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #02268a; }
        """)
        connect_btn.clicked.connect(self.scan_and_refresh_async)
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(connect_btn)
        layout.addLayout(btn_layout)
        
        # Styles for the panel
        self.setStyleSheet("border-right: 1px solid #e0e0e0; background-color: #f9f9f9;")
        self.apk_combo.currentIndexChanged.connect(self.emit_config)
        self.dd_input.valueChanged.connect(lambda _: self.emit_config())
        self.dc_input.valueChanged.connect(lambda _: self.emit_config())
        self.emit_config()

    def scan_and_refresh_async(self):
        if self._scan_thread and self._scan_thread.is_alive():
            return

        def worker():
            ADBManager.attempt_emulator_connection()
            self.refresh_requested.emit()

        self._scan_thread = threading.Thread(target=worker, daemon=True)
        self._scan_thread.start()

    def refresh_devices_async(self):
        def worker():
            devices = ADBManager.get_connected_devices()
            self.devices_loaded.emit(devices)

        threading.Thread(target=worker, daemon=True).start()

    def toggle_mgmt_mode(self, button):
        # Index 1 is Re-install
        is_reinstall = (self.mgmt_group.id(button) == 1)
        self.apk_combo.setEnabled(is_reinstall)
        if is_reinstall:
            self.refresh_apks()
        self.emit_config()

    def refresh_apks(self):
        self.apk_combo.clear()
        if os.path.exists(self.apk_folder):
            apk_list = []
            for root, dirs, files in os.walk(self.apk_folder):
                for file in files:
                    if file.endswith(".apk"):
                        # Get relative path from apk_folder for display
                        rel_path = os.path.relpath(os.path.join(root, file), self.apk_folder)
                        apk_list.append(rel_path)
            
            if apk_list:
                for rel_path in sorted(apk_list):
                    display_name = os.path.splitext(os.path.basename(rel_path))[0]
                    self.apk_combo.addItem(display_name, rel_path)
            else:
                self.apk_combo.addItem("No APKs found")
        else:
            self.apk_combo.addItem("Config folder missing")
        self.emit_config()

    def refresh_devices(self):
        self.table.setRowCount(0) # Clear existing rows
        self.device_selected.emit([])

    def _apply_device_list(self, devices):
        self.refresh_devices()
        if not devices:
            return
        for dev in devices:
            self.add_device(dev['id'], dev['name'], dev['status'])

    def add_device(self, id_val, name, status):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Create items
        id_item = QTableWidgetItem(id_val)
        name_item = QTableWidgetItem(name)
        status_item = QTableWidgetItem(status)
        
        # Center text
        id_item.setTextAlignment(Qt.AlignCenter)
        status_item.setTextAlignment(Qt.AlignCenter)
        
        # Set items
        self.table.setItem(row, 0, id_item)
        self.table.setItem(row, 1, name_item)
        self.table.setItem(row, 2, status_item)

    def on_selection_changed(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.device_selected.emit([])
            return

        row_ids = []
        seen_rows = set()
        for item in selected_items:
            row = item.row()
            if row in seen_rows:
                continue
            seen_rows.add(row)
            id_item = self.table.item(row, 0)
            if id_item and id_item.text():
                row_ids.append(id_item.text())

        self.device_selected.emit(row_ids)

    def on_item_clicked(self, item):
        # If multiple rows are selected, collapse to just the clicked row.
        if self.table.selectedItems() and len(self.table.selectionModel().selectedRows()) > 1:
            row = item.row()
            self.table.blockSignals(True)
            self.table.clearSelection()
            self.table.selectRow(row)
            self.table.blockSignals(False)
            self.on_selection_changed()

    def emit_config(self):
        self.config_changed.emit(self.get_current_config())

    def get_current_config(self):
        mgmt_id = self.mgmt_group.checkedId()
        mgmt_mode = "clear_cache" if mgmt_id == 0 else "reinstall"

        apk_text = ""
        if self.apk_combo.isEnabled():
            apk_text = self.apk_combo.currentData()
            if not apk_text and self.apk_combo.currentText() in ("No APKs found", "Config folder missing", ""):
                apk_text = ""

        delay_id = self.delay_group.checkedId()
        if delay_id == 0:
            delay_type = "device"
            delay_seconds = int(self.dd_input.value())
        elif delay_id == 1:
            delay_type = "click"
            delay_seconds = int(self.dc_input.value())
        else:
            delay_type = None
            delay_seconds = 0

        return {
            "mgmt_mode": mgmt_mode,
            "apk_rel_path": apk_text,
            "apk_folder": self.apk_folder,
            "delay_type": delay_type,
            "delay_seconds": delay_seconds,
        }

    def set_device_status(self, device_id, status_text):
        if not device_id:
            return
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            if id_item and id_item.text() == device_id:
                status_item = self.table.item(row, 2)
                if not status_item:
                    status_item = QTableWidgetItem("")
                    status_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, 2, status_item)
                status_item.setText(status_text)
                break
