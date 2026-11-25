"""
Simple DMX

(C) 2026 Kati Salin under GNU GPL v2 license. ChatGPT and Claude Code used to assist in and to speed up the coding process.
"""

import signal
import tkinter as tk

from pyudmx import pyudmx # The library used for uDMX communication, install via requirements.txt

from config import *  # all settings: channel names, colours, ...

CHANNEL_COUNT = len(CHANNEL_NAMES) # Number of channels comes from configuration - each channel must be labeled with a name
DMX_MAX = 255 # Value per channel is between 0 and 255, 8 bits


class Fader(tk.Canvas):
    """A horizontal fader drawn to look like a mixing console slider."""

    MAX_HEIGHT = 46
    MIN_HEIGHT = 28
    CAP_WIDTH = 24
    PAD = 22  # horizontal space left at both ends so the cap fits

    def __init__(self, master, command, width=1200, height=MAX_HEIGHT):
        self.HEIGHT = height
        self.CAP_HEIGHT = height - 10
        super().__init__(
            master, width=width, height=height, bg=PANEL,
            highlightthickness=0, cursor="hand2",
        )
        self.command = command
        self.value = 0
        self._drag_offset = 0

        self.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Double-Button-1>", lambda _e: self.set_value(0))
        self.bind("<MouseWheel>", self._on_wheel)                 # Windows
        self.bind("<Button-4>", lambda e: self._on_wheel(e, +1))  # Linux
        self.bind("<Button-5>", lambda e: self._on_wheel(e, -1))  # Linux

    # --- geometry -------------------------------------------------------

    def _track_span(self):
        width = max(self.winfo_width(), 2 * self.PAD + 1)
        return self.PAD, width - self.PAD

    def _value_to_x(self, value):
        x0, x1 = self._track_span()
        return x0 + (x1 - x0) * value / DMX_MAX

    def _x_to_value(self, x):
        x0, x1 = self._track_span()
        fraction = (x - x0) / (x1 - x0)
        return round(min(max(fraction, 0.0), 1.0) * DMX_MAX)

    # --- drawing --------------------------------------------------------

    def _redraw(self):
        self.delete("all")
        x0, x1 = self._track_span()
        mid = self.HEIGHT // 2

        # Scale ticks above and below the groove: 10 % steps, with the
        # 0 / 50 / 100 % marks longer.
        for step in range(11):
            x = x0 + (x1 - x0) * step / 10
            length = (9 if step in (0, 5, 10) else 5) * self.HEIGHT // 46
            self.create_line(x, mid - 8 - length, x, mid - 8, fill=TICK)
            self.create_line(x, mid + 8, x, mid + 8 + length, fill=TICK)

        # The groove the cap slides in, with a lit section up to the value.
        self.create_rectangle(x0 - 3, mid - 4, x1 + 3, mid + 4,
                              fill=GROOVE, outline=GROOVE_EDGE)
        cap_x = self._value_to_x(self.value)
        if self.value > 0:
            self.create_rectangle(x0 - 1, mid - 2, cap_x, mid + 2,
                                  fill=LEVEL, width=0)

        # The fader cap: bevelled body, grip ridges and a centre line.
        half_w, half_h = self.CAP_WIDTH // 2, self.CAP_HEIGHT // 2
        left, right = cap_x - half_w, cap_x + half_w
        top, bottom = mid - half_h, mid + half_h
        self.create_rectangle(left + 2, top + 2, right + 2, bottom + 2,
                              fill=CAP_DROP_SHADOW, width=0)  # drop shadow
        self.create_rectangle(left, top, right, bottom,
                              fill=CAP_SHADOW, outline=CAP_OUTLINE)
        self.create_rectangle(left + 1, top + 1, right - 2, bottom - 2,
                              fill=CAP_LIGHT, width=0)
        self.create_rectangle(left + 3, top + 3, right - 2, bottom - 2,
                              fill=CAP_BODY, width=0)
        for dx in (-8, -5, 5, 8):
            self.create_line(cap_x + dx, top + 5, cap_x + dx, bottom - 5,
                             fill=CAP_SHADOW)
            self.create_line(cap_x + dx + 1, top + 5, cap_x + dx + 1,
                             bottom - 5, fill=CAP_LIGHT)
        self.create_line(cap_x, top + 2, cap_x, bottom - 2,
                         fill=CAP_LINE, width=2)

    # --- interaction ----------------------------------------------------

    def set_value(self, value):
        value = min(max(int(value), 0), DMX_MAX)
        if value == self.value:
            return
        self.value = value
        self._redraw()
        self.command(value)

    def _on_press(self, event):
        self.focus_set()
        cap_x = self._value_to_x(self.value)
        if abs(event.x - cap_x) <= self.CAP_WIDTH // 2:
            # Grabbed the cap: keep the grab point under the mouse.
            self._drag_offset = event.x - cap_x
        else:
            # Clicked the track: jump the cap there.
            self._drag_offset = 0
            self.set_value(self._x_to_value(event.x))

    def _on_drag(self, event):
        self.set_value(self._x_to_value(event.x - self._drag_offset))

    def _on_wheel(self, event, direction=None):
        if direction is None:
            direction = 1 if event.delta > 0 else -1
        step = 10 if event.state & 0x0001 else 1  # Shift held
        self.set_value(self.value + direction * step)


class DmxWindow:
    def __init__(self, root, device):
        self.root = root
        self.device = device
        self._send_error_shown = False

        root.title("Simple DMX")
        root.configure(bg=BG)

        # Size the faders so the window fits on the screen (max 1920x1080,
        # leaving room for the taskbar and window decorations). With Windows
        # display scaling the usable screen is smaller, e.g. 1536x864 at 125%.
        screen_w = min(root.winfo_screenwidth(), 1920)
        screen_h = min(root.winfo_screenheight(), 1080)
        fader_width = max(400, min(1400, screen_w - 380))
        fader_height = (screen_h - 160) // CHANNEL_COUNT - 4
        fader_height = max(Fader.MIN_HEIGHT, min(Fader.MAX_HEIGHT, fader_height))

        frame = tk.Frame(root, bg=BG, padx=16, pady=12)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        self.value_labels = []
        self.faders = []
        for row, name in enumerate(CHANNEL_NAMES):
            channel = row + 1  # uDMX channel numbers are one-based

            tk.Label(frame, text=name, bg=BG, fg=TEXT, anchor="e",
                     font=("Segoe UI", 11), width=16).grid(
                row=row, column=0, sticky="e", padx=(0, 12), pady=2)

            value_label = tk.Label(frame, text="0", bg=BG, fg=TEXT_DIM,
                                   font=("Consolas", 12, "bold"), width=4,
                                   anchor="e")
            value_label.grid(row=row, column=2, padx=(12, 0))
            self.value_labels.append(value_label)

            fader = Fader(
                frame, width=fader_width, height=fader_height,
                command=lambda value, ch=channel: self._on_change(ch, value),
            )
            fader.grid(row=row, column=1, sticky="ew", pady=2)
            self.faders.append(fader)

        self.status = tk.Label(root, text="Connected to uDMX.", bg=BG,
                               fg=TEXT_DIM, anchor="w", padx=16)
        self.status.pack(fill="x", pady=(0, 8))

        root.protocol("WM_DELETE_WINDOW", root.destroy)

    def _on_change(self, channel, value):
        self.value_labels[channel - 1].configure(
            text=str(value), fg=TEXT if value else TEXT_DIM)
        try:
            self.device.send_single_value(channel, value)
        except Exception as exc:
            self.status.configure(text=f"Send failed: {exc}", fg=ERROR_TEXT)
            if not self._send_error_shown:
                print(f"Could not send DMX value: {exc}")
                self._send_error_shown = True


def blackout(device):
    for channel in range(1, CHANNEL_COUNT + 1):
        device.send_single_value(channel, 0)


def main():
    device = pyudmx.uDMXDevice()

    print("Looking for uDMX interface (USB VID:PID 16C0:05DC)...")
    if not device.open():
        print("Could not open the uDMX interface.")
        print("Check that it is connected, that its Windows USB driver is")
        print("compatible with libusb, and that no other DMX program is using it.")
        return

    print(f"Connected. Controlling DMX channels 1-{CHANNEL_COUNT}.")
    print("Close the window or press Ctrl+C to stop.\n")

    try:
        # Start from a known state: every channel at zero, like the faders.
        blackout(device)

        root = tk.Tk()
        DmxWindow(root, device)

        # Ctrl+C in the terminal closes the window. Tk's main loop does not
        # give Python a chance to handle signals on its own, so wake it up
        # periodically.
        signal.signal(signal.SIGINT, lambda *_: root.destroy())

        def keep_signals_alive():
            root.after(200, keep_signals_alive)

        keep_signals_alive()
        root.mainloop()

    except KeyboardInterrupt:
        pass

    finally:
        print(f"\nStopping; setting channels 1-{CHANNEL_COUNT} to zero...")
        try:
            blackout(device)
        except Exception as exc:
            print(f"Could not send the blackout values: {exc}")
        finally:
            device.close()
            print("uDMX interface closed.")


if __name__ == "__main__":
    main()
