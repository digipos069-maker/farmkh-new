
import subprocess

class ADBManager:
    @staticmethod
    def get_connected_devices():
        """
        Executes 'adb devices' and returns a list of dictionaries:
        [{'id': 'emulator-5554', 'status': 'device'}, ...]
        """
        try:
            # Run adb command
            result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            output = result.stdout.strip()
            
            devices = []
            lines = output.split('\n')
            
            # Skip the first line ("List of devices attached")
            for line in lines[1:]:
                line = line.strip()
                if not line: continue
                
                parts = line.split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    raw_status = parts[1]
                    
                    # Map raw status to user-friendly status
                    status = "Online" if raw_status == "device" else raw_status.capitalize()
                    
                    # Basic name mapping
                    name = "Emulator" if "emulator" in device_id else "Real Device"
                    
                    devices.append({
                        'id': device_id,
                        'name': name,
                        'status': status
                    })
            
            return devices

        except FileNotFoundError:
            return [{'id': 'Error', 'name': 'ADB Not Found', 'status': 'Error'}]
        except Exception as e:
            return [{'id': 'Error', 'name': str(e), 'status': 'Error'}]
