import bpy, math, os, gpu, bgl
import numpy as np
from . import utility
from fractions import Fraction
from gpu_extras.batch import batch_for_shader

def encodeLogLuv(image, outDir, quality):
    input_image = bpy.data.images[image.name]
    image_name = input_image.name

    offscreen = gpu.types.GPUOffScreen(input_image.size[0], input_image.size[1])

    image = input_image

    vertex_shader = '''

        uniform mat4 ModelViewProjectionMatrix;

        in vec2 texCoord;
        in vec2 pos;
        out vec2 texCoord_interp;

        void main()
        {
        //gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f);
        //gl_Position.z = 1.0;
        gl_Position = vec4(pos.xy, 100, 100);
        texCoord_interp = texCoord;
        }

    '''
    fragment_shader = '''
        in vec2 texCoord_interp;
        out vec4 fragColor;

        uniform sampler2D image;
        
        const mat3 cLogLuvM = mat3( 0.2209, 0.3390, 0.4184, 0.1138, 0.6780, 0.7319, 0.0102, 0.1130, 0.2969 );
        vec4 LinearToLogLuv( in vec4 value )  {
            vec3 Xp_Y_XYZp = cLogLuvM * value.rgb;
            Xp_Y_XYZp = max( Xp_Y_XYZp, vec3( 1e-6, 1e-6, 1e-6 ) );
            vec4 vResult;
            vResult.xy = Xp_Y_XYZp.xy / Xp_Y_XYZp.z;
            float Le = 2.0 * log2(Xp_Y_XYZp.y) + 127.0;
            vResult.w = fract( Le );
            vResult.z = ( Le - ( floor( vResult.w * 255.0 ) ) / 255.0 ) / 255.0;
            return vResult;
            //return vec4(Xp_Y_XYZp,1);
        }
        
        const mat3 cLogLuvInverseM = mat3( 6.0014, -2.7008, -1.7996, -1.3320, 3.1029, -5.7721, 0.3008, -1.0882, 5.6268 );
        vec4 LogLuvToLinear( in vec4 value ) {
            float Le = value.z * 255.0 + value.w;
            vec3 Xp_Y_XYZp;
            Xp_Y_XYZp.y = exp2( ( Le - 127.0 ) / 2.0 );
            Xp_Y_XYZp.z = Xp_Y_XYZp.y / value.y;
            Xp_Y_XYZp.x = value.x * Xp_Y_XYZp.z;
            vec3 vRGB = cLogLuvInverseM * Xp_Y_XYZp.rgb;
            //return vec4( max( vRGB, 0.0 ), 1.0 );
            return vec4( max( Xp_Y_XYZp, 0.0 ), 1.0 );
        }

        void main()
        {
        //fragColor = LinearToLogLuv(pow(texture(image, texCoord_interp), vec4(0.454)));
        fragColor = LinearToLogLuv(texture(image, texCoord_interp));
        //fragColor = LogLuvToLinear(LinearToLogLuv(texture(image, texCoord_interp)));
        }

    '''

    x_screen = 0
    off_x = -100
    off_y = -100
    y_screen_flip = 0
    sx = 200
    sy = 200

    vertices = (
                (x_screen + off_x, y_screen_flip - off_y), 
                (x_screen + off_x, y_screen_flip - sy - off_y), 
                (x_screen + off_x + sx, y_screen_flip - sy - off_y),
                (x_screen + off_x + sx, y_screen_flip - off_x))

    if input_image.colorspace_settings.name != 'Linear':
        input_image.colorspace_settings.name = 'Linear'

    # Removing .exr or .hdr prefix
    if image_name[-4:] == '.exr' or image_name[-4:] == '.hdr':
        image_name = image_name[:-4]

    target_image = bpy.data.images.get(image_name + '_encoded')
    print(image_name + '_encoded')
    if not target_image:
        target_image = bpy.data.images.new(
                name = image_name + '_encoded',
                width = input_image.size[0],
                height = input_image.size[1],
                alpha = True,
                float_buffer = False
                )

    shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {
            "pos": vertices,
            "texCoord": ((0, 1), (0, 0), (1, 0), (1, 1)),
        },
    )

    if image.gl_load():
        raise Exception()
    
    with offscreen.bind():
        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)

        shader.bind()
        shader.uniform_int("image", 0)
        batch.draw(shader)
        
        buffer = bgl.Buffer(bgl.GL_BYTE, input_image.size[0] * input_image.size[1] * 4)
        bgl.glReadBuffer(bgl.GL_BACK)
        bgl.glReadPixels(0, 0, input_image.size[0], input_image.size[1], bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, buffer)

    offscreen.free()
    
    target_image.pixels = [v / 255 for v in buffer]
    input_image = target_image
    
    #Save LogLuv
    print(input_image.name)
    input_image.filepath_raw = outDir + "/" + input_image.name + ".png"
    #input_image.filepath_raw = outDir + "_encoded.png"
    input_image.file_format = "PNG"
    bpy.context.scene.render.image_settings.quality = quality
    #input_image.save_render(filepath = input_image.filepath_raw, scene = bpy.context.scene)
    input_image.save()
    
    #Todo - Find a way to save
    #bpy.ops.image.save_all_modified()

def encodeImageRGBM(image, maxRange, outDir, quality):
    input_image = bpy.data.images[image.name]
    image_name = input_image.name

    if input_image.colorspace_settings.name != 'Linear':
        input_image.colorspace_settings.name = 'Linear'

    # Removing .exr or .hdr prefix
    if image_name[-4:] == '.exr' or image_name[-4:] == '.hdr':
        image_name = image_name[:-4]

    target_image = bpy.data.images.get(image_name + '_encoded')
    print(image_name + '_encoded')
    if not target_image:
        target_image = bpy.data.images.new(
                name = image_name + '_encoded',
                width = input_image.size[0],
                height = input_image.size[1],
                alpha = True,
                float_buffer = False
                )
    
    num_pixels = len(input_image.pixels)
    result_pixel = list(input_image.pixels)

    for i in range(0,num_pixels,4):
        for j in range(3):
            result_pixel[i+j] *= 1.0 / maxRange;
        result_pixel[i+3] = saturate(max(result_pixel[i], result_pixel[i+1], result_pixel[i+2], 1e-6))
        result_pixel[i+3] = math.ceil(result_pixel[i+3] * 255.0) / 255.0
        for j in range(3):
            result_pixel[i+j] /= result_pixel[i+3]
    
    target_image.pixels = result_pixel
    input_image = target_image
    
    #Save RGBM
    print(input_image.name)
    input_image.filepath_raw = outDir + "/" + input_image.name + ".png"
    input_image.file_format = "PNG"
    bpy.context.scene.render.image_settings.quality = quality
    input_image.save()

    #input_image.save_render(filepath = input_image.filepath_raw, scene = bpy.context.scene)
    # input_image.filepath_raw = outDir + "_encoded.png"
    # input_image.file_format = "PNG"
    # bpy.context.scene.render.image_settings.quality = quality
    # input_image.save_render(filepath = input_image.filepath_raw, scene = bpy.context.scene)
    #input_image.
    #input_image.save()

def saturate(num, floats=True):
    if num < 0:
        num = 0
    elif num > (1 if floats else 255):
        num = (1 if floats else 255)
    return num

def encodeImageRGBD(image, maxRange, outDir, quality):
    input_image = bpy.data.images[image.name]
    image_name = input_image.name

    if input_image.colorspace_settings.name != 'Linear':
        input_image.colorspace_settings.name = 'Linear'

    # Removing .exr or .hdr prefix
    if image_name[-4:] == '.exr' or image_name[-4:] == '.hdr':
        image_name = image_name[:-4]

    target_image = bpy.data.images.get(image_name + '_encoded')
    if not target_image:
        target_image = bpy.data.images.new(
                name = image_name + '_encoded',
                width = input_image.size[0],
                height = input_image.size[1],
                alpha = True,
                float_buffer = False
                )
    
    num_pixels = len(input_image.pixels)
    result_pixel = list(input_image.pixels)

    for i in range(0,num_pixels,4):

        m = utility.saturate(max(result_pixel[i], result_pixel[i+1], result_pixel[i+2], 1e-6))
        d = max(maxRange / m, 1)
        d = utility.saturate(math.floor(d) / 255 )

        result_pixel[i] = result_pixel[i] * d * 255 / maxRange
        result_pixel[i+1] = result_pixel[i+1] * d * 255 / maxRange
        result_pixel[i+2] = result_pixel[i+2] * d * 255 / maxRange
        result_pixel[i+3] = d
    
    target_image.pixels = result_pixel
    
    input_image = target_image

    #Save RGBD
    input_image.filepath_raw = outDir + "_encoded.png"
    input_image.file_format = "PNG"
    bpy.context.scene.render.image_settings.quality = quality
    input_image.save_render(filepath = input_image.filepath_raw, scene = bpy.context.scene)