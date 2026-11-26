"""
Simple DMX

(C) 2026 Kati Salin under GNU GPL v2 license. ChatGPT and Claude Code used to assist in and to speed up the coding process.
"""

import math
import random
import signal
import time
import tkinter as tk
import sys
from pathlib import Path
from pyudmx import pyudmx # The library used for uDMX communication, install via requirements.txt

from config import *  # all settings: channel names, colours, ...

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys._MEIPASS)
else:
    APP_DIR = Path.cwd() #Path(__file__).resolve().parent

CHANNEL_COUNT = len(CHANNEL_NAMES) # Number of channels comes from configuration - each channel must be labeled with a name
DMX_MAX = 255 # Value per channel is between 0 and 255, 8 bits
PNG_ICON = APP_DIR / "simpledmx_icon.png"
        
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
        self.locked = False  # True while the channel is animated
        self._drag_offset = 0

        self.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Double-Button-1>", self._on_double_click)
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

    def set_value(self, value, notify=True):
        """Move the cap. Returns True if the value changed. With notify=False
        the command callback is skipped (the caller sends the value itself)."""
        value = min(max(int(value), 0), DMX_MAX)
        if value == self.value:
            return False
        self.value = value
        self._redraw()
        if notify:
            self.command(value)
        return True

    def set_locked(self, locked):
        """Ignore mouse input while the channel is being animated."""
        self.locked = locked
        self.configure(cursor="arrow" if locked else "hand2")

    def _on_double_click(self, _event):
        if not self.locked:
            self.set_value(0)

    def _on_press(self, event):
        self.focus_set()
        if self.locked:
            return
        cap_x = self._value_to_x(self.value)
        if abs(event.x - cap_x) <= self.CAP_WIDTH // 2:
            # Grabbed the cap: keep the grab point under the mouse.
            self._drag_offset = event.x - cap_x
        else:
            # Clicked the track: jump the cap there.
            self._drag_offset = 0
            self.set_value(self._x_to_value(event.x))

    def _on_drag(self, event):
        if self.locked:
            return
        self.set_value(self._x_to_value(event.x - self._drag_offset))

    def _on_wheel(self, event, direction=None):
        if self.locked:
            return
        if direction is None:
            direction = 1 if event.delta > 0 else -1
        step = 10 if event.state & 0x0001 else 1  # Shift held
        self.set_value(self.value + direction * step)


def waveform_level(waveform, phase, noise_level):
    """Level 0.0-1.0 of a waveform at phase 0.0-1.0 (one cycle)."""
    if waveform == "sine":
        return 0.5 + 0.5 * math.sin(2 * math.pi * phase)
    if waveform == "cosine":
        return 0.5 + 0.5 * math.cos(2 * math.pi * phase)
    if waveform == "square":
        return 1.0 if phase < 0.5 else 0.0
    if waveform == "sawtooth":
        return phase
    if waveform == "noise":
        return noise_level  # a new random level is picked once per cycle
    return 0.0


class ChannelAnimation:
    """The from / to / Hz / waveform / play controls of one channel."""

    def __init__(self, master, row, fader, on_value):
        self.fader = fader
        self.on_value = on_value  # called with each new animated value
        self.playing = False
        self.phase = 0.0
        self.noise_level = 0.0

        # Last valid settings; invalid typing keeps these until it is fixed.
        self.low = 0
        self.high = DMX_MAX
        self.hz = 1.0

        self.low_var = tk.StringVar(value=str(self.low))
        self.high_var = tk.StringVar(value=str(self.high))
        self.hz_var = tk.StringVar(value=f"{self.hz:.3f}")
        self.wave_var = tk.StringVar(value=DEFAULT_WAVEFORM)

        self.low_entry = self._entry(master, self.low_var, 4, row, 3)
        self.high_entry = self._entry(master, self.high_var, 4, row, 4)
        self.hz_entry = self._entry(master, self.hz_var, 7, row, 5)
        self.low_var.trace_add("write", lambda *_: self._parse_range())
        self.high_var.trace_add("write", lambda *_: self._parse_range())
        self.hz_var.trace_add("write", lambda *_: self._parse_hz())

        menu = tk.OptionMenu(master, self.wave_var, *WAVEFORMS)
        menu.configure(bg=BUTTON_BG, fg=TEXT, activebackground=BUTTON_ACTIVE,
                       activeforeground=TEXT, highlightthickness=0, bd=0,
                       relief="flat", width=8, font=("Segoe UI", 9))
        menu["menu"].configure(bg=BUTTON_BG, fg=TEXT,
                               activebackground=LEVEL, activeforeground=BG)
        menu.grid(row=row, column=6, padx=(6, 0))

        self.play_button = tk.Button(
            master, text="▶", width=3, command=self.toggle,
            bg=BUTTON_BG, fg=TEXT, activebackground=BUTTON_ACTIVE,
            activeforeground=TEXT, relief="flat", bd=0,
            font=("Segoe UI Symbol", 10))
        self.play_button.grid(row=row, column=7, padx=(6, 0))

    @staticmethod
    def _entry(master, var, width, row, column):
        entry = tk.Entry(master, textvariable=var, width=width, justify="right",
                         bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                         relief="flat", highlightthickness=1,
                         highlightbackground=GROOVE_EDGE,
                         highlightcolor=LEVEL, font=("Consolas", 10))
        entry.grid(row=row, column=column, padx=(6, 0), ipady=2)
        return entry

    # --- input validation -----------------------------------------------

    def _parse_range(self):
        for var, entry, attr in ((self.low_var, self.low_entry, "low"),
                                 (self.high_var, self.high_entry, "high")):
            try:
                value = int(var.get().strip())
                valid = 0 <= value <= DMX_MAX
            except ValueError:
                valid = False
            if valid:
                setattr(self, attr, value)
            entry.configure(bg=ENTRY_BG if valid else ENTRY_INVALID)

    def _parse_hz(self):
        try:
            value = float(self.hz_var.get().strip().replace(",", "."))
            valid = math.isfinite(value) and value >= 0
        except ValueError:
            valid = False
        if valid:
            self.hz = value
        self.hz_entry.configure(bg=ENTRY_BG if valid else ENTRY_INVALID)

    # --- play / stop ----------------------------------------------------

    def toggle(self):
        self.playing = not self.playing
        if self.playing:
            self.phase = 0.0
            self.noise_level = random.random()
        self.fader.set_locked(self.playing)
        self.play_button.configure(
            text="■" if self.playing else "▶",
            bg=PLAYING if self.playing else BUTTON_BG)

    def advance(self, seconds):
        """Step the waveform forward and move the fader. Returns True if
        the channel's value changed."""
        self.phase += self.hz * seconds
        if self.phase >= 1.0:
            self.phase -= math.floor(self.phase)
            self.noise_level = random.random()
        level = waveform_level(self.wave_var.get(), self.phase,
                               self.noise_level)
        value = round(self.low + (self.high - self.low) * level)
        if self.fader.set_value(value, notify=False):
            self.on_value(value)
            return True
        return False


class DmxWindow:
    def __init__(self, root, device):
        self.root = root
        self.device = device
        self._send_error_shown = False

        root.title("Simple DMX")
        root.configure(bg=BG)

        if PNG_ICON.exists():
            icon_png = tk.PhotoImage(file=str(PNG_ICON))
            root.iconphoto(True, icon_png)
            root._icon = icon_png # Keep image reference alive

        # Size the faders so the window fits on the screen (max 1920x1080,
        # leaving room for the taskbar and window decorations). With Windows
        # display scaling the usable screen is smaller, e.g. 1536x864 at 125%.
        screen_w = min(root.winfo_screenwidth(), 1920)
        screen_h = min(root.winfo_screenheight(), 1080)
        fader_width = max(400, min(1400, screen_w - 720))
        fader_height = (screen_h - 190) // CHANNEL_COUNT - 4
        fader_height = max(Fader.MIN_HEIGHT, min(Fader.MAX_HEIGHT, fader_height))

        frame = tk.Frame(root, bg=BG, padx=16, pady=12)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        for column, title in ((3, "From"), (4, "To"), (5, "Hz"),
                              (6, "Waveform"), (7, "Play")):
            tk.Label(frame, text=title, bg=BG, fg=TEXT_DIM,
                     font=("Segoe UI", 9)).grid(row=0, column=column,
                                                padx=(6, 0))

        self.value_labels = []
        self.faders = []
        self.animations = []
        for index, name in enumerate(CHANNEL_NAMES):
            channel = index + 1  # uDMX channel numbers are one-based
            row = index + 1      # row 0 holds the column titles

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

            self.animations.append(ChannelAnimation(
                frame, row, fader,
                on_value=lambda value, ch=channel: self._show_value(ch, value),
            ))

        self.status = tk.Label(root, text="Connected to uDMX.", bg=BG,
                               fg=TEXT_DIM, anchor="w", padx=16)
        self.status.pack(fill="x", pady=(0, 8))

        root.protocol("WM_DELETE_WINDOW", root.destroy)

        # Animation timer: runs every ANIMATION_INTERVAL_MS for the whole
        # session and drives the channels whose play button is on.
        self._last_tick = time.perf_counter()
        root.after(ANIMATION_INTERVAL_MS, self._tick)

    def _tick(self):
        started = time.perf_counter()
        # Use the real elapsed time, so the waveform speed stays correct even
        # if the timer fires late (e.g. while the window is being dragged).
        elapsed = started - self._last_tick
        self._last_tick = started

        changed = False
        for animation in self.animations:
            if animation.playing:
                changed |= animation.advance(elapsed)

        if changed:
            # One USB transfer for all channels instead of one per channel.
            self._send(lambda: self.device.send_multi_value(
                1, [fader.value for fader in self.faders]))

        spent_ms = int((time.perf_counter() - started) * 1000)
        self.root.after(max(1, ANIMATION_INTERVAL_MS - spent_ms), self._tick)

    def _show_value(self, channel, value):
        self.value_labels[channel - 1].configure(
            text=str(value), fg=TEXT if value else TEXT_DIM)

    def _on_change(self, channel, value):
        self._show_value(channel, value)
        self._send(lambda: self.device.send_single_value(channel, value))

    def _send(self, send):
        try:
            send()
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
