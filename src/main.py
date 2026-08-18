import random
from device import Device

def main():
    random.seed(42)  # Set a fixed seed for reproducibility
    print("Virtual Embedded Test Platform")
    print()

    device = Device()

    device.start()
    device.run()

    device.enable_intermittent_fault()  # Enable intermittent fault 
    for sample in range(1, 10):
        device.update_measurements()
        device.check_faults()
        fault_active = device.intermittent_status()
        print(f"Sample {sample}:")
        print(f"Voltage: {device.voltage:.2f} V")
        print(f"Intermittent Fault Active: {fault_active}")
        print(f"Fault Code: {device.faultcode}")
    

if __name__ == "__main__":

    main()