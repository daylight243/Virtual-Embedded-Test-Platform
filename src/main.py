import random
from device import Device

def main():
    random.seed(42)  # Set a fixed seed for reproducibility
    print("Virtual Embedded Test Platform")
    print()

    device = Device()

    device.start()
    device.run()

    print("Initial Running Conditions")
    device.display_info()

    print("Health Device")
    device.update_measurements()
    device.check_faults()
    device.display_info()

    print("Invalidating Temperature Sensors")

    device.invalidate_temperature_sensor()
    device.check_faults()
    device.display_info()

    device.invalidate_current_sensor()
    device.check_faults()                       
    device.display_info()

    device.invalidate_voltage_sensor()
    device.check_faults()           
    device.display_info()

if __name__ == "__main__":

    main()