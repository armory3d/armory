import bpy, os, importlib
from os import listdir
from os.path import isfile, join

class TLM_NP_Filtering:

    image_output_destination = ""

    def init(lightmap_dir, denoise):

        scene = bpy.context.scene

        print("Beginning filtering for files: ")

        if denoise:
            file_ending = "_denoised.hdr"
        else:
            file_ending = "_baked.hdr"

        dirfiles = [f for f in listdir(lightmap_dir) if isfile(join(lightmap_dir, f))]

        for file in dirfiles:

            if denoise:
                file_ending = "_denoised.hdr"
                file_split = 13
            else:
                file_ending = "_baked.hdr"
                file_split = 10

            if file.endswith(file_ending):

                file_input = os.path.join(lightmap_dir, file)
                os.chdir(lightmap_dir)

                #opencv_process_image = cv2.imread(file_input, -1)

                print("Filtering: " + file_input)

                print(os.path.join(lightmap_dir, file))

                if scene.TLM_SceneProperties.tlm_numpy_filtering_mode == "3x3 blur":
                    pass

                #filter_file_output = os.path.join(lightmap_dir, file[:-file_split] + "_filtered.hdr")

                #cv2.imwrite(filter_file_output, opencv_bl_result)

                print("Written to: " + filter_file_output)