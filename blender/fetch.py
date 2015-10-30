import os
import bpy

def fetch():
    s = bpy.data.filepath.split(os.path.sep)
    name = s.pop()
    name = name.split(".")
    name = name[0]
    fp = os.path.sep.join(s)

    # Update scripts
    os.chdir(fp + "/Libraries/zblend/blender")
    os.system("git pull")

    # Clone kha
    #self.report({'INFO'}, "Fetching Kha...")
    os.chdir(fp)
    if not os.path.exists('Kha'):
        os.system("git clone --depth=1 --recursive https://github.com/ktxsoftware/Kha")

    os.chdir(fp + "/Kha")
    os.system("git pull && git submodule foreach --recursive git checkout master && git submodule foreach --recursive git pull origin master")
    
    # Create sources directories
    os.chdir(fp)
    if not os.path.exists('Sources/Shaders'):
        os.makedirs('Sources/Shaders')
    if not os.path.exists('Libraries/zblend/Sources'):
        os.makedirs('Libraries/zblend/Sources')
    if not os.path.exists('Libraries/dependencies'):
        os.makedirs('Libraries/dependencies')
    if not os.path.exists('Assets'):
        os.makedirs('Assets')
    
    # Clone dependencies
    #self.report({'INFO'}, "Fetching dependencies...")
    os.chdir(fp + "/Libraries/dependencies")
    if not os.path.exists('Sources'):
        os.system("git clone --depth=1 https://github.com/luboslenco/zblend_dependencies Sources")
    
    os.chdir(fp + "/Libraries/dependencies/Sources")
    os.system("git pull")
    
    # Clone shaders
    #self.report({'INFO'}, "Fetching shaders...")
    os.chdir(fp + "/Libraries/zblend/Sources")
    if not os.path.exists('Shaders'):
        os.system("git clone --depth=1 https://github.com/luboslenco/zblend_shaders Shaders")
    
    os.chdir(fp + "/Libraries/zblend/Sources/Shaders")
    os.system("git pull")

    # Clone oimo        
    os.chdir(fp + "/Libraries")
    if not os.path.exists('oimo'):
        os.system("git clone --depth=1 https://github.com/luboslenco/oimo oimo")
    
    os.chdir(fp + "/Libraries/oimo")
    os.system("git pull")

    # Clone haxebullet
    #self.report({'INFO'}, "Fetching physics...")
    os.chdir(fp + "/Libraries")
    if not os.path.exists('haxebullet'):
        os.system("git clone --depth=1 https://github.com/luboslenco/haxebullet haxebullet")

    os.chdir(fp + "/Libraries/haxebullet")
    os.system("git pull")

    # Clone zblend
    #self.report({'INFO'}, "Fetching zblend...")
    os.chdir(fp + "/Libraries/zblend/Sources")
    if not os.path.exists('zblend'):
        os.system("git clone --depth=1 https://github.com/luboslenco/zblend")
    
    os.chdir(fp + "/Libraries/zblend/Sources/zblend")
    os.system("git pull")

    print("Fetch complete!")

fetch()
