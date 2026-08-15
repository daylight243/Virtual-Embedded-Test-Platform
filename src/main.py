from device import Device

def main():

    print("Virtual Embedded Test Platform")
    print()

    device = Device()

    device.start()
    device.run()

    print("Initial Running Conditions")
    device.display_info()

    print("Updated Measurements")
    for sample_number in range(1, 6):
        print(f"Sample {sample_number}")
        device.update_measurements()
        device.display_info()

if __name__ == "__main__":

    main()