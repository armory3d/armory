import bpy, os, importlib, subprocess, sys, threading, platform, aud
from . import encoding
from . cycles import lightmap, prepare, nodes, cache
from . denoiser import integrated, oidn
from . filtering import opencv
from os import listdir
from os.path import isfile, join
from time import time, sleep

previous_settings = {}

def prepare_build(self=0, background_mode=False):

    if bpy.context.scene.TLM_EngineProperties.tlm_bake_mode == "Foreground" or background_mode==True:

        global start_time
        start_time = time()

        scene = bpy.context.scene
        sceneProperties = scene.TLM_SceneProperties

        #We dynamically load the renderer and denoiser, instead of loading something we don't use

        if sceneProperties.tlm_lightmap_engine == "Cycles":

            pass

        if sceneProperties.tlm_lightmap_engine == "LuxCoreRender":

            pass

        if sceneProperties.tlm_lightmap_engine == "OctaneRender":

            pass

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

        ## RENDER DEPENDENCY FROM HERE

        if sceneProperties.tlm_lightmap_engine == "Cycles":

            prepare.init(self, previous_settings)

        if sceneProperties.tlm_lightmap_engine == "LuxCoreRender":

            pass

        if sceneProperties.tlm_lightmap_engine == "OctaneRender":

            pass

        #Renderer - Store settings

        #Renderer - Set settings

        #Renderer - Config objects, lights, world

        begin_build()

    else:

        filepath = bpy.data.filepath

        start_time = time()

        scene = bpy.context.scene
        sceneProperties = scene.TLM_SceneProperties

        #We dynamically load the renderer and denoiser, instead of loading something we don't use

        if sceneProperties.tlm_lightmap_engine == "Cycles":

            pass

        if sceneProperties.tlm_lightmap_engine == "LuxCoreRender":

            pass

        if sceneProperties.tlm_lightmap_engine == "OctaneRender":

            pass

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

        pipe_open([sys.executable,"-b",filepath,"--python-expr",'import bpy; import thelightmapper; thelightmapper.addon.utility.build.prepare_build(0, True);'], finish_assemble)

def finish_assemble():
    pass
    #bpy.ops.wm.revert_mainfile() We cannot use this, as Blender crashes...
    print("Background baking finished")

    scene = bpy.context.scene
    sceneProperties = scene.TLM_SceneProperties

    if sceneProperties.tlm_lightmap_engine == "Cycles":

        prepare.init(previous_settings)

    if sceneProperties.tlm_lightmap_engine == "LuxCoreRender":
        pass

    if sceneProperties.tlm_lightmap_engine == "OctaneRender":
        pass

    manage_build(True)

def pipe_open(args, callback):

    def thread_process(args, callback):
        process = subprocess.Popen(args)
        process.wait()
        callback()
        return
    
    thread = threading.Thread(target=thread_process, args=(args, callback))
    thread.start()
    return thread

def begin_build():

    dirpath = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)

    scene = bpy.context.scene
    sceneProperties = scene.TLM_SceneProperties

    if sceneProperties.tlm_lightmap_engine == "Cycles":

        lightmap.bake()

    if sceneProperties.tlm_lightmap_engine == "LuxCoreRender":
        pass

    if sceneProperties.tlm_lightmap_engine == "OctaneRender":
        pass

    #Denoiser

    if sceneProperties.tlm_denoise_use:

        if sceneProperties.tlm_denoise_engine == "Integrated":

            baked_image_array = []

            dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

            for file in dirfiles:
                if file.endswith("_baked.hdr"):
                    baked_image_array.append(file)

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

            denoiser.denoise()

            denoiser.clean()

            del denoiser

        else:
            pass

    #Filtering
    if sceneProperties.tlm_filtering_use:

        if sceneProperties.tlm_denoise_use:
            useDenoise = True
        else:
            useDenoise = False

        filter = opencv.TLM_CV_Filtering

        filter.init(dirpath, useDenoise)

    if sceneProperties.tlm_encoding_use:

        if sceneProperties.tlm_encoding_mode == "HDR":

            if sceneProperties.tlm_format == "EXR":

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

        if sceneProperties.tlm_encoding_mode == "LogLuv":

            dirfiles = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]

            end = "_baked"

            if sceneProperties.tlm_denoise_use:

                end = "_denoised"

            if sceneProperties.tlm_filtering_use:

                end = "_filtered"

            for file in dirfiles:
                if file.endswith(end + ".hdr"):

                    img = bpy.data.images.load(os.path.join(dirpath, file), check_existing=False)
                    
                    encoding.encodeLogLuv(img, dirpath, 0)

        if sceneProperties.tlm_encoding_mode == "RGBM":

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
                    
                    print("Encoding:" + str(file))
                    encoding.encodeImageRGBM(img, sceneProperties.tlm_encoding_range, dirpath, 0)

    manage_build()

def manage_build(background_pass=False):

    scene = bpy.context.scene
    sceneProperties = scene.TLM_SceneProperties

    if sceneProperties.tlm_lightmap_engine == "Cycles":

        if background_pass:
            nodes.apply_lightmaps()

        nodes.apply_materials() #From here the name is changed...

        end = "_baked"

        if sceneProperties.tlm_denoise_use:

            end = "_denoised"

        if sceneProperties.tlm_filtering_use:

            end = "_filtered"

        formatEnc = ".hdr"
        
        if sceneProperties.tlm_encoding_use:

            if sceneProperties.tlm_encoding_mode == "HDR":

                if sceneProperties.tlm_format == "EXR":

                    formatEnc = ".exr"

            if sceneProperties.tlm_encoding_mode == "LogLuv":

                formatEnc = "_encoded.png"

            if sceneProperties.tlm_encoding_mode == "RGBM":

                formatEnc = "_encoded.png"

        if not background_pass:
            nodes.exchangeLightmapsToPostfix("_baked", end, formatEnc)

    if sceneProperties.tlm_lightmap_engine == "LuxCoreRender":

        pass

    if sceneProperties.tlm_lightmap_engine == "OctaneRender":

        pass

    if bpy.context.scene.TLM_EngineProperties.tlm_bake_mode == "Background":
        pass
        #bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath + "baked") #Crashes Blender

    if scene.TLM_EngineProperties.tlm_setting_supersample == "2x":
        supersampling_scale = 2
    elif scene.TLM_EngineProperties.tlm_setting_supersample == "4x":
        supersampling_scale = 4
    else:
        supersampling_scale = 1

    # for image in bpy.data.images:
    #     if image.name.endswith("_baked"):
    #         resolution = image.size[0]
    #         rescale = resolution / supersampling_scale
    #         image.scale(rescale, rescale)
    #         image.save()

    for image in bpy.data.images:
        if image.users < 1:
            bpy.data.images.remove(image)

    if scene.TLM_SceneProperties.tlm_headless:

        filepath = bpy.data.filepath
        dirpath = os.path.join(os.path.dirname(bpy.data.filepath), scene.TLM_EngineProperties.tlm_lightmap_savedir)

        for obj in bpy.data.objects:
            if obj.type == "MESH":
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    cache.backup_material_restore(obj)

        for obj in bpy.data.objects:
            if obj.type == "MESH":
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    cache.backup_material_rename(obj)

        for mat in bpy.data.materials:
            if mat.users < 1:
                bpy.data.materials.remove(mat)

        for mat in bpy.data.materials:
            if mat.name.startswith("."):
                if "_Original" in mat.name:
                    bpy.data.materials.remove(mat)

        for obj in bpy.data.objects:

            if obj.type == "MESH":
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    img_name = obj.name + '_baked'
                    Lightmapimage = bpy.data.images[img_name]
                    obj["Lightmap"] = Lightmapimage.filepath_raw

        for image in bpy.data.images:
            if image.name.endswith("_baked"):
                bpy.data.images.remove(image, do_unlink=True)

    total_time = sec_to_hours((time() - start_time))
    print(total_time)

    reset_settings(previous_settings["settings"])

    if scene.TLM_SceneProperties.tlm_alert_on_finish:

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        sound_path = os.path.abspath(os.path.join(scriptDir, '..', 'assets/sound.ogg'))

        device = aud.Device()
        sound = aud.Sound.file(sound_path)
        device.play(sound)
        print("ALERT!")

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
    
    #for obj in prev_settings[12]:
    #    obj.select_set(True)

def naming_check():

    for obj in bpy.data.objects:

        if obj.type == "MESH":

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

def opencv_check():

    cv2 = importlib.util.find_spec("cv2")

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
                return 0

    # if scene.TLM_SceneProperties.tlm_denoise_use:
    #     if scene.TLM_SceneProperties.tlm_oidn_path == "":
    #         print("NO DENOISE PATH")
    #         return False
    #     else:
    #         return True
    # else:
    #     return True

def check_materials():
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                for slot in obj.material_slots:
                    mat = slot.material

                    if mat is None:
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
    c=str((seconds%3600)%60)
    d=["{} hours {} mins {} seconds".format(a, b, c)]
    return d