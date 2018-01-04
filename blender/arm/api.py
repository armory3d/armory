
drivers = dict()

def add_driver(driver_name, draw_props, make_rpass, make_rpath):
	global drivers

	if driver_name in drivers:
		return

	d = {}
	d['driver_name'] = driver_name
	d['draw_props'] = draw_props
	d['make_rpass'] = make_rpass
	d['make_rpath'] = make_rpath

	drivers[driver_name] = d
