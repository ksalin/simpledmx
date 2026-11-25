"""
Configuration settings.

Edit the values below and restart simpledmx.py to apply them.
"""

# Channel labels, one per DMX channel, in channel order (the first entry is
# DMX channel 1). The number of faders in the window equals the number of
# entries here, so add or remove lines to change the channel count.
CHANNEL_NAMES = [
    "Channel 1",
    "Channel 2",
    "Channel 3",
    "Channel 4",
    "Channel 5",
    "Channel 6",
    "Channel 7",
    "Channel 8",
    "Channel 9",
    "Channel 10",
    "Channel 11",
    "Channel 12",
    "Channel 13",
    "Channel 14",
    "Channel 15",
    "Channel 16",
]


# Colours for the mixing-desk look, as "#rrggbb" hex values.
BG = "#1e1f22"           # window background
PANEL = "#2a2c30"        # background behind each fader
TEXT = "#e6e6e6"         # channel names, and values above zero
TEXT_DIM = "#8a8d93"     # values at zero and the status line
TICK = "#5a5d63"         # scale marks above and below the groove
GROOVE = "#0c0c0d"       # the slot the fader cap slides in
GROOVE_EDGE = "#45484e"  # outline of the groove
LEVEL = "#e0a030"        # lit part of the groove, up to the current value
CAP_BODY = "#c9cbcf"     # fader cap face
CAP_LIGHT = "#f2f3f5"    # fader cap highlights
CAP_SHADOW = "#7d8086"   # fader cap edges and grip ridges
CAP_LINE = "#1a1a1a"     # centre line on the fader cap
CAP_OUTLINE = "#3a3c40"  # thin border around the fader cap
CAP_DROP_SHADOW = "#111111"  # shadow under the fader cap
ERROR_TEXT = "#ff6b6b"   # status line when sending to the device fails
