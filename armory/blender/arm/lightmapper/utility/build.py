import bpy, os, subprocess, sys, platform, aud, json, datetime, socket

from . import encoding, pack, log
from . cycles import lightmap, prepare, nodes, cache
from . luxcore import setup
from . octane import configure, lightmap2
from . denoiser import integrated, oidn, optix
from . filtering import opencv
from . gui import Viewport
from .. network import client

from os import listdir
from os.path import isfile, join
from time import time, sleep
from importlib import util

previous_settings = {}
postprocess_shutdown = False
logging = True

def prepare_build(self=0, background_mode=False, shutdown_after_build=False):

    global tlm_log
    tlm_log = log.TLM_Logman()
    bpy.app.driver_namespace["logman"] = tlm_log
    tlm_log.append("Preparing build")

    if shutdown_after_build:
        postprocess_shutdown = True

    print("Building lightmaps")

    if bpy.context.scene.TLM_EngineProperties.tlm_lighting_mode == "combinedao": 

        scene = bpy.context.scene

        if not "tlm_plus_mode" in bpy.app.driver_namespace or bpy.app.driver_namespace["tlm_plus_mode"] == 0:
            filepath = bpy.data.filepath
            dirpath = os.path.join(os.path.dirname(bpy.data.filepath), scene.TLM_EngineProperties.tlm_lightmap_savedir)
            if os.path.isdir(dirpath):
                for file in os.listdir(dirpath):
                    os.remove(os.path.join(dirpath + "/" + file))
            bpy.app.driver_namespace["tlm_plus_mode"] = 1
            print("Plus Mode")

    if bpy.context.scene.TLM_EngineProperties.tlm_lighting_mode == "indirectao": 

        scene = bpy.context.scene

        if not "tlm_plus_mode" in bpy.app.driver_namespace or bpy.app.driver_namespace["tlm_plus_mode"] == 0:
            filepath = bpy.data.filepath
            dirpath = os.path.join(os.path.dirname(bpy.data.filepath), scene.TLM_EngineProperties.tlm_lightmap_savedir)
            if os.path.isdir(dirpath):
                for file in os.listdir(dirpath):
                    os.remove(os.path.join(dirpath + "/" + file))
            bpy.app.driver_namespace["tlm_plus_mode"] = 1
            print("Plus Mode")

    if bpy.context.scene.TLM_EngineProperties.tlm_bake_mode == "Foreground" or background_mode==True:

        global start_time
        start_time = time()
        bpy.app.driver_namespace["tlm_start_time"] = time()

        scene = bpy.context.scene
        sceneProperties = scene.TLM_SceneProperties

        if not background_mode and bpy.context.scene.TLM_EngineProperties.tlm_lighting_mode != "combinedao" and bpy.context.scene.TLM_EngineProperties.tlm_lighting_mode != "indirectao":
            #pass
            setGui(1)

        if check_save():
            print("Please save your file first")
            self.report({'INFO'}, "Please save your file first")
            setGui(0)
            return{'FINISHED'}

        if check_denoiser():
            print("No denoise OIDN path assigned")
            self.report({'INFO'}, "No denoise OIDN path assigned. Check that it points to the correct executable.")
            setGui(0)
            return{'FINISHED'}

        if check_materials():
            print("Error with material")
            self.report({'INFO'}, "Error with material")
            setGui(0)
            return{'FINISHED'}

        if opencv_check():
            if sceneProperties.tlm_filtering_use:
                print("Error:Filtering - OpenCV not installed")
                self.report({'INFO'}, "Error:Filtering - OpenCV not installed")
                setGui(0)
                return{'FINISHED'}

        setMode()

        dirpath = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)
        if not os.path.isdir(dirpath):
            os.mkdir(dirpath)

        #Naming check
        naming_check()

        if sceneProperties.tlm_lightmap_engine == "Cycles":

            prepare.init(self, previous_settings)

        if sceneProperties.tlm_lightmap_engine == "LuxCoreRender":

            setup.init(self, previous_settings)

        if sceneProperties.tlm_lightmap_engine == "OctaneRender":

            configure.init(self, previous_settings)

        begin_build()

    else:

        print("Baking in background")

        filepath = bpy.data.filepath

        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

        start_time = time()

        scene = bpy.context.scene
        sceneProperties = scene.TLM_SceneProperties

        #Timer start here bound to global
        if check_save():
            print("Please save your file first")
            self.report({'INFO'}, "Please save your file first")
            return{'FINISHED'}

        if check_denoiser():
            print("No denoise OIDN path assigned")
            self.report({'INFO'}, "No denoise OIDN path assigned")
            return{'FINISHED'}

        if check_materials():
            print("Error with material")
            self.report({'INFO'}, "Error with material")
            return{'FINISHED'}

        if opencv_check():
            if sceneProperties.tlm_filtering_use:
                print("Error:Filtering - OpenCV not installed")
                self.report({'INFO'}, "Error:Filtering - OpenCV not installed")
                return{'FINISHED'}

        dirpath = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)
        if not os.path.isdir(dirpath):
            os.mkdir(dirpath)

        #Naming check
        naming_check()

        if scene.TLM_SceneProperties.tlm_network_render:

            print("NETWORK RENDERING")

            if scene.TLM_SceneProperties.tlm_network_paths != None:
                HOST = bpy.data.texts[scene.TLM_SceneProperties.tlm_network_paths.name].lines[0].body  # The server's hostname or IP address
            else:
                HOST = '127.0.0.1'  # The server's hostname or IP address

            PORT = 9898        # The port used by the server

            client.connect_client(HOST, PORT, bpy.data.filepath, 0)

            finish_assemble()

        else:

            print("Background driver process")

            bpy.app.driver_namespace["alpha"] = 0

            bpy.app.driver_namespace["tlm_process"] = False

            if os.path.exists(os.path.join(dirpath, "process.tlm")):
                os.remove(os.path.join(dirpath, "process.tlm"))

            bpy.app.timers.register(distribute_building)

def distribute_building():

    print("Distributing lightmap building")

    #CHECK IF THERE'S AN EXISTING SUBPROCESS 

    if not os.path.isfile(os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir, "process.tlm")):
        
        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
            print("No process file - Creating one...")
            tlm_log.append("No process file - Creating one...")
        
        write_directory = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)

        blendPath = bpy.data.filepath

        process_status = [blendPath, 
                    {'bake': 'all', 
                    'completed': False
                    }]

        with open(os.path.join(write_directory, "process.tlm"), 'w') as file:
            json.dump(process_status, file, indent=2)

        if (2, 91, 0) > bpy.app.version:
            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                bpy.app.driver_namespace["tlm_process"] = subprocess.Popen([sys.executable,"-b", blendPath,"--python-expr",'import bpy; import thelightmapper; thelightmapper.addon.utility.build.prepare_build(0, True);'], shell=False, stdout=subprocess.PIPE)
            else:
                bpy.app.driver_namespace["tlm_process"] = subprocess.Popen([sys.executable,"-b", blendPath,"--python-expr",'import bpy; import thelightmapper; thelightmapper.addon.utility.build.prepare_build(0, True);'], shell=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        else:
            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                bpy.app.driver_namespace["tlm_process"] = subprocess.Popen([bpy.app.binary_path,"-b", blendPath,"--python-expr",'import bpy; import thelightmapper; thelightmapper.addon.utility.build.prepare_build(0, True);'], shell=False, stdout=subprocess.PIPE)
            else:
                bpy.app.driver_namespace["tlm_process"] = subprocess.Popen([bpy.app.binary_path,"-b", blendPath,"--python-expr",'import bpy; import thelightmapper; thelightmapper.addon.utility.build.prepare_build(0, True);'], shell=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        tlm_log.append("Started process: " + str(bpy.app.driver_namespace["tlm_process"]) + " at " + str(datetime.datetime.now()))
        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
            print("Started process: " + str(bpy.app.driver_namespace["tlm_process"]) + " at " + str(datetime.datetime.now()))

    else:

        write_directory = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)

        process_status = json.loads(open(os.path.join(write_directory, "process.tlm")).read())

        if process_status[1]["completed"]:

            tlm_log.append("Baking finished from process. Status: Completed.")
            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                print("Baking finished")

            bpy.app.timers.unregister(distribute_building)

            finish_assemble()

        else:

            #Open the json and check the status!
            tlm_log.append("Process check: Baking in progress.")
            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                print("Baking in progress")
            
            process_status = json.loads(open(os.path.join(write_directory, "process.tlm")).read())

            tlm_log.append(process_status)
            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                print(process_status)

    return 1.0


def finish_assemble(self=0, background_pass=0, load_atlas=0):

    print("Finishing assembly")

    tlm_log = log.TLM_Logman()
    tlm_log.append("Preparing build")

    if load_atlas:
        print("Assembly in Atlas load mode")
        tlm_log.append("Assembly in Atlas load mode")

    tlm_log.append("Background baking finished")
    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        print("Background baking finished")

    scene = bpy.context.scene
    sceneProperties = scene.TLM_SceneProperties

    if sceneProperties.tlm_lightmap_engine == "Cycles":

        prepare.init(self, previous_settings)

    if sceneProperties.tlm_lightmap_engine == "LuxCoreRender":
        pass

    if sceneProperties.tlm_lightmap_engine == "OctaneRender":
        pass

    if not 'start_time' in globals():
        global start_time
        start_time = time()

    if background_pass:
        manage_build(True, load_atlas)
    else:
        manage_build(False, load_atlas)

def begin_build():

    print("Beginning build")

    dirpath = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)

    scene = bpy.context.scene
    sceneProperties = scene.TLM_SceneProperties

    if sceneProperties.tlm_lightmap_engine == "Cycles":

        lightmap.bake()

        # try:
        #     lightmap.bake()
        # except Exception as e:

        #     print("An error occured during lightmap baking. See the line below for more detail:")
        #     print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

        #     tlm_log.append("An error occured during lightmap baking. See the line below for more detail:")
        #     tlm_log.append(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

        #     if not bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        #         print("Turn on verbose mode to get more detail.")

    if sceneProperties.tlm_lightmap_engine == "LuxCoreRender":
        pass

    if sceneProperties.tlm_lightmap_engine == "OctaneRender":

        lightmap2.bake()

    #Denoiser
    if sceneProperties.tlm_denoise_use:

        if sceneProperties.tlm_denoise_engine == "Integrated":

            baked_image_array = []

            dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

            for file in dirfiles:
                if file.endswith("_baked.hdr"):
                    baked_image_array.append(file)

            tlm_log.append(baked_image_array)
            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                print(baked_image_array)

            denoiser = integrated.TLM_Integrated_Denoise()

            denoiser.load(baked_image_array)

            denoiser.setOutputDir(dirpath)

            denoiser.denoise()

        elif sceneProperties.tlm_denoise_engine == "OIDN":

            baked_image_array = []

            dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

            for file in dirfiles:
                if file.endswith("_baked.hdr"):
                    baked_image_array.append(file)

            oidnProperties = scene.TLM_OIDNEngineProperties

            denoiser = oidn.TLM_OIDN_Denoise(oidnProperties, baked_image_array, dirpath)

            try:
                denoiser.denoise()
            except Exception as e:

                print("An error occured during denoising. See the line below for more detail:")
                print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

                tlm_log.append("An error occured during denoising. See the line below for more detail:")
                tlm_log.append(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

                if not bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                    print("Turn on verbose mode to get more detail.")

            denoiser.clean()

            del denoiser

        else:

            baked_image_array = []

            dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

            for file in dirfiles:
                if file.endswith("_baked.hdr"):
                    baked_image_array.append(file)

            optixProperties = scene.TLM_OptixEngineProperties

            denoiser = optix.TLM_Optix_Denoise(optixProperties, baked_image_array, dirpath)

            denoiser.denoise()

            denoiser.clean()

            del denoiser

    #Filtering
    if sceneProperties.tlm_filtering_use:

        if sceneProperties.tlm_denoise_use:
            useDenoise = True
        else:
            useDenoise = False

        filter = opencv.TLM_CV_Filtering

        try:
            filter.init(dirpath, useDenoise)

        except Exception as e:

            print("An error occured during filtering. See the line below for more detail:")
            print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

            tlm_log.append("An error occured during filtering. See the line below for more detail:")
            tlm_log.append(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

            if not bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                print("Turn on verbose mode to get more detail.")

    #Encoding
    if sceneProperties.tlm_encoding_use and scene.TLM_EngineProperties.tlm_bake_mode != "Background":

        if sceneProperties.tlm_encoding_device == "CPU":

            if sceneProperties.tlm_encoding_mode_a == "HDR":

                if sceneProperties.tlm_format == "EXR":

                    tlm_log.append("EXR Format")
                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        
                        print("EXR Format")

                    ren = bpy.context.scene.render
                    ren.image_settings.file_format = "OPEN_EXR"
                    #ren.image_settings.exr_codec = "scene.TLM_SceneProperties.tlm_exr_codec"

                    end = "_baked"

                    baked_image_array = []

                    if sceneProperties.tlm_denoise_use:

                        end = "_denoised"

                    if sceneProperties.tlm_filtering_use:

                        end = "_filtered"
                    
                    #For each image in folder ending in denoised/filtered
                    dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

                    for file in dirfiles:
                        if file.endswith(end + ".hdr"):

                            img = bpy.data.images.load(os.path.join(dirpath,file))
                            img.save_render(img.filepath_raw[:-4] + ".exr")

            if sceneProperties.tlm_encoding_mode_a == "RGBM":

                tlm_log.append("ENCODING RGBM")
                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                    
                    print("ENCODING RGBM")

                dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

                end = "_baked"

                if sceneProperties.tlm_denoise_use:

                    end = "_denoised"

                if sceneProperties.tlm_filtering_use:

                    end = "_filtered"

                for file in dirfiles:
                    if file.endswith(end + ".hdr"):

                        img = bpy.data.images.load(os.path.join(dirpath, file), check_existing=False)
                        
                        tlm_log.append("Encoding:" + str(file))
                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                            print("Encoding:" + str(file))
                        encoding.encodeImageRGBMCPU(img, sceneProperties.tlm_encoding_range, dirpath, 0)

            if sceneProperties.tlm_encoding_mode_a == "RGBD":

                tlm_log.append("ENCODING RGBD")
                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                    
                    print("ENCODING RGBD")

                dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

                end = "_baked"

                if sceneProperties.tlm_denoise_use:

                    end = "_denoised"

                if sceneProperties.tlm_filtering_use:

                    end = "_filtered"

                for file in dirfiles:
                    if file.endswith(end + ".hdr"):

                        img = bpy.data.images.load(os.path.join(dirpath, file), check_existing=False)
                        
                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                            tlm_log.append("Encoding:" + str(file))
                            print("Encoding:" + str(file))
                        encoding.encodeImageRGBDCPU(img, sceneProperties.tlm_encoding_range, dirpath, 0)

            if sceneProperties.tlm_encoding_mode_a == "SDR":

                tlm_log.append("EXR Format")
                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                    
                    print("EXR Format")

                ren = bpy.context.scene.render
                ren.image_settings.file_format = "PNG"
                #ren.image_settings.exr_codec = "scene.TLM_SceneProperties.tlm_exr_codec"

                end = "_baked"

                baked_image_array = []

                if sceneProperties.tlm_denoise_use:

                    end = "_denoised"

                if sceneProperties.tlm_filtering_use:

                    end = "_filtered"
                
                #For each image in folder ending in denoised/filtered
                dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

                for file in dirfiles:
                    if file.endswith(end + ".hdr"):

                        img = bpy.data.images.load(os.path.join(dirpath,file))
                        img.save_render(img.filepath_raw[:-4] + ".png")

        else:

            if sceneProperties.tlm_encoding_mode_b == "HDR":

                if sceneProperties.tlm_format == "EXR":

                    tlm_log.append("EXR Format")
                    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                        
                        print("EXR Format")

                    ren = bpy.context.scene.render
                    ren.image_settings.file_format = "OPEN_EXR"
                    #ren.image_settings.exr_codec = "scene.TLM_SceneProperties.tlm_exr_codec"

                    end = "_baked"

                    baked_image_array = []

                    if sceneProperties.tlm_denoise_use:

                        end = "_denoised"

                    if sceneProperties.tlm_filtering_use:

                        end = "_filtered"
                    
                    #For each image in folder ending in denoised/filtered
                    dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

                    for file in dirfiles:
                        if file.endswith(end + ".hdr"):

                            img = bpy.data.images.load(os.path.join(dirpath,file))
                            img.save_render(img.filepath_raw[:-4] + ".exr")

            if sceneProperties.tlm_encoding_mode_b == "LogLuv":

                dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

                end = "_baked"

                if sceneProperties.tlm_denoise_use:

                    end = "_denoised"

                if sceneProperties.tlm_filtering_use:

                    end = "_filtered"

                #CHECK FOR ATLAS MAPS!
                for file in dirfiles:
                    if file.endswith(end + ".hdr"):

                        img = bpy.data.images.load(os.path.join(dirpath, file), check_existing=False)
                        
                        encoding.encodeLogLuvGPU(img, dirpath, 0)

                        if sceneProperties.tlm_split_premultiplied:

                            image_name = img.name

                            if image_name[-4:] == '.exr' or image_name[-4:] == '.hdr':
                                image_name = image_name[:-4]

                            image_name = image_name + '_encoded.png'

                            print("SPLIT PREMULTIPLIED: " + image_name)
                            encoding.splitLogLuvAlpha(os.path.join(dirpath, image_name), dirpath, 0)

            if sceneProperties.tlm_encoding_mode_b == "RGBM":

                tlm_log.append("ENCODING RGBM")
                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                    
                    print("ENCODING RGBM")

                dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

                end = "_baked"

                if sceneProperties.tlm_denoise_use:

                    end = "_denoised"

                if sceneProperties.tlm_filtering_use:

                    end = "_filtered"

                for file in dirfiles:
                    if file.endswith(end + ".hdr"):

                        img = bpy.data.images.load(os.path.join(dirpath, file), check_existing=False)
                        
                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                            print("Encoding:" + str(file))
                        encoding.encodeImageRGBMGPU(img, sceneProperties.tlm_encoding_range, dirpath, 0)

            if sceneProperties.tlm_encoding_mode_b == "RGBD":

                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                    print("ENCODING RGBD")

                dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

                end = "_baked"

                if sceneProperties.tlm_denoise_use:

                    end = "_denoised"

                if sceneProperties.tlm_filtering_use:

                    end = "_filtered"

                for file in dirfiles:
                    if file.endswith(end + ".hdr"):

                        img = bpy.data.images.load(os.path.join(dirpath, file), check_existing=False)
                        
                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                            print("Encoding:" + str(file))
                        encoding.encodeImageRGBDGPU(img, sceneProperties.tlm_encoding_range, dirpath, 0)

            if sceneProperties.tlm_encoding_mode_b == "PNG":

                ren = bpy.context.scene.render
                ren.image_settings.file_format = "PNG"
                #ren.image_settings.exr_codec = "scene.TLM_SceneProperties.tlm_exr_codec"

                end = "_baked"

                baked_image_array = []

                if sceneProperties.tlm_denoise_use:

                    end = "_denoised"

                if sceneProperties.tlm_filtering_use:

                    end = "_filtered"
                
                #For each image in folder ending in denoised/filtered
                dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

                for file in dirfiles:
                    if file.endswith(end + ".hdr"):

                        img = bpy.data.images.load(os.path.join(dirpath,file))
                        img.save_render(img.filepath_raw[:-4] + ".png")

    manage_build()

def manage_build(background_pass=False, load_atlas=0):

    print("Managing build")

    if load_atlas:
        print("Managing in load atlas mode")

    scene = bpy.context.scene
    sceneProperties = scene.TLM_SceneProperties

    if sceneProperties.tlm_lightmap_engine == "Cycles":

        if background_pass:
            print("In background pass")

            try:

                nodes.apply_lightmaps()

            except Exception as e:

                print("An error occured during lightmap application. See the line below for more detail:")
                print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

                tlm_log.append("An error occured during lightmap application. See the line below for more detail:")
                tlm_log.append(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

                if not bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                    print("Turn on verbose mode to get more detail.")


        try:
            nodes.apply_materials(load_atlas) #From here the name is changed...

        except Exception as e:

            print("An error occured during material application. See the line below for more detail:")
            print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

            tlm_log.append("An error occured during material application. See the line below for more detail:")
            tlm_log.append(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

            if not bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                print("Turn on verbose mode to get more detail.")

        end = "_baked"

        if sceneProperties.tlm_denoise_use:

            end = "_denoised"

        if sceneProperties.tlm_filtering_use:

            end = "_filtered"

        formatEnc = ".hdr"
        
        if sceneProperties.tlm_encoding_use and scene.TLM_EngineProperties.tlm_bake_mode != "Background":

            if sceneProperties.tlm_encoding_device == "CPU":

                print("CPU Encoding")

                if sceneProperties.tlm_encoding_mode_a == "HDR":

                    if sceneProperties.tlm_format == "EXR":

                        formatEnc = ".exr"

                if sceneProperties.tlm_encoding_mode_a == "RGBM":

                    formatEnc = "_encoded.png"

                if sceneProperties.tlm_encoding_mode_a == "RGBD":

                    formatEnc = "_encoded.png"

                if sceneProperties.tlm_encoding_mode_a == "SDR":

                    formatEnc = ".png"

            else:

                print("GPU Encoding")

                if sceneProperties.tlm_encoding_mode_b == "HDR":

                    if sceneProperties.tlm_format == "EXR":

                        formatEnc = ".exr"

                if sceneProperties.tlm_encoding_mode_b == "LogLuv":

                    formatEnc = "_encoded.png"

                if sceneProperties.tlm_encoding_mode_b == "RGBM":

                    formatEnc = "_encoded.png"

                if sceneProperties.tlm_encoding_mode_b == "RGBD":

                    formatEnc = "_encoded.png"

                if sceneProperties.tlm_encoding_mode_b == "SDR":

                    formatEnc = ".png"

        if not background_pass:
            nodes.exchangeLightmapsToPostfix("_baked", end, formatEnc)

        if scene.TLM_EngineProperties.tlm_setting_supersample == "2x":
            supersampling_scale = 2
        elif scene.TLM_EngineProperties.tlm_setting_supersample == "4x":
            supersampling_scale = 4
        else:
            supersampling_scale = 1

        pack.postpack()
        #We need to also make sure out postpacked atlases gets split w. premultiplied
        #CHECK FOR ATLAS MAPS!

        if bpy.context.scene.TLM_SceneProperties.tlm_split_premultiplied:

            dirpath = os.path.join(os.path.dirname(bpy.data.filepath), scene.TLM_EngineProperties.tlm_lightmap_savedir)
            dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

            for atlas in bpy.context.scene.TLM_PostAtlasList:

                for file in dirfiles:
                    if file.startswith(atlas.name):

                        print("TODO: SPLIT LOGLUV FOR: " + str(file))
                        encoding.splitLogLuvAlpha(os.path.join(dirpath, file), dirpath, 0)

            #Need to update file list for some reason?
            dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

            for atlas in bpy.context.scene.TLM_PostAtlasList:

                #FIND SOME WAY TO FIND THE RIGTH FILE! TOO TIRED NOW!
                for obj in bpy.context.scene.objects:
                    if obj.TLM_ObjectProperties.tlm_postpack_object:
                        if obj.TLM_ObjectProperties.tlm_postatlas_pointer == atlas.name:
                            for slot in obj.material_slots:
                            
                                mat = slot.material

                                node_tree = mat.node_tree

                                foundBakedNode = False

                                #for file in dirfiles:
                                #    if file.startswith(atlas.name):
                                #        if file.endswith("XYZ"):

                                #Find nodes
                                for node in node_tree.nodes:

                                    if node.name == "TLM_Lightmap":

                                        print("Found the main lightmap node: LOGLUV")

                                        for file in dirfiles:
                                            if file.startswith(atlas.name) and file.endswith("XYZ.png"):
                                                print("Found an atlas file: " + str(file))
                                                node.image.filepath_raw = os.path.join(dirpath, file)
                                                print("CHANGED LIGHTMAP MAIN INTO XYZ: " + str(file))

                                    if node.name == "TLM_Lightmap_Extra":

                                        print("Found the main lightmap node: LOGLUV")

                                        for file in dirfiles:
                                            if file.startswith(atlas.name) and file.endswith("W.png"):
                                                print("Found an atlas file: " + str(file))
                                                node.image.filepath_raw = os.path.join(dirpath, file)
                                                print("CHANGED LIGHTMAP MAIN INTO W: " + str(file))

                                        #print("Found the extra lightmap node: LOGLUV")
                                        # if node.image.filepath_raw.startswith(atlas.name):
                                        #     if node.image.filepath_raw.endswith("W.png"):
                                        #         print("ALREADY W: " + str(node.image.filepath_raw))
                                        
                                        # else:

                                        #     for file in dirfiles:
                                        #         if file.startswith(atlas.name):
                                        #             if file.endswith("W.png"):

                                        #                 node.image.filepath_raw = os.path.join(dirpath, file)
                                        #                 print("CHANGED LIGHTMAP MAIN INTO W: " + str(file))

            #for file in dirfiles:
            #    if file.endswith(end + ".hdr"):

            #for atlas in bpy.context.scene.TLM_PostAtlasList:



                #print("TODO: SPLIT LOGLUV FOR: " + str(atlas.name) + "..file?")

                    #CHECK FOR ATLAS MAPS!
                #dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]
                    # for file in dirfiles:
                    #     if file.endswith(end + ".hdr"):

                    #         img = bpy.data.images.load(os.path.join(dirpath, file), check_existing=False)
                            
                    #         encoding.encodeLogLuvGPU(img, dirpath, 0)

                    #         if sceneProperties.tlm_split_premultiplied:

                    #             image_name = img.name

                    #             if image_name[-4:] == '.exr' or image_name[-4:] == '.hdr':
                    #                 image_name = image_name[:-4]

                    #             image_name = image_name + '_encoded.png'

                    #             print("SPLIT PREMULTIPLIED: " + image_name)
                    #             encoding.splitLogLuvAlpha(os.path.join(dirpath, image_name), dirpath, 0)

        for image in bpy.data.images:
            if image.users < 1:
                bpy.data.images.remove(image)

        if scene.TLM_SceneProperties.tlm_headless:

            filepath = bpy.data.filepath
            dirpath = os.path.join(os.path.dirname(bpy.data.filepath), scene.TLM_EngineProperties.tlm_lightmap_savedir)

            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                        cache.backup_material_restore(obj)

            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                        cache.backup_material_rename(obj)

            for mat in bpy.data.materials:
                if mat.users < 1:
                    bpy.data.materials.remove(mat)

            for mat in bpy.data.materials:
                if mat.name.startswith("."):
                    if "_Original" in mat.name:
                        bpy.data.materials.remove(mat)

            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                        if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":
                            atlasName = obj.TLM_ObjectProperties.tlm_atlas_pointer
                            img_name = atlasName + '_baked'
                            Lightmapimage = bpy.data.images[img_name]
                            obj["Lightmap"] = Lightmapimage.filepath_raw
                        elif obj.TLM_ObjectProperties.tlm_postpack_object:
                            atlasName = obj.TLM_ObjectProperties.tlm_postatlas_pointer
                            img_name = atlasName + '_baked' + ".hdr"
                            Lightmapimage = bpy.data.images[img_name]
                            obj["Lightmap"] = Lightmapimage.filepath_raw
                        else:
                            img_name = obj.name + '_baked'
                            Lightmapimage = bpy.data.images[img_name]
                            obj["Lightmap"] = Lightmapimage.filepath_raw

            for image in bpy.data.images:
                if image.name.endswith("_baked"):
                    bpy.data.images.remove(image, do_unlink=True)

        if "tlm_plus_mode" in bpy.app.driver_namespace: #First DIR pass

            if bpy.app.driver_namespace["tlm_plus_mode"] == 1: #First DIR pass

                filepath = bpy.data.filepath
                dirpath = os.path.join(os.path.dirname(bpy.data.filepath), scene.TLM_EngineProperties.tlm_lightmap_savedir)

                for obj in bpy.context.scene.objects:
                    if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
                        if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                            cache.backup_material_restore(obj)

                for obj in bpy.context.scene.objects:
                    if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
                        if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                            cache.backup_material_rename(obj)

                for mat in bpy.data.materials:
                    if mat.users < 1:
                        bpy.data.materials.remove(mat)

                for mat in bpy.data.materials:
                    if mat.name.startswith("."):
                        if "_Original" in mat.name:
                            bpy.data.materials.remove(mat)

                for image in bpy.data.images:
                    if image.name.endswith("_baked"):
                        bpy.data.images.remove(image, do_unlink=True)

                dirpath = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)

                files = os.listdir(dirpath)

                for index, file in enumerate(files):

                    filename = extension = os.path.splitext(file)[0]
                    extension = os.path.splitext(file)[1]

                    os.rename(os.path.join(dirpath, file), os.path.join(dirpath, filename + "_dir" + extension))
                
                print("First DIR pass complete")

                bpy.app.driver_namespace["tlm_plus_mode"] = 2

                prepare_build(self=0, background_mode=False, shutdown_after_build=False)

                if not background_pass and bpy.context.scene.TLM_EngineProperties.tlm_lighting_mode != "combinedao":
                    #pass
                    setGui(0)

            elif bpy.app.driver_namespace["tlm_plus_mode"] == 2:

                filepath = bpy.data.filepath

                dirpath = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)

                files = os.listdir(dirpath)

                for index, file in enumerate(files):

                    filename = os.path.splitext(file)[0]
                    extension = os.path.splitext(file)[1]

                    if not filename.endswith("_dir"):
                        os.rename(os.path.join(dirpath, file), os.path.join(dirpath, filename + "_ao" + extension))
                
                print("Second AO pass complete")

                total_time = sec_to_hours((time() - start_time))
                tlm_log.append(total_time)
                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                    
                    print(total_time)

                bpy.context.scene["TLM_Buildstat"] = total_time

                reset_settings(previous_settings["settings"])

                bpy.app.driver_namespace["tlm_plus_mode"] = 0

                if not background_pass:

                    #TODO CHANGE!

                    nodes.exchangeLightmapsToPostfix(end, end + "_dir", formatEnc)

                    nodes.applyAOPass()

        else:

            total_time = sec_to_hours((time() - start_time))
            tlm_log.append(total_time)
            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                print(total_time)

            bpy.context.scene["TLM_Buildstat"] = total_time

            reset_settings(previous_settings["settings"])

            tlm_log.append("Lightmap building finished")
            tlm_log.append("--------------------------")
            print("Lightmap building finished")

            if sceneProperties.tlm_lightmap_engine == "LuxCoreRender":

                pass

            if sceneProperties.tlm_lightmap_engine == "OctaneRender":

                pass

            if bpy.context.scene.TLM_EngineProperties.tlm_bake_mode == "Background":
                pass

            if not background_pass and scene.TLM_EngineProperties.tlm_bake_mode != "Background" and bpy.context.scene.TLM_EngineProperties.tlm_lighting_mode != "combinedao":
                #pass
                setGui(0)

        if scene.TLM_SceneProperties.tlm_alert_on_finish:

            alertSelect = scene.TLM_SceneProperties.tlm_alert_sound

            if alertSelect == "dash":
                soundfile = "dash.ogg"
            elif alertSelect == "pingping":
                soundfile = "pingping.ogg"  
            elif alertSelect == "gentle":
                soundfile = "gentle.ogg"
            else:
                soundfile = "noot.ogg"

            scriptDir = os.path.dirname(os.path.realpath(__file__))
            sound_path = os.path.abspath(os.path.join(scriptDir, '..', 'assets/'+soundfile))

            device = aud.Device()
            sound = aud.Sound.file(sound_path)
            device.play(sound)

        if logging:
            print("Log file output:")
            tlm_log.dumpLog()

        if bpy.app.background:

            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                print("Writing background process report")
            
            write_directory = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)

            if os.path.exists(os.path.join(write_directory, "process.tlm")):

                process_status = json.loads(open(os.path.join(write_directory, "process.tlm")).read())

                process_status[1]["completed"] = True

                with open(os.path.join(write_directory, "process.tlm"), 'w') as file:
                    json.dump(process_status, file, indent=2)

            if postprocess_shutdown:
                sys.exit()

#TODO - SET BELOW TO UTILITY

def reset_settings(prev_settings):
    scene = bpy.context.scene
    cycles = scene.cycles

    cycles.samples = int(prev_settings[0])
    cycles.max_bounces = int(prev_settings[1])
    cycles.diffuse_bounces = int(prev_settings[2])
    cycles.glossy_bounces = int(prev_settings[3])
    cycles.transparent_max_bounces = int(prev_settings[4])
    cycles.transmission_bounces = int(prev_settings[5])
    cycles.volume_bounces = int(prev_settings[6])
    cycles.caustics_reflective = prev_settings[7]
    cycles.caustics_refractive = prev_settings[8]
    cycles.device = prev_settings[9]
    scene.render.engine = prev_settings[10]
    bpy.context.view_layer.objects.active = prev_settings[11]
    scene.render.resolution_x = prev_settings[13][0]
    scene.render.resolution_y = prev_settings[13][1]
    
    #for obj in prev_settings[12]:
    #    obj.select_set(True)

def naming_check():

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:

            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                if obj.name != "":

                    if "_" in obj.name:
                        obj.name = obj.name.replace("_",".")
                    if " " in obj.name:
                        obj.name = obj.name.replace(" ",".")
                    if "[" in obj.name:
                        obj.name = obj.name.replace("[",".")
                    if "]" in obj.name:
                        obj.name = obj.name.replace("]",".")
                    if "ø" in obj.name:
                        obj.name = obj.name.replace("ø","oe")
                    if "æ" in obj.name:
                        obj.name = obj.name.replace("æ","ae")
                    if "å" in obj.name:
                        obj.name = obj.name.replace("å","aa")
                    if "/" in obj.name:
                        obj.name = obj.name.replace("/",".")

                    for slot in obj.material_slots:
                        if "_" in slot.material.name:
                            slot.material.name = slot.material.name.replace("_",".")
                        if " " in slot.material.name:
                            slot.material.name = slot.material.name.replace(" ",".")
                        if "[" in slot.material.name:
                            slot.material.name = slot.material.name.replace("[",".")
                        if "[" in slot.material.name:
                            slot.material.name = slot.material.name.replace("]",".")
                        if "ø" in slot.material.name:
                            slot.material.name = slot.material.name.replace("ø","oe")
                        if "æ" in slot.material.name:
                            slot.material.name = slot.material.name.replace("æ","ae")
                        if "å" in slot.material.name:
                            slot.material.name = slot.material.name.replace("å","aa")
                        if "/" in slot.material.name:
                            slot.material.name = slot.material.name.replace("/",".")

def opencv_check():

    cv2 = util.find_spec("cv2")

    if cv2 is not None:
        return 0
    else:
        return 1

def check_save():
    if not bpy.data.is_saved:

        return 1

    else:

        return 0

def check_denoiser():

    if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
        print("Checking denoiser path")

    scene = bpy.context.scene

    if scene.TLM_SceneProperties.tlm_denoise_use:

        if scene.TLM_SceneProperties.tlm_denoise_engine == "OIDN":

            oidnPath = scene.TLM_OIDNEngineProperties.tlm_oidn_path

            if scene.TLM_OIDNEngineProperties.tlm_oidn_path == "":
                return 1

            if platform.system() == "Windows":
                if not scene.TLM_OIDNEngineProperties.tlm_oidn_path.endswith(".exe"):
                    return 1
                else:
                    if os.path.isfile(bpy.path.abspath(scene.TLM_OIDNEngineProperties.tlm_oidn_path)):
                        return 0
                    else:
                        return 1
            else:
                return 0

def check_materials():
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name in bpy.context.view_layer.objects:
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                for slot in obj.material_slots:
                    mat = slot.material

                    if mat is None:
                        if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                            print("MatNone")
                        mat = bpy.data.materials.new(name="Material")
                        mat.use_nodes = True
                        slot.material = mat

                    nodes = mat.node_tree.nodes

                    #TODO FINISH MATERIAL CHECK -> Nodes check
                    #Afterwards, redo build/utility

def sec_to_hours(seconds):
    a=str(seconds//3600)
    b=str((seconds%3600)//60)
    c=str(round((seconds%3600)%60,1))
    d=["{} hours {} mins {} seconds".format(a, b, c)]
    return d

def setMode():

    obj = bpy.context.scene.objects[0]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    hidden = False

    if obj.hide_get():
        hidden = True
    if obj.hide_viewport:
        hidden = True
    if obj.hide_render:
        hidden = True

    if not hidden:
        bpy.ops.object.mode_set(mode='OBJECT')

    #TODO Make some checks that returns to previous selection

def setGui(mode):

    if mode == 0:

        context = bpy.context
        driver = bpy.app.driver_namespace

        if "TLM_UI" in driver:
            driver["TLM_UI"].remove_handle()

    if mode == 1:

        #bpy.context.area.tag_redraw()
        context = bpy.context
        driver = bpy.app.driver_namespace
        driver["TLM_UI"] = Viewport.ViewportDraw(context, "Building Lightmaps")

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

def checkAtlasSize():

    overflow = False

    scene = bpy.context.scene

    if scene.TLM_EngineProperties.tlm_setting_supersample == "2x":
        supersampling_scale = 2
    elif scene.TLM_EngineProperties.tlm_setting_supersample == "4x":
        supersampling_scale = 4
    else:
        supersampling_scale = 1

    for atlas in bpy.context.scene.TLM_PostAtlasList:

        atlas_resolution = int(int(atlas.tlm_atlas_lightmap_resolution) / int(scene.TLM_EngineProperties.tlm_resolution_scale) * int(supersampling_scale))

        utilized = 0
        atlasUsedArea = 0

        for obj in bpy.context.scene.objects:
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                if obj.TLM_ObjectProperties.tlm_postpack_object:
                    if obj.TLM_ObjectProperties.tlm_postatlas_pointer == atlas.name:
                        
                        atlasUsedArea += int(obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution) ** 2

        utilized = atlasUsedArea / (int(atlas_resolution) ** 2)
        if (utilized * 100) > 100:
            overflow = True
            print("Overflow for: " + str(atlas.name))

    if overflow == True:
        return True
    else:
        return False

