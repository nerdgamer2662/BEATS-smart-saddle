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
def read_from_ble(service_uuid, characteristic_uuid, peripheral, grid):
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
            # find the first box in the grid that has the same EPC value
            for i in range(len(grid)):
                for j in range(len(grid[i])):
                    arf_tag = grid[i][j]
                    if arf_tag.EPC == "":
                        pass
                    elif arf_tag.EPC == tag_EPC:
                        arf_tag.frame.config(bg="red")
                    elif arf_tag.EPC != tag_EPC and arf_tag.frame.cget("bg") == "red":
                        # Reset the color if it was previously red and no longer matches
                        arf_tag.frame.config(bg="lightgreen")

        else:
            # Sleep for a short duration to avoid busy waiting
            threading.Event().wait(0.1)


class ArfTag:
    def __init__(self, frame):
        self.EPC = ""
        self.frame = frame


def create_grid_of_boxes(parent, rows, cols):
    """Creates a grid of boxes (frames) within the given parent widget."""
    grid = []
    for i in range(rows):
        row = []
        for j in range(cols):
            frame = tk.Frame(
                parent, relief=tk.SOLID, borderwidth=1, width=50, height=50
            )
            frame.grid(row=i, column=j)
            row.append(ArfTag(frame))
        grid.append(row)
    return grid


class ArfGUI:
    def __init__(self, root, peripheral):
        self.root = root
        self.peripheral = peripheral
        rows = 10
        cols = 10
        self.grid = create_grid_of_boxes(self.root, rows, cols)
        # self.toggleRecordingButton = tk.Button(
        #     root, text="Toggle Recording", command=toggleDeviceRecording
        # )
        # self.toggleRecordingButton.grid(
        #     row=rows, columnspan=cols, pady=10
        # )  # Place the button below the grid
        # self.newTrialButton = tk.Button(
        #     root, text="Create New Trial", command=startNewTrial
        # )
        # self.newTrialButton.grid(
        #     row=rows + 1, columnspan=cols, pady=10
        # )  # Place the button below the grid

        self.toggleReading = False

        # set the EPC of tags here
        self.grid[0][8].EPC = "0x111111222222333333444444"
        self.grid[0][0].EPC = "0x111133b2ddd9014000000000"
        self.grid[1][2].EPC = "0x300833b2ddd9014000000000"
        
        # loop through each box in the grid and set the background color based on the EPC value
        for i in range(rows):
            for j in range(cols):
                arf_tag = self.grid[i][j]
                if arf_tag.EPC:
                    arf_tag.frame.config(bg="lightgreen")
                else:
                    arf_tag.frame.config(bg="white")

    def toggleDeviceRecording(self):
        # This function can be implemented to toggle the recording state of the device
        print("Toggling device recording state...")  # Placeholder action
        self.toggleReading = int(not self.toggleReading)
        self.peripheral.write_request(
            service_uuid, control_characteristic_uuid, str.encode(self.toggleReading)
        )

    def startNewTrial(self):
        # This function can be implemented to reset the grid or start a new trial
        print("Starting a new trial...")  # Placeholder action
        self.peripheral.write_request(
            service_uuid, control_characteristic_uuid, str.encode("2")
        )

        # Reset all boxes to their initial state
        for row in self.grid:
            for arf_tag in row:
                arf_tag.frame.config(bg="white")


if __name__ == "__main__":
    # Initialize BLE and start reading from it
    peripheral = initBLE()
    root = tk.Tk()
    root.title("Arf-BLE GUI")
    arfGUI = ArfGUI(root, peripheral)  # Create the GUI with the grid of boxes

    ble_thread = threading.Thread(
        target=read_from_ble,
        args=(service_uuid, tag_characteristic_uuid, peripheral, arfGUI.grid),
        daemon=True,
    )
    ble_thread.start()
    root.mainloop()
