class Device:

    def __init__(self):
        self.device_name = "Power Controller"
        
        self.device_id = "PWR-001"
        
        self.state = "OFF"
        
        self.voltage = 0.0 
        
        self.current = 0.0 
        
        self.temperature = 25.0
        

    def start(self):
             self.state = "STARTUP" 
             self.voltage = 12.0 
             self.current = 0.8 
             self.temperature = 26.0

    def run(self): 
            self.state = "RUNNING"
            self.voltage = 12.0 
            self.current = 1.5 
            self.temperature = 32.0

    def shutdown(self): 
            self.state = "SHUTDOWN" 
            self.voltage = 12.0 
            self.current = 0.4
            self.temperature = 29.0

    def turn_off(self): 
            self.state = "OFF" 
            self.voltage = 0.0 
            self.current = 0.0
            self.temperature = 25.0

        
    def display_info(self):
        power = self.voltage * self.current

        print("=" * 40)
        print("Virtual Device Created")
        print()

        print(f"Device Name: {self.device_name}")
        print(f"Device ID: {self.device_id}")
        print(f"State: {self.state}")

        print()
        print("---Measurements---")
        print()

        print(f"Voltage: {self.voltage} V")
        print(f"Current: {self.current} A")
        print(f"Power: {power} W")
        print(f"Temperature: {self.temperature} °C")
        print("=" * 40)