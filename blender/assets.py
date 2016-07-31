assets = []
khafile_defs = []

def reset():
    global assets
    global khafile_defs
    assets = []
    khafile_defs = []

def add(file):
    global assets
    assets.append(file)

def add_khafile_def(d):
	global khafile_defs
	khafile_defs.append(d)
