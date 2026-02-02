
import time
import threading

class RegistrationBot:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.is_running = False
        self._thread = None

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def start_registration(self, count, proxy_file, sms_key):
        if self.is_running:
            self.log("Registration already in progress...")
            return

        self.is_running = True
        self._thread = threading.Thread(target=self._run_process, args=(count, proxy_file, sms_key))
        self._thread.start()

    def stop_registration(self):
        self.is_running = False
        self.log("Stopping registration process...")

    def _run_process(self, count, proxy_file, sms_key):
        self.log(f"Starting registration for {count} accounts...")
        self.log(f"Using proxy file: {proxy_file}")
        
        for i in range(1, count + 1):
            if not self.is_running:
                break
            
            self.log(f"[{i}/{count}] Initializing browser...")
            time.sleep(1) # Simulate work
            
            self.log(f"[{i}/{count}] Solving captcha...")
            time.sleep(2) # Simulate work
            
            self.log(f"[{i}/{count}] Verifying email/phone...")
            time.sleep(1) # Simulate work
            
            self.log(f"[{i}/{count}] Account created successfully!")
            time.sleep(1)
            
        self.is_running = False
        self.log("Registration batch completed.")
