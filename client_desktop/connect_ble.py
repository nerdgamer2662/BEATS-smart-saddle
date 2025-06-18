from tkinter import *
from tkinter import ttk

import threading
import simplepyble
import time

reading = False

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
    adapter.scan_for(5000)
    peripherals = adapter.scan_get_results()

    # Query the user to pick a peripheral
    # print("Please select a peripheral:")
    for i, peripheral in enumerate(peripherals):
        print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")
        services = peripheral.services()
        for service in services:
            print(f"    Service UUID: {service.uuid()}")
            print(f"    Service data: {service.data()}")

    choice = int(input("Enter choice: "))
    peripheral = peripherals[choice]

    print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
    peripheral.connect()

    print("Successfully connected, listing services...")
    services = peripheral.services()
    service_characteristic_pair = []
    for service in services:
        for characteristic in service.characteristics():
            service_characteristic_pair.append((service.uuid(), characteristic.uuid()))

    # Query the user to pick a service/characteristic pair
    print("Please select service/characteristic pairs:")
    for i, (service_uuid, characteristic) in enumerate(service_characteristic_pair):
        print(f"{i}: {service_uuid} {characteristic}")

    pairs = []

    try:
        while True:
            choice = int(input("Enter choice: "))
            pairs.append(service_characteristic_pair[choice])
    except Exception as e:
        print(e)

    return peripheral, pairs


# create a thread to read from BLE and send to queue
def read_from_ble(pairs, peripheral, file_name):
    print("Started reading")
    old_contents = []
    contents = []
    start_time = time.time()

    for p in pairs:
        contents.append("")
        old_contents.append("")

    print(reading)

    with open(file_name + ".csv", "a") as f:
        while reading:
            no_updates = True
            line = str(time.time() - start_time)
            for i, p in enumerate(pairs):
                line += ","
                service_uuid, characteristic_uuid = p
                contents[i] = peripheral.read(service_uuid, characteristic_uuid)
                # print(contents[i])
                if contents[i] != old_contents[i]:
                    no_updates = False
                old_contents[i] = contents[i]
                # Decode the contents assuming it's a string
                decoded_contents = contents[i].decode("utf-8", errors="ignore").strip()
                line += decoded_contents

                first = False

            if no_updates:
                threading.Event().wait(0.1)
            else:
                print(line)
                f.write(line)
                f.write("\n")

    print("Done reading")

def spawn_reader(file_name):
    global reading
    reading = True

    ble_thread = threading.Thread(
        target=read_from_ble,
        args=(pairs, peripheral, file_name),
        daemon=False,
    )

    ble_thread.start()

def end_reader():
    global reading
    reading = False
    print("Reader concluded, file should be stable")

def spawn_ui():
    root = Tk()
    root.title("BLE CSVer")

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    file_name = StringVar()
    file_name_entry = ttk.Entry(mainframe, width=7, textvariable=file_name)
    file_name_entry.grid(column=2, row=1, sticky=(W, E))

    ttk.Button(mainframe, text="Start Read", command= lambda: spawn_reader(file_name.get())).grid(column=1, row=3, sticky=W)
    ttk.Button(mainframe, text="Stop Read", command=end_reader).grid(column=3, row=3, sticky=W)

    ttk.Label(mainframe, text=".csv").grid(column=3, row=1, sticky=W)

    for child in mainframe.winfo_children(): 
        child.grid_configure(padx=5, pady=5)

    file_name_entry.focus()
    root.bind("<Return>", spawn_reader)
    return root

if __name__ == "__main__":
    # Initialize BLE and start reading from it
    peripheral, pairs = initBLE()

    root = spawn_ui()

    print("Init complete! See UI for buttons")
    root.mainloop()