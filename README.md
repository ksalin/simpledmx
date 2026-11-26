# Simple DMX

## Description

A simple DMX controller with animated effects. A personal project, because commercial control applications were huge, complicated to use, and expensive. Tested with "uDMX" USB adapter and Fuzzix Stellar 2 light only.

(C) 2026 Kati Salin under GNU GPL v2 license. ChatGPT and Claude Code used to assist in and to speed up the coding process.

Uses the udmx-pyusb package for communication, maintained by dhocker at https://dhocker.github.io/udmx-pyusb/ or https://github.com/dhocker/udmx-pyusb.

## Status

Still work in progress!

Implemented:
- Can adjust each channels values 0-255 with sliders in real time
- Channels are labeled
- Per-channel waveform animation (sine, cosine, square, sawtooth, noise) between a chosen range at a chosen speed

TODO:
- Quick save/load profile slots
- Status message on the lower part of the window could be dynamic about what was last done

Tested only on Windows 11, not yet on Linux.

## Install and usage

To run as-is:
    python -m pip install -r requirements.txt
    python simpledmx.py

To build a distribution:
    pip install pyinstaller
    make_dist.bat or ./make_dist.sh

Close the window (or press Ctrl+C in the terminal) to stop. Sets all channels to zero before closing the interface.

## Configuration
Modify the config.py file to set labels for channels, which also tells the amount of channels to use (counting from the starting address of 1.)

`ANIMATION_INTERVAL_MS` in config.py sets how often animated channels are updated (default 50 ms = 20 times a second, to avoid flooding the DMX bus and the window). Waveforms faster than half that rate (10 Hz by default) will alias.

## Fader controls
    drag the fader cap, or click anywhere on the track to jump there
    mouse wheel           fine adjust by 1 (hold Shift for steps of 10)
    double-click          reset the channel to zero

## Waveform controls
Each channel has, to the right of its fader:

    From, To      range 0-255 the waveform moves between (From > To inverts it)
    Hz            cycles per second, decimals allowed (e.g. 0.250)
    Waveform      sine, cosine, square, sawtooth or noise (noise picks a new random level once per cycle)
    Play / Stop   starts or stops animating the channel

All channels start stopped. While a channel plays, its fader follows the waveform and cannot be dragged; when stopped it stays where it was and is manually adjustable again. Settings can be changed while playing. An invalid entry turns red and the last valid value stays in use.
