assets = []
khafile_defs = []
embedded_data = []
shaders = []
shader_datas = []

def reset():
    global assets
    global khafile_defs
    global embedded_data
    global shaders
    global shader_datas
    assets = []
    khafile_defs = []
    embedded_data = []
    shaders = []
    shader_datas = []

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
    if file not in embedded_data:
        embedded_data.append(file)

def add_shader(file):
    global shaders
    if file not in shaders:
        shaders.append(file)

def add_shader_data(file):
    global shader_datas
    if file not in shader_datas:
        shader_datas.append(file)
