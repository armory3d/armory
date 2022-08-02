import bpy, os, sys, re, platform, subprocess
import numpy as np

class TLM_OIDN_Denoise:

    image_array = []

    image_output_destination = ""

    denoised_array = []

    def __init__(self, oidnProperties, img_array, dirpath):

        self.oidnProperties = oidnProperties

        self.image_array = img_array

        self.image_output_destination = dirpath

        self.check_binary()

    def check_binary(self):

        oidnPath = self.oidnProperties.tlm_oidn_path

        if oidnPath != "":

            file = os.path.basename(os.path.realpath(oidnPath))
            filename, file_extension = os.path.splitext(file)
            
            
            if platform.system() == 'Windows':
            
                if(file_extension == ".exe"):
                
                    pass
                    
                else:
                
                    self.oidnProperties.tlm_oidn_path = os.path.join(self.oidnProperties.tlm_oidn_path,"oidnDenoise.exe")

        else:

            if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                print("Please provide OIDN path")

    def denoise(self):

        for image in self.image_array:

            if image not in self.denoised_array:

                image_path = os.path.join(self.image_output_destination, image)

                #Save to pfm
                loaded_image = bpy.data.images.load(image_path, check_existing=False)

                width = loaded_image.size[0]
                height = loaded_image.size[1]

                image_output_array = np.zeros([width, height, 3], dtype="float32")
                image_output_array = np.array(loaded_image.pixels)
                image_output_array = image_output_array.reshape(height, width, 4)
                image_output_array = np.float32(image_output_array[:,:,:3])

                image_output_denoise_destination = image_path[:-4] + ".pfm"

                image_output_denoise_result_destination = image_path[:-4] + "_denoised.pfm"

                with open(image_output_denoise_destination, "wb") as fileWritePFM:
                    self.save_pfm(fileWritePFM, image_output_array)

                #Denoise
                if bpy.context.scene.TLM_SceneProperties.tlm_verbose:
                    print("Loaded image: " + str(loaded_image))

                verbose = self.oidnProperties.tlm_oidn_verbose
                affinity = self.oidnProperties.tlm_oidn_affinity

                if verbose:
                    print("Denoiser search: " + bpy.path.abspath(self.oidnProperties.tlm_oidn_path))
                    v = "3"
                else:
                    v = "0"

                if affinity:
                    a = "1"
                else:
                    a = "0"

                threads = str(self.oidnProperties.tlm_oidn_threads)
                maxmem = str(self.oidnProperties.tlm_oidn_maxmem)

                if platform.system() == 'Windows':
                    oidnPath = bpy.path.abspath(self.oidnProperties.tlm_oidn_path)
                    pipePath = [oidnPath, '-f', 'RTLightmap', '-hdr', image_output_denoise_destination, '-o', image_output_denoise_result_destination, '-verbose', v, '-threads', threads, '-affinity', a, '-maxmem', maxmem]
                elif platform.system() == 'Darwin':
                    oidnPath = bpy.path.abspath(self.oidnProperties.tlm_oidn_path)
                    pipePath = [oidnPath + ' -f ' + ' RTLightmap ' + ' -hdr ' + image_output_denoise_destination + ' -o ' + image_output_denoise_result_destination + ' -verbose ' + v]
                else:
                    oidnPath = bpy.path.abspath(self.oidnProperties.tlm_oidn_path)
                    oidnPath = oidnPath.replace(' ', '\\ ')
                    image_output_denoise_destination = image_output_denoise_destination.replace(' ', '\\ ')
                    image_output_denoise_result_destination = image_output_denoise_result_destination.replace(' ', '\\ ')
                    pipePath = [oidnPath + ' -f ' + ' RTLightmap ' + ' -hdr ' + image_output_denoise_destination + ' -o ' + image_output_denoise_result_destination + ' -verbose ' + v]
                    
                if not verbose:
                    denoisePipe = subprocess.Popen(pipePath, stdout=subprocess.PIPE, stderr=None, shell=True)
                else:
                    denoisePipe = subprocess.Popen(pipePath, shell=True)

                denoisePipe.communicate()[0]

                if platform.system() != 'Windows':
                    image_output_denoise_result_destination = image_output_denoise_result_destination.replace('\\', '')

                with open(image_output_denoise_result_destination, "rb") as f:
                    denoise_data, scale = self.load_pfm(f)

                ndata = np.array(denoise_data)
                ndata2 = np.dstack((ndata, np.ones((width,height))))
                img_array = ndata2.ravel()

                loaded_image.pixels = img_array
                loaded_image.filepath_raw = image_output_denoise_result_destination = image_path[:-10] + "_denoised.hdr"
                loaded_image.file_format = "HDR"
                loaded_image.save()

                self.denoised_array.append(image)

                print(image_path)

    def clean(self):

        self.denoised_array.clear()
        self.image_array.clear()

        for file in self.image_output_destination:
                if file.endswith("_baked.hdr"):
                    baked_image_array.append(file)

        #self.image_output_destination

        #Clean temporary files here..
        #...pfm
        #...denoised.hdr


    def load_pfm(self, file, as_flat_list=False):
        #start = time()

        header = file.readline().decode("utf-8").rstrip()
        if header == "PF":
            color = True
        elif header == "Pf":
            color = False
        else:
            raise Exception("Not a PFM file.")

        dim_match = re.match(r"^(\d+)\s(\d+)\s$", file.readline().decode("utf-8"))
        if dim_match:
            width, height = map(int, dim_match.groups())
        else:
            raise Exception("Malformed PFM header.")

        scale = float(file.readline().decode("utf-8").rstrip())
        if scale < 0:  # little-endian
            endian = "<"
            scale = -scale
        else:
            endian = ">"  # big-endian

        data = np.fromfile(file, endian + "f")
        shape = (height, width, 3) if color else (height, width)
        if as_flat_list:
            result = data
        else:
            result = np.reshape(data, shape)
        #print("PFM import took %.3f s" % (time() - start))
        return result, scale

    def save_pfm(self, file, image, scale=1):
        #start = time()

        if image.dtype.name != "float32":
            raise Exception("Image dtype must be float32 (got %s)" % image.dtype.name)

        if len(image.shape) == 3 and image.shape[2] == 3:  # color image
            color = True
        elif len(image.shape) == 2 or len(image.shape) == 3 and image.shape[2] == 1:  # greyscale
            color = False
        else:
            raise Exception("Image must have H x W x 3, H x W x 1 or H x W dimensions.")

        file.write(b"PF\n" if color else b"Pf\n")
        file.write(b"%d %d\n" % (image.shape[1], image.shape[0]))

        endian = image.dtype.byteorder

        if endian == "<" or endian == "=" and sys.byteorder == "little":
            scale = -scale

        file.write(b"%f\n" % scale)

        image.tofile(file)

        #print("PFM export took %.3f s" % (time() - start))
