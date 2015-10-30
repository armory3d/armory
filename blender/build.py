import os
import webbrowser
import sys
import bpy
import shutil

def runProject(fp, target, name):
    os.chdir(fp)
    # OSX
    if (target == '0'):
        bashCommand = "xcodebuild -project 'build/osx-build/" + name + ".xcodeproj' && open 'build/osx-build/build/Release/" + name + ".app/Contents/MacOS/" + name + "'"
        os.system(bashCommand)
    # HTML5
    elif (target == '3'):
        webbrowser.open("http://127.0.0.1:8000/build/html5",new=2)

def openProject(fp, target, name):
    os.chdir(fp)
    # OSX
    if (target == '0'):
        bashCommand = "open -a Xcode.app 'build/osx-build/" + name + ".xcodeproj'"
        os.system(bashCommand)

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

    os.system(bashCommand)

    # Copy ammo.js if necessary
    if (target == '3'):
        if not os.path.isfile('build/html5/ammo.js'):
            shutil.copy('Libraries/haxebullet/js/ammo/ammo.js', 'build/html5')

    if build_type == '2':
        openProject(fp, target, name)
    elif build_type == '1':
        runProject(fp, target, name)

    print("Build done!")

build()
