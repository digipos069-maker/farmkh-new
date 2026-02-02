
import subprocess

class ADBManager:
    @staticmethod
    def _run_adb(args):
        try:
            result = subprocess.run(['adb'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_connected_devices():
        """
        Executes 'adb devices' and returns a list of dictionaries:
        [{'id': 'emulator-5554', 'status': 'device'}, ...]
        Filters out offline devices and deduplicates 127.0.0.1:5555 vs emulator-5554.
        """
        try:
            # Run adb command
            ok, output = ADBManager._run_adb(['devices'])
            output = output.strip()
            
            lines = output.split('\n')
            
            raw_devices = []
            claimed_ports = set()
            
            # First pass: Collect all valid devices and identify "emulator-XXXX" ports
            for line in lines[1:]:
                line = line.strip()
                if not line: continue
                
                parts = line.split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    raw_status = parts[1]
                    
                    if raw_status == 'offline':
                        continue
                        
                    # logic to identify emulator ports
                    if device_id.startswith("emulator-"):
                        try:
                            # emulator-5554 typically means ADB is on 5555
                            console_port = int(device_id.split("-")[1])
                            adb_port = console_port + 1
                            claimed_ports.add(adb_port)
                        except ValueError:
                            pass
                    
                    raw_devices.append({'id': device_id, 'raw_status': raw_status})

            devices = []
            for dev in raw_devices:
                device_id = dev['id']
                raw_status = dev['raw_status']
                
                # Deduplication: specific for localhost IPs
                if device_id.startswith("127.0.0.1:"):
                    try:
                        port = int(device_id.split(":")[1])
                        if port in claimed_ports:
                            continue # Skip this duplicate
                    except ValueError:
                        pass

                # Map raw status to user-friendly status
                status = "Online" if raw_status == "device" else raw_status.capitalize()
                
                # Basic name mapping
                name = "Emulator" if "emulator" in device_id or "127.0.0.1" in device_id else "Real Device"
                
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

    @staticmethod
    def connect_device(address):
        """
        Executes 'adb connect <address>'
        """
        ADBManager._run_adb(['connect', address])

    @staticmethod
    def attempt_emulator_connection():
        """
        Attempts to connect to common emulator ports (MuMu, etc.)
        """
        common_ports = [
            "127.0.0.1:5555",   # Default ADB / LDPlayer
            "127.0.0.1:5557",   # MuMu / LDPlayer Alternative
            "127.0.0.1:7555",   # MuMu 6/X
            "127.0.0.1:16384",  # MuMu 12
            "127.0.0.1:16416",  # MuMu 12 (Alternative)
        ]
        for addr in common_ports:
            ADBManager.connect_device(addr)

    @staticmethod
    def install_apk(device_id, apk_path):
        """Installs an APK on the specified device."""
        return ADBManager._run_adb(['-s', device_id, 'install', '-r', apk_path])

    @staticmethod
    def uninstall_app(device_id, package_name):
        """Uninstalls an app from the specified device."""
        return ADBManager._run_adb(['-s', device_id, 'uninstall', package_name])

    @staticmethod
    def clear_app_data(device_id, package_name):
        """Clears cache and data for an app."""
        return ADBManager._run_adb(['-s', device_id, 'shell', 'pm', 'clear', package_name])

    @staticmethod
    def launch_app(device_id, package_name):
        """Launches the app on the specified device."""
        return ADBManager._run_adb(['-s', device_id, 'shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'])
