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

    print("Updated Measurements")
    device.reset_sensor_model
    for sample_number in range(1, 4):
        print(f"Sample {sample_number}")
        device.update_measurements()
        device.check_faults()
        device.display_info()

    print("Freezing Temperature Sensors")

    device.freeze_temperature_sensor()
    for sample_number in range(4, 8):
            print(f"Sample {sample_number}")
            device.update_measurements()
            device.check_faults()
            device.display_info()

if __name__ == "__main__":

    main()