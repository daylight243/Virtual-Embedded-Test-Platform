from device import Device

def main():

    print("Virtual Embedded Test Platform")
    print()

    device = Device()

    device.start()
    device.run()

    print("Normal Operation")
    device.check_faults()
    device.display_info()

    print()
    print("Injecting Undervoltage Fault")
    print()

    device.voltage = 9.0
    device.check_faults()
    device.display_info()

    print("Test 2- Injecting Overvoltage Fault")
    device.voltage = 12.0
    device.check_faults()
    device.display_info()   

    print("Test 3- Injecting Overcurrent Fault")
    device.voltage = 12.0
    device.current = 4.0
    device.check_faults()
    device.display_info()

    print("Test 4- Injecting Overheat Fault")
    device.current = 1.5
    device.temperature = 80.0
    device.check_faults()   
    device.display_info()    

    print("Test 5- Returning to Normal Operation")
    device.temperature = 32.0
    device.check_faults()
    device.display_info()

if __name__ == "__main__":

    main()