from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QSpinBox, QFileDialog, 
                             QTextEdit, QFrame, QComboBox, QCheckBox, 
                             QStackedWidget, QScrollArea, QRadioButton, 
                             QButtonGroup, QGroupBox, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from src.core.adb_manager import ADBManager
import os
import threading
import time
from src.core.registration import RegistrationBot
from .dialogs.proxy_dialog import ProxyDialog
from .dialogs.name_dialog import NameDialog
from .widgets.selection_input import SelectionInput

class Signaler(QObject):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class RegAccountPage(QWidget):
    device_status_signal = pyqtSignal(str, str)
    FACEBOOK_PACKAGE = "com.facebook.katana"
    GET_STARTED_TEXTS = ["Get Started", "Get start", "Get Start", "GET STARTED"]
    def __init__(self):
        super().__init__()
        self.bot = None
        self.signaler = Signaler()
        self.signaler.log_signal.connect(self.append_log)
        self.signaler.finished_signal.connect(self.on_registration_finished)
        self.proxy_data = "" 
        self.proxy_list = [] 
        self.custom_first_names = []
        self.custom_last_names = []
        self.selected_device_ids = []
        self.current_device_id = None
        self.device_config = {}
        self.multi_run_active = False
        self._multi_stop_event = None
        self.init_ui()

    def init_ui(self):
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        # Add main layout components
        
        # 1. Scroll Area for Config & Logs
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # --- Main Configuration Row ---
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(12)
        row_layout.setAlignment(Qt.AlignCenter)
        
        # Define a specific style for these group boxes to ensure borders show
        gb_style = """
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 10px;
                background-color: white;
                font-size: 11px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #032EA1;
                font-weight: bold;
            }
        """

        # 1. Network Group
        gb_net = QGroupBox("Network IP")
        gb_net.setStyleSheet(gb_style)
        
        net_main_layout = QVBoxLayout(gb_net)
        net_main_layout.setContentsMargins(5, 15, 5, 15) # Equal Top/Bottom
        net_main_layout.setSpacing(5)
        net_main_layout.setAlignment(Qt.AlignCenter)
        
        self.network_group = QButtonGroup(self)
        
        # --- Row 1: 5G, Proxy, Wifi ---
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(10)
        row1_layout.setAlignment(Qt.AlignCenter)
        
        networks_row1 = ["5G", "Proxy", "Wifi"]
        for i, net in enumerate(networks_row1):
            if net == "Proxy":
                # Proxy with Clickable Label
                proxy_container = QWidget()
                pc_layout = QHBoxLayout(proxy_container)
                pc_layout.setContentsMargins(0, 0, 0, 0)
                pc_layout.setSpacing(2)
                
                rb = QRadioButton("")
                self.network_group.addButton(rb, i)
                
                lbl = ClickableLabel("Proxy")
                lbl.setCursor(Qt.PointingHandCursor)
                lbl.setStyleSheet("color: #032EA1; font-weight: bold;")
                lbl.clicked.connect(self.open_proxy_config)
                
                pc_layout.addWidget(rb)
                pc_layout.addWidget(lbl)
                row1_layout.addWidget(proxy_container)
            else:
                rb = QRadioButton(net)
                if i == 0: rb.setChecked(True)
                self.network_group.addButton(rb, i)
                row1_layout.addWidget(rb)
        
        net_main_layout.addLayout(row1_layout)
        
        # --- Row 2: OpenVPN ---
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(5)
        row2_layout.setAlignment(Qt.AlignCenter)
        
        vpn_rb = QRadioButton("OpenVPN")
        self.network_group.addButton(vpn_rb, 3)
        row2_layout.addWidget(vpn_rb)
        
        self.vpn_mode = SelectionInput(items=["Current", "Random"], width=70, height=22)
        self.vpn_mode.setEnabled(False)
        self.network_group.buttonClicked.connect(self.toggle_vpn_mode)
        
        row2_layout.addWidget(self.vpn_mode)
        net_main_layout.addLayout(row2_layout)

        row_layout.addWidget(gb_net)

        # 2. Name Group
        gb_name = QGroupBox("Name")
        gb_name.setStyleSheet(gb_style)
        name_l = QVBoxLayout(gb_name)
        name_l.setContentsMargins(5, 15, 5, 15) # Adjusted
        name_l.setAlignment(Qt.AlignCenter)
        
        self.name_group = QButtonGroup(self)
        
        # Auto English
        rb_auto = QRadioButton("Auto English")
        rb_auto.setChecked(True)
        self.name_group.addButton(rb_auto, 0)
        name_l.addWidget(rb_auto, alignment=Qt.AlignCenter)
        
        # Custom
        custom_container = QWidget()
        cc_layout = QHBoxLayout(custom_container)
        cc_layout.setContentsMargins(0, 0, 0, 0)
        cc_layout.setSpacing(2)
        cc_layout.setAlignment(Qt.AlignCenter)
        
        rb_custom = QRadioButton("")
        self.name_group.addButton(rb_custom, 1)
        
        lbl_custom = ClickableLabel("Custom")
        lbl_custom.setCursor(Qt.PointingHandCursor)
        lbl_custom.setStyleSheet("color: #032EA1; font-weight: bold;")
        lbl_custom.clicked.connect(self.open_name_config)
        
        cc_layout.addWidget(rb_custom)
        cc_layout.addWidget(lbl_custom)
        name_l.addWidget(custom_container)
        
        row_layout.addWidget(gb_name)

        # 3. Contact Group
        gb_cont = QGroupBox("Contact")
        gb_cont.setStyleSheet(gb_style)
        cont_l = QVBoxLayout(gb_cont)
        cont_l.setContentsMargins(5, 15, 5, 15) # Equal Top/Bottom
        cont_l.setAlignment(Qt.AlignCenter)
        
        self.contact_group = QButtonGroup(self)
        
        # 3.1 Phone Option
        phone_layout = QHBoxLayout()
        phone_layout.setContentsMargins(0, 0, 0, 0)
        phone_layout.setSpacing(5)
        phone_layout.setAlignment(Qt.AlignCenter)
        
        rb_phone = QRadioButton("Phone")
        rb_phone.setChecked(True)
        self.contact_group.addButton(rb_phone, 0)
        
        self.country_selection = SelectionInput(items=["US", "UK", "VN", "KH", "PH"], width=60, height=22)
        
        phone_layout.addWidget(rb_phone)
        phone_layout.addWidget(self.country_selection)
        cont_l.addLayout(phone_layout)
        
        # 3.2 Email Option
        email_layout = QHBoxLayout()
        email_layout.setContentsMargins(0, 0, 0, 0)
        email_layout.setSpacing(5)
        email_layout.setAlignment(Qt.AlignCenter)
        
        rb_email = QRadioButton("")
        self.contact_group.addButton(rb_email, 1)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("***user@gmail.com")
        self.email_input.setFixedHeight(22)
        self.email_input.setEnabled(False)
        
        email_layout.addWidget(rb_email)
        email_layout.addWidget(self.email_input)
        cont_l.addLayout(email_layout)
        
        self.contact_group.buttonClicked.connect(self.toggle_contact_mode)
        
        row_layout.addWidget(gb_cont)

        # 4. Gender Group
        gb_gen = QGroupBox("Gender")
        gb_gen.setStyleSheet(gb_style)
        gen_l = QVBoxLayout(gb_gen)
        gen_l.setContentsMargins(5, 15, 5, 15) # Equal Top/Bottom
        gen_l.setAlignment(Qt.AlignCenter)
        
        self.gender_group = QButtonGroup(self)
        
        # Random
        rb_rand = QRadioButton("Random")
        rb_rand.setChecked(True)
        self.gender_group.addButton(rb_rand, 0)
        gen_l.addWidget(rb_rand, alignment=Qt.AlignCenter)
        
        # Custom Selection
        custom_gen_layout = QHBoxLayout()
        custom_gen_layout.setContentsMargins(0, 0, 0, 0)
        custom_gen_layout.setSpacing(2)
        custom_gen_layout.setAlignment(Qt.AlignCenter)
        
        rb_custom_gen = QRadioButton("")
        self.gender_group.addButton(rb_custom_gen, 1)
        
        self.gender_selection = SelectionInput(items=["Female", "Male"], width=70, height=22)
        self.gender_selection.setEnabled(False)
        
        custom_gen_layout.addWidget(rb_custom_gen)
        custom_gen_layout.addWidget(self.gender_selection)
        
        gen_l.addLayout(custom_gen_layout)
        
        self.gender_group.buttonClicked.connect(self.toggle_gender_mode)
        
        row_layout.addWidget(gb_gen)

        # 6. Password Group
        gb_pwd = QGroupBox("Password")
        gb_pwd.setStyleSheet(gb_style)
        pwd_l = QVBoxLayout(gb_pwd)
        pwd_l.setContentsMargins(5, 15, 5, 15) # Equal Top/Bottom
        pwd_l.setAlignment(Qt.AlignCenter)
        
        self.password_group = QButtonGroup(self)
        
        # 6.1 Random Option
        rand_layout = QHBoxLayout()
        rand_layout.setContentsMargins(0, 0, 0, 0)
        rand_layout.setSpacing(5)
        rand_layout.setAlignment(Qt.AlignCenter)
        
        rb_rand_pwd = QRadioButton("Random")
        rb_rand_pwd.setChecked(True)
        self.password_group.addButton(rb_rand_pwd, 0)
        
        self.pwd_len_input = QSpinBox()
        self.pwd_len_input.setRange(6, 30)
        self.pwd_len_input.setValue(10)
        self.pwd_len_input.setFixedWidth(40)
        self.pwd_len_input.setToolTip("Password Length")
        
        lbl_sym = QLabel("Symbol:")
        lbl_sym.setStyleSheet("color: #555; font-size: 10px;")
        
        self.pwd_sym_input = QLineEdit()
        self.pwd_sym_input.setPlaceholderText("@#$%")
        self.pwd_sym_input.setFixedWidth(50)
        self.pwd_sym_input.setFixedHeight(22)
        
        rand_layout.addWidget(rb_rand_pwd)
        rand_layout.addWidget(self.pwd_len_input)
        rand_layout.addWidget(lbl_sym)
        rand_layout.addWidget(self.pwd_sym_input)
        pwd_l.addLayout(rand_layout)
        
        # 6.2 Custom Option
        custom_layout = QHBoxLayout()
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.setSpacing(5)
        custom_layout.setAlignment(Qt.AlignCenter)
        
        rb_custom_pwd = QRadioButton("Custom")
        self.password_group.addButton(rb_custom_pwd, 1)
        
        self.pwd_custom_input = QLineEdit()
        self.pwd_custom_input.setPlaceholderText("Enter Password")
        self.pwd_custom_input.setFixedHeight(22)
        self.pwd_custom_input.setEnabled(False)
        
        custom_layout.addWidget(rb_custom_pwd)
        custom_layout.addWidget(self.pwd_custom_input)
        pwd_l.addLayout(custom_layout)
        
        self.password_group.buttonClicked.connect(self.toggle_password_config)
        
        row_layout.addWidget(gb_pwd)
        
        self.layout.addWidget(row_widget)

        # Logs (Inside Scroll Area)
        self.log_area = QTextEdit(); self.log_area.setReadOnly(True); self.log_area.setMinimumHeight(250)
        self.log_area.setStyleSheet("background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; font-family: Consolas, monospace;")
        self.layout.addWidget(self.log_area)
        self.layout.addStretch()

        # Action Buttons (Pinned to Bottom, Outside Scroll Area)
        btn_widget = QWidget()
        btn_widget.setStyleSheet("background-color: white; border-top: 1px solid #e0e0e0;")
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(20, 10, 20, 10)
        
        self.start_btn = QPushButton("Start Reg")
        self.start_btn.setFixedHeight(45)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("background-color: #032EA1; color: white; border-radius: 5px; font-weight: bold; border: none;")
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setFixedHeight(45)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet("background-color: #d32f2f; color: white; border-radius: 5px; font-weight: bold; border: none;")
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_process); self.stop_btn.clicked.connect(self.stop_process)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        
        main_layout.addWidget(btn_widget)
        
        # Enforce cursors on all interactive elements
        self.set_cursors(self)
        self.update_start_state()

    def set_selected_device(self, device_ids):
        if not device_ids:
            self.selected_device_ids = []
        elif isinstance(device_ids, (list, tuple)):
            self.selected_device_ids = list(device_ids)
        else:
            self.selected_device_ids = [device_ids]
        self.update_start_state()

    def set_device_config(self, config):
        self.device_config = config or {}
        self.update_start_state()

    def set_cursors(self, widget):
        for child in widget.findChildren(QWidget):
            if isinstance(child, (QRadioButton, QPushButton, QComboBox, QSpinBox)):
                child.setCursor(Qt.PointingHandCursor)

    def open_name_config(self):
        # Open dialog without selecting radio button automatically
        dlg = NameDialog(self, self.custom_first_names, self.custom_last_names)
        if dlg.exec_() == QDialog.Accepted:
            self.custom_first_names = dlg.first_names
            self.custom_last_names = dlg.last_names
            
            # Log
            f_count = len(self.custom_first_names)
            l_count = len(self.custom_last_names)
            if f_count > 0 or l_count > 0:
                self.append_log(f"Custom Names updated: {f_count} First, {l_count} Last names loaded.")

    def open_proxy_config(self):
        # Only open dialog, DO NOT select the radio button automatically
        dlg = ProxyDialog(self, self.proxy_data)
        if dlg.exec_() == QDialog.Accepted:
            self.proxy_data = dlg.get_proxy_text()
            self.proxy_list = dlg.proxies
            self.append_log(f"Proxies updated: {len(self.proxy_list)} proxies loaded.")

    def toggle_contact_mode(self, button):
        # Index 0: Phone, 1: Email
        is_phone = (self.contact_group.id(button) == 0)
        self.country_selection.setEnabled(is_phone)
        self.email_input.setEnabled(not is_phone)

    def toggle_gender_mode(self, button):
        # Index 1 is Custom
        is_custom = (self.gender_group.id(button) == 1)
        self.gender_selection.setEnabled(is_custom)

    def toggle_vpn_mode(self, button):
        # Index 3 is OpenVPN
        is_vpn = (self.network_group.id(button) == 3)
        self.vpn_mode.setEnabled(is_vpn)

    def toggle_password_config(self, button):
        # Index 0: Random, 1: Custom
        is_random = (self.password_group.id(button) == 0)
        self.pwd_len_input.setEnabled(is_random)
        self.pwd_sym_input.setEnabled(is_random)
        self.pwd_custom_input.setEnabled(not is_random)

    def start_process(self):
        self.append_log("--- Starting Automation ---")
        if not self.selected_device_ids:
            self.append_log("Error: No device selected. Please select a device first.")
            self.update_start_state()
            return

        ok, msg = self.validate_device_config()
        if not ok:
            self.append_log(f"Error: {msg}")
            self.update_start_state()
            return

        ok, msg = self.validate_reg_config()
        if not ok:
            self.append_log(f"Error: {msg}")
            self.update_start_state()
            return
        
        # Check Proxy Logic
        net_id = self.network_group.checkedId()
        # "5G" is 0, "Proxy" is 1
        proxy_arg = "N/A"
        
        if net_id == 1: # Proxy Selected
            if not self.proxy_list:
                self.append_log("Error: Proxy mode selected but no proxies configured.")
                self.append_log("Click the 'Proxy' text to add proxies.")
                return
            proxy_arg = f"{len(self.proxy_list)} Proxies Loaded"

        delay_type = self.device_config.get("delay_type")
        delay_seconds = int(self.device_config.get("delay_seconds") or 0)
        device_delay = delay_seconds if delay_type == "device" else 0
        click_delay = delay_seconds if delay_type == "click" else 0

        devices = list(self.selected_device_ids)
        if len(devices) > 1:
            self.start_multi_device_flow(devices, proxy_arg, device_delay, click_delay)
            return

        self.start_single_device_flow(devices[0], proxy_arg, device_delay, click_delay)

    def stop_process(self):
        if self._multi_stop_event:
            self._multi_stop_event.set()
        if self.bot:
            self.bot.stop_registration()
        self.update_start_state()

    def append_log(self, text):
        self.log_area.append(text)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def on_registration_finished(self):
        if self.multi_run_active:
            return
        if self.current_device_id:
            self.device_status_signal.emit(self.current_device_id, "Idle")
        self.update_start_state()

    def update_start_state(self):
        can_start = bool(self.selected_device_ids) and not (self.bot and self.bot.is_running) and not self.multi_run_active
        self.start_btn.setEnabled(can_start)
        self.stop_btn.setEnabled(bool(self.bot and self.bot.is_running) or self.multi_run_active)

    def validate_device_config(self):
        cfg = self.device_config or {}
        mgmt_mode = cfg.get("mgmt_mode")
        apk_rel = cfg.get("apk_rel_path") or ""
        apk_folder = cfg.get("apk_folder") or ""
        package_name = self.FACEBOOK_PACKAGE

        if mgmt_mode == "reinstall":
            if not apk_rel:
                return False, "APK is required for Re-install."
            apk_path = os.path.join(apk_folder, apk_rel)
            if not os.path.isfile(apk_path):
                return False, "Selected APK not found on disk."

        return True, ""

    def validate_reg_config(self):
        # Name
        if self.name_group.checkedId() == 1:
            if not self.custom_first_names or not self.custom_last_names:
                return False, "Custom name selected but name lists are empty."

        # Contact
        if self.contact_group.checkedId() == 1:
            email = self.email_input.text().strip()
            if not email or "@" not in email or "." not in email:
                return False, "Valid email is required for Email contact mode."

        # Password
        if self.password_group.checkedId() == 1:
            if not self.pwd_custom_input.text().strip():
                return False, "Custom password is required."

        # Proxy
        if self.network_group.checkedId() == 1 and not self.proxy_list:
            return False, "Proxy mode selected but no proxies configured."

        return True, ""

    def apply_device_config_for_device(self, device_id):
        cfg = self.device_config or {}
        mgmt_mode = cfg.get("mgmt_mode")
        apk_rel = cfg.get("apk_rel_path") or ""
        apk_folder = cfg.get("apk_folder") or ""
        package_name = self.FACEBOOK_PACKAGE

        if mgmt_mode == "clear_cache":
            self.log_step(f"Clearing app data on {device_id} ({package_name})...")
            ok, msg = ADBManager.clear_app_data(device_id, package_name)
            if not ok:
                return False, f"Clear cache failed: {msg.strip()}"
            return True, "Clear cache OK"

        if mgmt_mode == "reinstall":
            apk_path = os.path.join(apk_folder, apk_rel)
            if package_name:
                self.log_step(f"Uninstalling {package_name} on {device_id}...")
                ADBManager.uninstall_app(device_id, package_name)
            self.log_step(f"Installing APK on {device_id}: {apk_rel}")
            ok, msg = ADBManager.install_apk(device_id, apk_path)
            if not ok:
                return False, f"Install failed: {msg.strip()}"
            self.log_step(f"Opening {package_name} on {device_id}...")
            ok, msg = ADBManager.launch_app(device_id, package_name)
            if not ok:
                return False, f"Open app failed: {msg.strip()}"
            time.sleep(2)
            ok, msg = self.click_if_button_exists(device_id, self.GET_STARTED_TEXTS)
            if not ok:
                self.log_step(f"Get Start button not found: {msg}")
            return True, "Re-install OK"

        return True, ""

    def click_if_button_exists(self, device_id, texts):
        ok, xml_text = ADBManager.dump_ui_xml(device_id)
        if not ok:
            return False, xml_text
        bounds = ADBManager.find_text_bounds(xml_text, texts)
        if not bounds:
            return False, "Button not found"
        return ADBManager.click_bounds(device_id, bounds)

    def start_multi_device_flow(self, devices, proxy_arg, device_delay, click_delay):
        if self.multi_run_active:
            return
        self.multi_run_active = True
        self._multi_stop_event = threading.Event()
        self.update_start_state()

        thread = threading.Thread(
            target=self._run_multi_device_flow,
            args=(devices, proxy_arg, device_delay, click_delay),
            daemon=True
        )
        thread.start()

    def _run_multi_device_flow(self, devices, proxy_arg, device_delay, click_delay):
        for idx, device_id in enumerate(devices, start=1):
            if self._multi_stop_event.is_set():
                break

            self.current_device_id = device_id
            self.log_step(f"--- Device {idx}/{len(devices)}: {device_id} ---")

            ok, msg = self.apply_device_config_for_device(device_id)
            if not ok:
                self.log_step(f"Error: {msg}")
                break

            done_event = threading.Event()
            self.bot = RegistrationBot(self.log_step, done_event.set)
            self.bot.start_registration(1, proxy_arg, "N/A", device_delay=0, click_delay=click_delay)

            while not done_event.is_set():
                if self._multi_stop_event.is_set():
                    self.bot.stop_registration()
                done_event.wait(0.2)

            self.device_status_signal.emit(device_id, "Idle")

            if idx < len(devices) and device_delay > 0 and not self._multi_stop_event.is_set():
                self.log_step(f"Waiting {device_delay}s before next device...")
                waited = 0
                while waited < device_delay and not self._multi_stop_event.is_set():
                    threading.Event().wait(0.2)
                    waited += 0.2

        self.multi_run_active = False
        self._multi_stop_event = None
        self.signaler.finished_signal.emit()

    def start_single_device_flow(self, device_id, proxy_arg, device_delay, click_delay):
        if self.multi_run_active:
            return
        self.multi_run_active = True
        self._multi_stop_event = threading.Event()
        self.update_start_state()

        thread = threading.Thread(
            target=self._run_single_device_flow,
            args=(device_id, proxy_arg, device_delay, click_delay),
            daemon=True
        )
        thread.start()

    def _run_single_device_flow(self, device_id, proxy_arg, device_delay, click_delay):
        self.current_device_id = device_id

        if self._multi_stop_event.is_set():
            self.multi_run_active = False
            self._multi_stop_event = None
            self.signaler.finished_signal.emit()
            return

        ok, msg = self.apply_device_config_for_device(device_id)
        if not ok:
            self.log_step(f"Error: {msg}")
            self.multi_run_active = False
            self._multi_stop_event = None
            self.signaler.finished_signal.emit()
            return

        done_event = threading.Event()
        self.bot = RegistrationBot(self.log_step, done_event.set)
        self.bot.start_registration(1, proxy_arg, "N/A", device_delay=device_delay, click_delay=click_delay)

        while not done_event.is_set():
            if self._multi_stop_event.is_set():
                self.bot.stop_registration()
            done_event.wait(0.2)

        self.device_status_signal.emit(device_id, "Idle")
        self.multi_run_active = False
        self._multi_stop_event = None
        self.signaler.finished_signal.emit()
    def log_step(self, message):
        self.signaler.log_signal.emit(message)
        if self.current_device_id:
            self.device_status_signal.emit(self.current_device_id, message)
