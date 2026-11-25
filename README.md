# Simple DMX

## Description

A simple DMX controller with animated effects. A personal project, because commercial control applications were huge, complicated to use, and expensive. Tested with "uDMX" USB adapter and Fuzzix Stellar 2 light only.

(C) 2026 Kati Salin under GNU GPL v2 license. ChatGPT and Claude Code used to assist in and to speed up the coding process.

Uses the udmx-pyusb package for communication, maintained by dhocker at https://dhocker.github.io/udmx-pyusb/ or https://github.com/dhocker/udmx-pyusb.

## Status

Still work in progress, writes only random values to channels.

Will have adjustable sliders in a window. Animation will be done by toggleable sine wave with adjustable speed (a second slider per channel.) Channel count and labels will be in a configuration py-file. If there is time, it will also have a few quick save / load presets for the channel value and effect slider's positions as profiles the user can quickly switch between and keep adjusting.

Will be tested only on Windows 11, possibly later on Linux if the adapter is compatible.

## Install
    python -m pip install -r requirements.txt

## Configuration
Modify the config.py file to set labels for channels, which also tells the amount of channels to use (counting from the starting address of 1.)

## Usage
    python simpledmx.py

Close the window (or press Ctrl+C in the terminal) to stop. Sets all channels to zero before closing the interface.

## Fader controls
    drag the fader cap, or click anywhere on the track to jump there
    mouse wheel           fine adjust by 1 (hold Shift for steps of 10)
    double-click          reset the channel to zero
