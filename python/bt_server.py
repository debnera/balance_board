#%%

import asyncio
import threading
import time
from scipy.spatial.transform import Rotation as R

from bleak import BleakClient
class BtServer():

    def __init__(self, verbose):
        self.verbose = verbose
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.update_timestamp = 0
        self.ready = False  # Will be true when first reading is received
        # Replace 'DEVICE_ADDRESS' with the address of your BLE device
        # Replace 'CHARACTERISTIC_UUID' with the UUID of the characteristic you want to listen to
        self.address = '60:1D:AB:24:DB:46'
        self.characteristic_uuid = '19B10001-E8F2-537E-4F6C-D104768A1214'
        self.characteristic_uuid_pitch = '19B10001-E8F2-537E-4F6C-D104768A1215'
        self.characteristic_uuid_roll = '19B10001-E8F2-537E-4F6C-D104768A1216'
        self.thread = threading.Thread(target=self.start_loop, daemon=True)
        self.loop = None
        self.stop_event = threading.Event()
        self.rot = R.from_euler('xyz', [self.yaw, self.pitch, self.roll], degrees=True)

    def is_ready(self):
        return self.ready

    def form_rotation_matrix(self):
        self.rot = R.from_euler('xyz', [self.yaw, self.pitch, self.roll], degrees=True)
        # self.rot = R.from_euler('xyz', [0, 0, 0], degrees=True)

    def get_orientation(self):
        angles = R.from_euler('xyz', [self.yaw, self.pitch, self.roll], degrees=True)
        angles = angles * self.rot.inv()
        # return self.yaw, self.pitch, self.roll
        # print(angles.as_euler("xyz", degrees=True))
        # print(angles.as_euler("xyz", degrees=True), self.rot.as_euler("xyz", degrees=True))
        return angles.as_euler("xyz", degrees=True)

    def start_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        # self.loop.run_forever()
        # self.loop.run_until_complete(self.listen_for_notifications(self.address, self.characteristic_uuid_roll))
        self.loop.run_until_complete(self.listen_for_notifications(self.address, self.characteristic_uuid))

    # Define the handler for receiving notifications
    def notification_handler(self, sender, data):
        """ NOTE: It would be more optimal to use one byte for each angle, instead of strings """
        # print(f"Received data from {sender}: {int.from_bytes(data, 'little')}")
        try:
            data_str = bytes(data).decode(encoding='utf-8')
            yaw,pitch,roll = data_str.split(',')

            self.yaw = float(yaw)
            # self.yaw = 0
            self.pitch = float(pitch)
            self.roll = float(roll)
            if not self.ready:
                self.form_rotation_matrix()
            self.update_timestamp = time.time()
            self.ready = True
            if self.verbose:
                # print(f"yaw: {yaw}, pitch: {pitch}, roll: {roll}")
                print(self.get_orientation())
        except Exception as e:
            print(e)

    def notification_handler_pitch_byte(self, sender, data):
        """ This would be more optimal than receiving strings """
        # print(f"Received data from {sender}: {int.from_bytes(data, 'little')}")
        try:
            # Data is sent in format (angle + 128), range 0-255
            data_int = int.from_bytes(data, byteorder='big')
            self.pitch = float(data_int - 128)  # Convert back to range [-128, 128]
            self.ready = True
        except Exception as e:
            print(e)

    def notification_handler_roll_byte(self, sender, data):
        """ This would be more optimal than receiving strings """
        # print(f"Received data from {sender}: {int.from_bytes(data, 'little')}")
        try:
            # Data is sent in format (angle + 128), range [0,255]
            data_int = int.from_bytes(data, byteorder='big')
            self.roll = float(data_int - 128)  # Convert back to range [-128, 128]

            self.ready = True
            if self.verbose:
                print(f"yaw: {self.yaw}, pitch: {self.pitch}, roll: {self.roll}")
        except Exception as e:
            print(e)

    # Define the main function to listen for notifications
    async def listen_for_notifications(self, address, characteristic_uuid):
        async with BleakClient(address) as client:
            # Start the notification listener
            # await client.start_notify(characteristic_uuid, self.notification_handler_roll_byte)
            await client.start_notify(characteristic_uuid, self.notification_handler)
            print("Listening for notifications...")

            # Keep the program running
            while not self.stop_event.is_set():
                await asyncio.sleep(5)  # Run for 30 seconds, adjust as needed

            # Stop the notification listener
            await client.stop_notify(characteristic_uuid)
            print("Stopped listening for notifications.")


    def run(self):
        # Start the event loop and listen for notifications
        print("Starting bt loop")
        # loop = asyncio.get_event_loop()
        # asyncio.run_coroutine_threadsafe(self.listen_for_notifications(self.address, self.characteristic_uuid),
        #                                  self.loop)
        self.thread.start()
        # self.loop.run_forever()

    def stop(self):
        print("Stopping bt loop")
        # self.loop = asyncio.get_event_loop()
        self.stop_event.set()
        # self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()

if __name__ == '__main__':
    x = BtServer(verbose=True)
    x.run()
    time.sleep(1000)
    x.stop()

