class Device:

    def __init__(self):

        self.device_name = "Power Controller"

        self.device_id = "PWR-001"

        self.status = "READY"

        self.voltage = 12.0 

        self.current = 1.5 

        self.temperature = 25.0

    def display_info(self):
        power = self.voltage * self.current

        print("=" * 40)
        print("Virtual Device Created")
        print()

        print(f"Device Name: {self.device_name}")
        print(f"Device ID: {self.device_id}")
        print(f"Status: {self.status}")

        print()
        print("---Measurements---")
        print()

        print(f"Voltage: {self.voltage} V")
        print(f"Current: {self.current} A")
        print(f"Power: {power} W")
        print(f"Temperature: {self.temperature} °C")
        print("=" * 40)