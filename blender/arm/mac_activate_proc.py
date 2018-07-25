#!/usr/bin/python

import sys
from Cocoa import NSRunningApplication, NSApplicationActivateIgnoringOtherApps

# see https://stackoverflow.com/questions/10655484/how-to-start-an-app-in-the-foreground-on-mac-os-x-with-python
app = NSRunningApplication.runningApplicationWithProcessIdentifier_(int(sys.argv[1]))
app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
