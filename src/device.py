import random
class Device:

    def __init__(self):
        self.device_name = "Power Controller"
        
        self.device_id = "PWR-001"
        
        self.state = "OFF"

        self.nominal_voltage = 12.0
        self.nominal_current = 1.5
        self.nominal_temperature = 32.0

        self.voltage_noise_std = 0.02
        self.current_noise_std = 0.02
        self.temperature_noise_std = 0.20

        self.voltage_bias = 0.04
        self.current_bias = 0.01
        self.temperature_bias = 0.3
        
        self.voltage = 0.0 
        self.current = 0.0 
        self.temperature = 25.0

        self.alarm = False
        self.faultcode = "NONE"
        

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

    def check_faults(self):

        self.alarm = False
        self.faultcode = "NONE"

        if self.temperature > 70.0:
            self.alarm = True
            self.faultcode = "OVERHEAT"
            return
        if self.voltage < 10.0:
            self.alarm = True
            self.faultcode = "UNDERVOLTAGE"
            return
        if self.voltage > 14.0:
            self.alarm = True
            self.faultcode = "OVERVOLTAGE"
            return
        if self.current > 3.0:
            self.alarm = True
            self.faultcode = "OVERCURRENT"
            return

    def update_measurements(self):
        voltage_noise = random.gauss(0, self.voltage_noise_std)
        current_noise = random.gauss(0, self.current_noise_std)
        temperature_noise = random.gauss(0, self.temperature_noise_std)

        self.voltage = self.nominal_voltage + self.voltage_bias + voltage_noise
        self.current = self.nominal_current + self.current_bias + current_noise
        self.temperature = self.nominal_temperature + self.temperature_bias + temperature_noise

    def display_info(self):
        power = self.voltage * self.current
        self.alarm = "on" if self.alarm else "off"

        print("=" * 40)
        print("Virtual Device Created")
        print()

        print(f"Device Name: {self.device_name}")
        print(f"Device ID: {self.device_id}")
        print(f"State: {self.state}")

        print()
        print("---Measurements---")
        print()

        print(f"Voltage: {self.voltage:.2f} V")
        print(f"Current: {self.current:.2f} A")
        print(f"Power: {power:.2f} W")
        print(f"Temperature: {self.temperature:.2f} °C")
        print(f"Alarm: {self.alarm}")
        print(f"Fault Code: {self.faultcode}")
        print("=" * 40)

    