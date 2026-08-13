from device import Device

def main():

    print("Virtual Embedded Test Platform")
    print()

    device = Device()

    print("1.) Device created")
    device.display_info()

    print("2.) Starting Device")
    device.start()  
    device.display_info()

    print("3.) Running Device")
    device.run()
    device.display_info()

    print("4.) Shutting down Device")
    device.shutdown()
    device.display_info()

    print("5.) Turning off Device")
    device.turn_off()
    device.display_info()  

if __name__ == "__main__":

    main()