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

        self.voltage_drift_per_sample = 0.005
        self.current_drift_per_sample = 0.002
        self.temperature_drift_per_sample = 0.5  

        self.voltage_sensor_frozen = False
        self.current_sensor_frozen = False
        self.temperature_sensor_frozen = False

        self.voltage_valid = True
        self.current_valid = True
        self.temperature_valid = True

        self.sample_count = 0   
        
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

        if not self.voltage_valid:
            self.alarm = True
            self.faultcode = "INVALID_VOLTAGE"
            return

        if not self.current_valid:
            self.alarm = True
            self.faultcode = "INVALID_CURRENT"
            return

        if not self.temperature_valid:
            self.alarm = True
            self.faultcode = "INVALID_TEMPERATURE"
            return

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
    def reset_sensor_model(self):
        self.sample_count = 0

    def freeze_voltage_sensor(self):
        self.voltage_sensor_frozen = True

    def freeze_current_sensor(self):
        self.current_sensor_frozen = True

    def freeze_temperature_sensor(self):
        self.temperature_sensor_frozen = True

    def clear_sensor_freeze(self):
        self.voltage_sensor_frozen = False
        self.current_sensor_frozen = False
        self.temperature_sensor_frozen = False

    def invalidate_voltage_sensor(self):
        self.voltage = None
        self.voltage_valid = False

    def invalidate_current_sensor(self):
        self.current = None
        self.current_valid = False

    def invalidate_temperature_sensor(self):
        self.temperature = None
        self.temperature_valid = False

    def clear_invalid_measurements(self):
        self.voltage_valid = True
        self.current_valid = True
        self.temperature_valid = True

        if self.state == "RUNNING":
            self.voltage = self.nominal_voltage 
            self.current = self.nominal_current 
            self.temperature = self.nominal_temperature 

    def update_measurements(self):

        if self.state != "RUNNING":
            return

        self.sample_count += 1

        voltage_noise = random.gauss(0, self.voltage_noise_std)
        current_noise = random.gauss(0, self.current_noise_std)
        temperature_noise = random.gauss(0, self.temperature_noise_std)
       
        voltage_drift = (self.voltage_drift_per_sample * self.sample_count)
        current_drift = (self.current_drift_per_sample * self.sample_count)
        temperature_drift = (self.temperature_drift_per_sample * self.sample_count)

        if (self.voltage_valid and not self.voltage_sensor_frozen):
            self.voltage = (self.nominal_voltage + self.voltage_bias + voltage_noise + voltage_drift)

        if (self.current_valid and not self.current_sensor_frozen):
            self.current = (self.nominal_current + self.current_bias + current_noise + current_drift)

        if (self.temperature_valid and not self.temperature_sensor_frozen):
            self.temperature = (self.nominal_temperature + self.temperature_bias + 
                                temperature_noise + temperature_drift)

    def display_info(self):

        if self.voltage_valid and self.current_valid:
            power = self.voltage * self.current
        else:
            power = None

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

        if self.voltage_valid:
             voltage_text = f"{self.voltage:.2f} V"
        else:
             voltage_text = "INVALID"
        if self.current_valid:
             current_text = f"{self.current:.2f} A" 
        else:
             current_text = "INVALID"
        if self.temperature_valid:
             temperature_text = f"{self.temperature:.2f} °C"    
        else:
             temperature_text = "INVALID"
        if power is not None:
             power_text = f"{power:.2f} W" 
        else:
             power_text = "INVALID"

        print(f"Sample Count: {self.sample_count}")
        print(f"Voltage: {voltage_text}")
        print(f"Current: {current_text}")
        print(f"Power: {power_text}")
        print(f"Temperature: {temperature_text}")
        print(f"Alarm: {self.alarm}")
        print(f"Fault Code: {self.faultcode}")   

        print()
        print("---Sensor Validity---")
        print()

        print(f"Voltage Valid: {self.voltage_valid}")   
        print(f"Current Valid: {self.current_valid}")
        print(f"Temperature Valid: {self.temperature_valid}")

        print("=" * 40)

    