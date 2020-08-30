import bpy, os, platform, subprocess

class TLM_Optix_Denoise:

    image_array = []

    image_output_destination = ""

    denoised_array = []

    def __init__(self, optixProperties, img_array, dirpath):

        self.optixProperties = optixProperties

        self.image_array = img_array

        self.image_output_destination = dirpath

        self.check_binary()

    def check_binary(self):

        optixPath = self.optixProperties.tlm_optix_path

        if optixPath != "":

            file = os.path.basename(os.path.realpath(optixPath))
            filename, file_extension = os.path.splitext(file)

            if(file_extension == ".exe"):

                #if file exists optixDenoise or denoise

                pass

            else:

                #if file exists optixDenoise or denoise

                self.optixProperties.tlm_optix_path = os.path.join(self.optixProperties.tlm_optix_path,"Denoiser.exe")

        else:

            print("Please provide Optix path")

    def denoise(self):

        print("Optix: Denoising")
        for image in self.image_array:

            if image not in self.denoised_array:

                image_path = os.path.join(self.image_output_destination, image)

                denoise_output_destination = image_path[:-10] + "_denoised.hdr"

                if platform.system() == 'Windows':
                    optixPath = bpy.path.abspath(self.optixProperties.tlm_optix_path)
                    pipePath = [optixPath, '-i', image_path, '-o', denoise_output_destination]
                elif platform.system() == 'Darwin':
                    print("Mac for Optix is still unsupported")    
                else:
                    print("Linux for Optix is still unsupported")

                if self.optixProperties.tlm_optix_verbose:
                    denoisePipe = subprocess.Popen(pipePath, shell=True)
                else:
                    denoisePipe = subprocess.Popen(pipePath, stdout=subprocess.PIPE, stderr=None, shell=True)

                denoisePipe.communicate()[0]
                
                image = bpy.data.images.load(image_path, check_existing=False)
                bpy.data.images[image.name].filepath_raw = bpy.data.images[image.name].filepath_raw[:-4] + "_denoised.hdr"
                bpy.data.images[image.name].reload()

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