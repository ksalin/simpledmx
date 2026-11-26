"""
Configuration settings.

Edit the values below and restart simpledmx.py to apply them.
"""

# Channel labels, one per DMX channel, in channel order (the first entry is
# DMX channel 1). The number of faders in the window equals the number of
# entries here, so add or remove lines to change the channel count.

# Fuzzix Stellar 2 at A001
CHANNEL_NAMES = [
    "Bee Angle or Speed",    # Channel 1, 0-127 = Static angle, 128-191 = Continuous clockwise speed, 192-255 = Continuous anticlockwise speed
    "Gobo Speed",            # Channel 2
    "Laser Speed",           # Channel 3
    "Master Brightness",     # Channel 4
    "All Flicker",           # Channel 5, 0-9 = Continuous, 10 = Slow flicker, 255 = Fast flicker
    "Bee Red",               # Channel 6
    "Bee Green",             # Channel 7
    "Bee Blue",              # Channel 8
    "Bee White",             # Channel 9
    "Gobo Brightness",       # Channel 10, Gobo brightness
    "Red Shape Laser",       # Channel 11
    "Green Shape Laser",     # Channel 12
    "Red Dot Laser",         # Channel 13
    "Green Dot Laser",       # Channel 14
    "Strobe",                # Channel 15, lower = off/slow flickering, higher = rapid flickering
    "Full On"                # Channel 16
]


# Animation timer: the tightest interval, in milliseconds, at which animated
# channels are recalculated and sent to the DMX bus. 50 ms = 20 updates per
# second, which keeps the uDMX serial bus and the window redraws from being
# overloaded. Waveforms faster than half this rate (10 Hz at 50 ms) cannot be
# reproduced faithfully and will alias.
ANIMATION_INTERVAL_MS = 50

# Waveforms offered in each channel's dropdown, and the default choice.
WAVEFORMS = ["sine", "cosine", "square", "sawtooth", "noise"]
DEFAULT_WAVEFORM = "sine"


# Colours for the mixing-desk look, as "#rrggbb" hex values.
BG = "#1e1f22"           # window background
PANEL = "#2a2c30"        # background behind each fader
TEXT = "#e6e6e6"         # channel names, and values above zero
TEXT_DIM = "#8a8d93"     # values at zero and the status line
TICK = "#5a5d63"         # scale marks above and below the groove
GROOVE = "#0c0c0d"       # the slot the fader cap slides in
GROOVE_EDGE = "#45484e"  # outline of the groove
LEVEL = "#30c0f0"        # lit part of the groove, up to the current value
CAP_BODY = "#c9cbcf"     # fader cap face
CAP_LIGHT = "#f2f3f5"    # fader cap highlights
CAP_SHADOW = "#7d8086"   # fader cap edges and grip ridges
CAP_LINE = "#1a1a1a"     # centre line on the fader cap
CAP_OUTLINE = "#3a3c40"  # thin border around the fader cap
CAP_DROP_SHADOW = "#111111"  # shadow under the fader cap
ERROR_TEXT = "#ff6b6b"   # status line when sending to the device fails
ENTRY_BG = "#141517"     # from / to / Hz text boxes
ENTRY_INVALID = "#5a1e1e"  # text box background when its value is not valid
BUTTON_BG = "#3a3c40"    # waveform dropdown and play/stop buttons
BUTTON_ACTIVE = "#4a4d52"  # buttons under the mouse
PLAYING = "#2e9e4f"      # play/stop button while the channel is animating
