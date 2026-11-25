"""
Random 16-channel DMX tester for Anyma-compatible uDMX USB interfaces.

Install:
    py -m pip install udmx-pyusb

Run:
    py random_udmx.py

Press Ctrl+C to stop. The script attempts to set channels 1-16 to zero
before closing the interface.
"""

import random
import time

from pyudmx import pyudmx


CHANNEL_COUNT = 16
UPDATE_INTERVAL_SECONDS = 5


def main():
    device = pyudmx.uDMXDevice()

    print("Looking for uDMX interface (USB VID:PID 16C0:05DC)...")
    if not device.open():
        print("Could not open the uDMX interface.")
        print("Check that it is connected, that its Windows USB driver is")
        print("compatible with libusb, and that no other DMX program is using it.")
        return

    print("Connected. Randomizing DMX channels 1-16 every 5 seconds.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            values = [random.randint(0, 255) for _ in range(CHANNEL_COUNT)]

            # uDMX channel numbers are one-based: 1 through 16.
            for channel, value in enumerate(values, start=1):
                device.send_single_value(channel, value)

            print("DMX: " + "  ".join(
                f"{channel:02d}={value:03d}"
                for channel, value in enumerate(values, start=1)
            ))

            time.sleep(UPDATE_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nStopping; setting channels 1-16 to zero...")

    finally:
        try:
            for channel in range(1, CHANNEL_COUNT + 1):
                device.send_single_value(channel, 0)
        except Exception as exc:
            print(f"Could not send the blackout values: {exc}")
        finally:
            device.close()
            print("uDMX interface closed.")


if __name__ == "__main__":
    main()
