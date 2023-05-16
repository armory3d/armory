import bpy, os, sys, math, mathutils, importlib
import numpy as np
from . rectpack import newPacker, PackingMode, PackingBin

def postpack():

    cv_installed = False

    cv2 = importlib.util.find_spec("cv2")

    if cv2 is None:
        print("CV2 not found - Ignoring postpacking")
        return 0
    else:
        cv2 = importlib.__import__("cv2")
        cv_installed = True

    if cv_installed:

        lightmap_directory = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)

        packedAtlas = {}

        #TODO - TEST WITH ONLY 1 ATLAS AT FIRST (1 Atlas for each, but only 1 bin (no overflow))
        #PackedAtlas = Packer
        #Each atlas has bins
        #Each bins has rects
        #Each rect corresponds to a pack_object

        scene = bpy.context.scene
        
        sceneProperties = scene.TLM_SceneProperties

        end = "_baked"

        if sceneProperties.tlm_denoise_use:

            end = "_denoised"

        if sceneProperties.tlm_filtering_use:

            end = "_filtered"

        formatEnc = ".hdr"

        image_channel_depth = cv2.IMREAD_ANYDEPTH
        linear_straight = False
        
        if sceneProperties.tlm_encoding_use and scene.TLM_EngineProperties.tlm_bake_mode != "Background":

            if sceneProperties.tlm_encoding_device == "CPU":

                if sceneProperties.tlm_encoding_mode_a == "HDR":

                    if sceneProperties.tlm_format == "EXR":

                        formatEnc = ".exr"

                if sceneProperties.tlm_encoding_mode_a == "RGBM":

                    formatEnc = "_encoded.png"
                    image_channel_depth = cv2.IMREAD_UNCHANGED

            else:

                if sceneProperties.tlm_encoding_mode_b == "HDR":

                    if sceneProperties.tlm_format == "EXR":

                        formatEnc = ".exr"

                if sceneProperties.tlm_encoding_mode_b == "LogLuv":

                    formatEnc = "_encoded.png"
                    image_channel_depth = cv2.IMREAD_UNCHANGED
                    linear_straight = True

                if sceneProperties.tlm_encoding_mode_b == "RGBM":

                    formatEnc = "_encoded.png"
                    image_channel_depth = cv2.IMREAD_UNCHANGED

                if sceneProperties.tlm_encoding_mode_b == "RGBD":

                    formatEnc = "_encoded.png"
                    image_channel_depth = cv2.IMREAD_UNCHANGED

        packer = {}

        for atlas in bpy.context.scene.TLM_PostAtlasList: #For each atlas

            packer[atlas.name] = newPacker(PackingMode.Offline, PackingBin.BFF, rotation=False)

            bpy.app.driver_namespace["logman"].append("Postpacking: " + str(atlas.name))

            if scene.TLM_EngineProperties.tlm_setting_supersample == "2x":
                supersampling_scale = 2
            elif scene.TLM_EngineProperties.tlm_setting_supersample == "4x":
                supersampling_scale = 4
            else:
                supersampling_scale = 1

            atlas_resolution = int(int(atlas.tlm_atlas_lightmap_resolution) / int(scene.TLM_EngineProperties.tlm_resolution_scale) * int(supersampling_scale))

            packer[atlas.name].add_bin(atlas_resolution, atlas_resolution, 1)

            #AtlasList same name prevention?
            rect = []

            #For each object that targets the atlas
            for obj in bpy.context.scene.objects:
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    if obj.TLM_ObjectProperties.tlm_postpack_object:
                        if obj.TLM_ObjectProperties.tlm_postatlas_pointer == atlas.name:

                            res = int(int(obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution) / int(scene.TLM_EngineProperties.tlm_resolution_scale) * int(supersampling_scale))

                            rect.append((res, res, obj.name))

            #Add rect to bin
            for r in rect:
                packer[atlas.name].add_rect(*r)

            print("Rects: " + str(rect))
            print("Bins:" + str(packer[atlas.name]))

            packedAtlas[atlas.name] = np.zeros((atlas_resolution,atlas_resolution, 3), dtype="float32")

            #Continue here...overwrite value if using 8-bit encoding
            if sceneProperties.tlm_encoding_use:
                if sceneProperties.tlm_encoding_device == "CPU":
                    if sceneProperties.tlm_encoding_mode_a == "RGBM":
                        packedAtlas[atlas.name] = np.zeros((atlas_resolution,atlas_resolution, 4), dtype=np.uint8)
                    if sceneProperties.tlm_encoding_mode_a == "RGBD":
                        packedAtlas[atlas.name] = np.zeros((atlas_resolution,atlas_resolution, 4), dtype=np.uint8)
                
                if sceneProperties.tlm_encoding_device == "GPU":
                    if sceneProperties.tlm_encoding_mode_b == "RGBM":
                        packedAtlas[atlas.name] = np.zeros((atlas_resolution,atlas_resolution, 4), dtype=np.uint8)
                    if sceneProperties.tlm_encoding_mode_b == "RGBD":
                        packedAtlas[atlas.name] = np.zeros((atlas_resolution,atlas_resolution, 4), dtype=np.uint8)
                    if sceneProperties.tlm_encoding_mode_b == "LogLuv":
                        packedAtlas[atlas.name] = np.zeros((atlas_resolution,atlas_resolution, 4), dtype=np.uint8)

            packer[atlas.name].pack()

            for idy, rect in enumerate(packer[atlas.name].rect_list()):

                print("Packing atlas at: " + str(rect))

                aob = rect[5]

                src = cv2.imread(os.path.join(lightmap_directory, aob + end + formatEnc), image_channel_depth) #"_baked.hdr"

                print("Obj name is: " + aob)

                x,y,w,h = rect[1],rect[2],rect[3],rect[4]

                print("Obj Shape: " + str(src.shape))
                print("Atlas shape: " + str(packedAtlas[atlas.name].shape))

                print("Bin Pos: ",x,y,w,h)
                

                packedAtlas[atlas.name][y:h+y, x:w+x] = src
                
                obj = bpy.data.objects[aob]

                for idx, layer in enumerate(obj.data.uv_layers):

                    if not obj.TLM_ObjectProperties.tlm_use_default_channel:
                        uv_channel = obj.TLM_ObjectProperties.tlm_uv_channel
                    else:
                        uv_channel = "UVMap_Lightmap"

                    if layer.name == uv_channel:
                        obj.data.uv_layers.active_index = idx

                        print("UVLayer set to: " + str(obj.data.uv_layers.active_index))

                atlasRes = atlas_resolution
                texRes = rect[3] #Any dimension w/h (square)
                ratio = texRes/atlasRes
                scaleUV(obj.data.uv_layers.active, (ratio, ratio), (0,1))
                print(rect)
                
                #Postpack error here...
                for uv_verts in obj.data.uv_layers.active.data:
                    #For each vert

                    #NOTES! => X FUNKER
                    #TODO => Y

                    #[0] = bin index
                    #[1] = x
                    #[2] = y (? + 1)
                    #[3] = w
                    #[4] = h

                    vertex_x = uv_verts.uv[0] + (rect[1]/atlasRes) #WORKING!
                    vertex_y = uv_verts.uv[1] - (rect[2]/atlasRes) # + ((rect[2]-rect[4])/atlasRes) #            #         + (1-((rect[1]-rect[4])/atlasRes))
                    #tr = "X: {0} + ({1}/{2})".format(uv_verts.uv[0],rect[1],atlasRes)
                    #print(tr)
                    #vertex_y = 1 - (uv_verts.uv[1]) uv_verts.uv[1] + (rect[1]/atlasRes)

                    #SET UV LAYER TO 

                    # atlasRes = atlas_resolution
                    # texRes = rect[3] #Any dimension w/h (square)
                    # print(texRes)
                    # #texRes = 0.0,0.0
                    # #x,y,w,z = x,y,texRes,texRes
                    # x,y,w,z = x,y,0,0
                    
                    # ratio = atlasRes/texRes
                    
                    # if x == 0:
                    #     x_offset = 0
                    # else:
                    #     x_offset = 1/(atlasRes/x)

                    # if y == 0:
                    #     y_offset = 0
                    # else:
                    #     y_offset = 1/(atlasRes/y)
                    
                    # vertex_x = (uv_verts.uv[0] * 1/(ratio)) + x_offset
                    # vertex_y = (1 - ((uv_verts.uv[1] * 1/(ratio)) + y_offset))

                    #TO FIX:
                    #SELECT ALL
                    #Scale Y => -1
                    
                    uv_verts.uv[0] = vertex_x
                    uv_verts.uv[1] = vertex_y

                #scaleUV(obj.data.uv_layers.active, (1, -1), getBoundsCenter(obj.data.uv_layers.active))
                #print(getCenter(obj.data.uv_layers.active))

            cv2.imwrite(os.path.join(lightmap_directory, atlas.name + end + formatEnc), packedAtlas[atlas.name])
            print("Written: " + str(os.path.join(lightmap_directory, atlas.name + end + formatEnc)))

            #Change the material for each material, slot
            for obj in bpy.context.scene.objects:
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    if obj.TLM_ObjectProperties.tlm_postpack_object:
                        if obj.TLM_ObjectProperties.tlm_postatlas_pointer == atlas.name:
                            for slot in obj.material_slots:
                                nodetree = slot.material.node_tree

                                for node in nodetree.nodes:

                                    if node.name == "TLM_Lightmap":

                                        existing_image = node.image

                                        atlasImage = bpy.data.images.load(os.path.join(lightmap_directory, atlas.name + end + formatEnc), check_existing=True)

                                        if linear_straight:
                                            if atlasImage.colorspace_settings.name != 'Linear':
                                                atlasImage.colorspace_settings.name = 'Linear'

                                        node.image = atlasImage

                                        #print("Seeking for: " + atlasImage.filepath_raw)
                                        #print(x)

                                        if(os.path.exists(os.path.join(lightmap_directory, obj.name + end + formatEnc))):
                                            os.remove(os.path.join(lightmap_directory, obj.name + end + formatEnc))
                                            existing_image.user_clear()

            #Add dilation map here...
            for obj in bpy.context.scene.objects:
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    if obj.TLM_ObjectProperties.tlm_postpack_object:
                        if obj.TLM_ObjectProperties.tlm_postatlas_pointer == atlas.name:
                            if atlas.tlm_atlas_dilation:
                                for slot in obj.material_slots:
                                    nodetree = slot.material.node_tree

                                    for node in nodetree.nodes:

                                        if node.name == "TLM_Lightmap":

                                            existing_image = node.image

                                            atlasImage = bpy.data.images.load(os.path.join(lightmap_directory, atlas.name + end + formatEnc), check_existing=True)

                                            img = cv2.imread(atlasImage.filepath_raw, image_channel_depth)

                                            kernel = np.ones((5,5), dtype="float32")

                                            img_dilation = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

                                            cv2.imshow('Dilation', img_dilation)
                                            cv2.waitKey(0)
                                            
                                            print("TODO: Adding dilation for: " + obj.name)
                                            #TODO MASKING OPTION!



    else:

        print("OpenCV not installed. Skipping postpacking process.")

def getCenter(uv_layer):

    total_x, total_y = 0,0
    len = 0

    for uv_verts in uv_layer.data:
        total_x += uv_verts.uv[0]
        total_y += uv_verts.uv[1]

        len += 1 

    center_x = total_x / len
    center_y = total_y / len

    return (center_x, center_y)

def getBoundsCenter(uv_layer):

    min_x = getCenter(uv_layer)[0]
    max_x = getCenter(uv_layer)[0]
    min_y = getCenter(uv_layer)[1]
    max_y = getCenter(uv_layer)[1]

    len = 0

    for uv_verts in uv_layer.data:

        if uv_verts.uv[0] < min_x:
            min_x = uv_verts.uv[0]
        if uv_verts.uv[0] > max_x:
            max_x = uv_verts.uv[0]
        if uv_verts.uv[1] < min_y:
            min_y = uv_verts.uv[1]
        if uv_verts.uv[1] > max_y:
            max_y = uv_verts.uv[1]

    center_x = (max_x - min_x) / 2 + min_x
    center_y = (max_y - min_y) / 2 + min_y

    return (center_x, center_y)


def scale2D(v, s, p):
    return (p[0] + s[0]*(v[0] - p[0]), p[1] + s[1]*(v[1] - p[1]))

def scaleUV( uvMap, scale, pivot ):
    for uvIndex in range( len(uvMap.data) ):
        uvMap.data[uvIndex].uv = scale2D(uvMap.data[uvIndex].uv, scale, pivot)