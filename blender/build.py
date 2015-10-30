import os
import webbrowser
import sys
import bpy
import shutil
import subprocess
import platform

def runProject(fp, target, name):
    os.chdir(fp)
    # HTML5
    if (target == '3'):
        webbrowser.open("http://127.0.0.1:8080/build/html5",new=2)

def build():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]  # Get all args after "--"

    s = bpy.data.filepath.split(os.path.sep)
    name = s.pop()
    name = name.split(".")
    name = name[0]
    fp = os.path.sep.join(s)
    os.chdir(fp)

    bashCommand = argv[0]
    build_type = argv[1]
    target = argv[2]

    haxelib_path = "haxelib"
    if platform.system() == 'Darwin':
        haxelib_path = "/usr/local/bin/haxelib"

    output = subprocess.check_output([haxelib_path + " path kha"], shell=True)
    output = str(output).split("\\n")[0].split("'")[1]
    kha_path = output
    node_path = output + "/Tools/nodejs/node-osx"

    print(subprocess.check_output([node_path + " " + kha_path + "/make -t html5"], shell=True))

    # Copy ammo.js if necessary
    if target == '3':
        if not os.path.isfile('build/html5/ammo.js'):
            output = subprocess.check_output([haxelib_path + " path haxebullet"], shell=True)
            output = str(output).split("\\n")[0].split("'")[1]
            ammojs_path = output + "js/ammo/ammo.js"
            
            shutil.copy(ammojs_path, 'build/html5')

    if build_type == '1':
        runProject(fp, target, name)

    print("Done!")

build()
