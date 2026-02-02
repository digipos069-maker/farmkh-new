
import time

class FacebookBot:
    def __init__(self, account_data):
        self.account_data = account_data
        self.is_running = False

    def login(self):
        print(f"Logging into {self.account_data.get('username')}...")
        time.sleep(2)
        return True

    def upload_video(self, video_path, caption):
        if not self.is_running:
            return "Bot is not running"
        print(f"Uploading {video_path} with caption: {caption}")
        time.sleep(5)
        return "Upload Successful"

    def stop(self):
        self.is_running = False
        print("Bot stopped.")
