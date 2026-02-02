
import time
import threading

class RegistrationBot:
    def __init__(self, log_callback, done_callback=None):
        self.log_callback = log_callback
        self.done_callback = done_callback
        self.is_running = False
        self._thread = None

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def start_registration(self, count, proxy_file, sms_key, device_delay=0, click_delay=0):
        if self.is_running:
            self.log("Registration already in progress...")
            return

        self.is_running = True
        self._thread = threading.Thread(target=self._run_process, args=(count, proxy_file, sms_key, device_delay, click_delay))
        self._thread.start()

    def stop_registration(self):
        self.is_running = False
        self.log("Stopping registration process...")

    def _run_process(self, count, proxy_file, sms_key, device_delay, click_delay):
        self.log(f"Starting registration for {count} accounts...")
        self.log(f"Using proxy file: {proxy_file}")
        if device_delay:
            self.log(f"Device delay: {device_delay}s")
            time.sleep(device_delay)
        
        for i in range(1, count + 1):
            if not self.is_running:
                break
            
            self.log(f"[{i}/{count}] Initializing browser...")
            time.sleep(1) # Simulate work
            if click_delay: time.sleep(click_delay)
            
            self.log(f"[{i}/{count}] Solving captcha...")
            time.sleep(2) # Simulate work
            if click_delay: time.sleep(click_delay)
            
            self.log(f"[{i}/{count}] Verifying email/phone...")
            time.sleep(1) # Simulate work
            if click_delay: time.sleep(click_delay)
            
            self.log(f"[{i}/{count}] Account created successfully!")
            time.sleep(1)
            
        self.is_running = False
        self.log("Registration batch completed.")
        if self.done_callback:
            self.done_callback()
