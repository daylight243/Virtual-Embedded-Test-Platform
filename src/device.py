class Device:
    
    def __init__(self):

        self.device_name = "Power Controller"

        self.device_id = "PWR-001"

        self.status = "READY"

    def display_info(self):

        print("=" * 40)
        print("Virtual Device Created")
        print()
        print(f"Device Name: {self.device_name}")
        print(f"Device ID: {self.device_id}")
        print(f"Status: {self.status}")
        print("=" * 40)