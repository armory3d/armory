assets = []
khafile_defs = []
embedded_data = []

def reset():
	global assets
	global khafile_defs
	global embedded_data
	assets = []
	khafile_defs = []
	embedded_data = []

def add(file):
	global assets
	if file not in assets:
		assets.append(file)

def add_khafile_def(d):
	global khafile_defs
	if d not in khafile_defs:
		khafile_defs.append(d)

def add_embedded_data(file):
	global embedded_data
	# add(file)
	embedded_data.append(file)
