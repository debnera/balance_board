import asyncio
from bleak import BleakScanner

async def run():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)

for i in range(10):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
#%%

#%%
import asyncio
from bleak import BleakClient

address = "60:1D:AB:24:DB:46"
MODEL_NBR_UUID = "00002a00-0000-1000-8000-00805f9b34fb"
MODEL_NBR_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"

async def main(address):
    client = BleakClient(address)
    try:
        await client.connect()
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

asyncio.run(main(address))

#%%
import asyncio
from bleak import BleakScanner, BleakClient

async def discover_and_read_services(address):
    async with BleakClient(address) as client:
        services = await client.get_services()
        for service in services:
            print(f"Service: {service}")
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        print(f"Characteristic {char.uuid}: {value} -- {bytes(value)}")
                    except Exception as e:
                        print(f"Could not read characteristic {char.uuid}: {e}")

# Replace 'DEVICE_ADDRESS' with the address of your BLE device
address = '60:1D:AB:24:DB:46'

loop = asyncio.get_event_loop()
loop.run_until_complete(discover_and_read_services(address))

#%%
import asyncio
from bleak import BleakClient

# Define the handler for receiving notifications
def notification_handler(sender, data):
    # print(f"Received data from {sender}: {int.from_bytes(data, 'little')}")
    print(f"Received data from {sender}: {bytes(data).decode(encoding='utf-8')}")

# Define the main function to listen for notifications
async def listen_for_notifications(address, characteristic_uuid):
    async with BleakClient(address) as client:
        # Start the notification listener
        await client.start_notify(characteristic_uuid, notification_handler)
        print("Listening for notifications...")

        # Keep the program running
        await asyncio.sleep(5)  # Run for 30 seconds, adjust as needed

        # Stop the notification listener
        await client.stop_notify(characteristic_uuid)
        print("Stopped listening for notifications.")

# Replace 'DEVICE_ADDRESS' with the address of your BLE device
# Replace 'CHARACTERISTIC_UUID' with the UUID of the characteristic you want to listen to
address = '60:1D:AB:24:DB:46'
characteristic_uuid = '19B10001-E8F2-537E-4F6C-D104768A1214'

# Start the event loop and listen for notifications
loop = asyncio.get_event_loop()
loop.run_until_complete(listen_for_notifications(address, characteristic_uuid))
#%%
