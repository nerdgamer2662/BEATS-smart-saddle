import tkinter as tk
import threading
import simplepyble

isRecording = False

tag_characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
control_characteristic_uuid = (
    "d1e3f1a2-4c5b-4f8e-9c6b-7f3e1a2b3c4d"  # This is for toggling recording state
)
service_uuid = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"


def initBLE():
    adapters = simplepyble.Adapter.get_adapters()
    if len(adapters) == 0:
        print("No adapters found")

    # Query the user to pick an adapter
    print("Please select an adapter:")
    for i, adapter in enumerate(adapters):
        print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

    choice = int(input("Enter choice: "))
    adapter = adapters[choice]

    print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

    adapter.set_callback_on_scan_start(lambda: print("Scan started."))
    adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
    adapter.set_callback_on_scan_found(
        lambda peripheral: print(
            f"Found {peripheral.identifier()} [{peripheral.address()}] ({peripheral.is_connectable()})"
        )
    )

    # Scan for 5 seconds
    adapter.scan_for(15000)
    peripherals = adapter.scan_get_results()

    # Query the user to pick a peripheral
    # print("Please select a peripheral:")
    for i, peripheral in enumerate(peripherals):
        print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")
        services = peripheral.services()
        for service in services:
            print(f"    Service UUID: {service.uuid()}")
            print(f"    Service data: {service.data()}")

    print("Connecting to Esp32...")
    choice = int(input("Enter choice: "))
    choice = i
    peripheral = peripherals[choice]

    print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
    peripheral.connect()

    # print("Successfully connected, listing services...")
    # services = peripheral.services()
    # service_characteristic_pair = []
    # for service in services:
    #     for characteristic in service.characteristics():
    #         service_characteristic_pair.append((service.uuid(), characteristic.uuid()))

    # Query the user to pick a service/characteristic pair
    # print("Please select a service/characteristic pair:")
    # for i, (service_uuid, characteristic) in enumerate(service_characteristic_pair):
    #     if characteristic == "d1e3f1a2-4c5b-4f8e-9c6b-7f3e1a2b3c4d"
    # print(f"{i}: {service_uuid} {characteristic}")
    
    print("Successfully connected")

    # choice = int(input("Enter choice: "))
    # choice = 0
    # service_uuid, characteristic_uuid = service_characteristic_pair[choice]
    return peripheral


# create a thread to read from BLE and send to queue
def read_from_ble(service_uuid, characteristic_uuid, peripheral):
    old_contents = None
    while True:
        contents = peripheral.read(service_uuid, characteristic_uuid)
        if contents != old_contents:
            old_contents = contents
            # Decode the contents assuming it's a string
            decoded_contents = contents.decode("utf-8", errors="ignore").strip()
            parsed_data = decoded_contents.split(",")
            tag_EPC = parsed_data[0]
            print(f"Parsed data: {parsed_data}")

        else:
            # Sleep for a short duration to avoid busy waiting
            threading.Event().wait(0.1)

if __name__ == "__main__":
    # Initialize BLE and start reading from it
    peripheral = initBLE()

    ble_thread = threading.Thread(
        target=read_from_ble,
        args=(service_uuid, tag_characteristic_uuid, peripheral),
        daemon=True,
    )

    ble_thread.start()