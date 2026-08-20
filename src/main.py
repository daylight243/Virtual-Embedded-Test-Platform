import random
from device import Device

def main():
    random.seed(42)  # Set a fixed seed for reproducibility
    print("Virtual Embedded Test Platform")
    print()

    device = Device()

    device.start()
    device.run()

    
    device.update_measurements()

    print("HEALTHY DEVICE")
    print() 

    device.display_info() 
    device.display_digital_inputs()

    device.voltage = 9.99
    device.request_start()
    device.display_fpga_inputs()

    
    
    
if __name__ == "__main__":

    main()