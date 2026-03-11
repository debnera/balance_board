import asyncio
from bleak import BleakClient

# Define the handler for receiving notifications
def notification_handler(sender, data):
    # print(f"Received data from {sender}: {int.from_bytes(data, 'little')}")
    data_str = bytes(data).decode(encoding='utf-8')
    yaw,pitch,roll = data_str.split(',')
    print(f"yaw: {yaw}, pitch: {pitch}, roll: {roll}")

# Define the main function to listen for notifications
async def listen_for_notifications(address, characteristic_uuid):
    async with BleakClient(address) as client:
        # Start the notification listener
        await client.start_notify(characteristic_uuid, notification_handler)
        print("Listening for notifications...")

        # Keep the program running
        await asyncio.sleep(50)  # Run for 30 seconds, adjust as needed

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

#%%

#%%
