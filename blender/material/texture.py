import log
import os
import armutils
import assets
import material.mat_state as mat_state
import make_state as state
import bpy

def make_texture(image_node, tex_name):
    wrd = bpy.data.worlds['Arm']
    tex = {}
    tex['name'] = tex_name
    tex['file'] = ''
    image = image_node.image
    matname = mat_state.material.name

    if image == None:
        return None

    if image.filepath == '':
        log.warn(matname + '/' + image.name + ' - file path not found')
        return None

    # Reference image name
    tex['file'] = armutils.extract_filename(armutils.safe_assetpath(image.filepath))
    tex['file'] = armutils.safefilename(tex['file'])
    s = tex['file'].rsplit('.', 1)
    
    if len(s) == 1:
        log.warn(matname + '/' + image.name + ' - file extension required for image name')
        return None

    ext = s[1].lower()
    do_convert = ext != 'jpg' and ext != 'png' and ext != 'hdr' # Convert image
    if do_convert:
        tex['file'] = tex['file'].rsplit('.', 1)[0] + '.jpg'
        # log.warn(matname + '/' + image.name + ' - image format is not (jpg/png/hdr), converting to jpg.')

    if image.packed_file != None:
        # Extract packed data
        unpack_path = armutils.get_fp() + '/build/compiled/Assets/unpacked'
        if not os.path.exists(unpack_path):
            os.makedirs(unpack_path)
        unpack_filepath = unpack_path + '/' + tex['file']
        
        if do_convert:
            if not os.path.isfile(unpack_filepath):
                armutils.write_image(image, unpack_filepath)
        
        # Write bytes if size is different or file does not exist yet
        elif os.path.isfile(unpack_filepath) == False or os.path.getsize(unpack_filepath) != image.packed_file.size:
            with open(unpack_filepath, 'wb') as f:
                f.write(image.packed_file.data)

        assets.add(unpack_filepath)

    else:
        if not os.path.isfile(image.filepath):
            log.warn(matname + '/' + image.name + ' - file not found')
            return None

        if do_convert:
            converted_path = armutils.get_fp() + '/build/compiled/Assets/unpacked/' + tex['file']
            # TODO: delete cache when file changes
            if not os.path.isfile(converted_path):
                armutils.write_image(image, converted_path)
            assets.add(converted_path)
        else:
            # Link image path to assets
            assets.add(armutils.safe_assetpath(image.filepath))


    # if image_format != 'RGBA32':
        # tex['format'] = image_format
    
    interpolation = image_node.interpolation
    aniso = wrd.anisotropic_filtering_state
    if aniso == 'On':
        interpolation = 'Smart'
    elif aniso == 'Off' and interpolation == 'Smart':
        interpolation = 'Linear'
    
    # TODO: Blender seems to load full images on size request, cache size instead
    powimage = is_pow(image.size[0]) and is_pow(image.size[1])

    # Pow2 required to generate mipmaps
    if powimage == True:
        if interpolation == 'Cubic': # Mipmap linear
            tex['mipmap_filter'] = 'linear'
            tex['generate_mipmaps'] = True
        elif interpolation == 'Smart': # Mipmap anisotropic
            tex['min_filter'] = 'anisotropic'
            tex['mipmap_filter'] = 'linear'
            tex['generate_mipmaps'] = True
    elif (image_node.interpolation == 'Cubic' or image_node.interpolation == 'Smart'):
        log.warn(matname + '/' + image.name + ' - power of 2 texture required for ' + image_node.interpolation + ' interpolation')

    if image_node.extension != 'REPEAT': # Extend or clip
        tex['u_addressing'] = 'clamp'
        tex['v_addressing'] = 'clamp'
    else:
        if state.target == 'html5' and powimage == False:
            log.warn(matname + '/' + image.name + ' - non power of 2 texture can not use repeat mode on HTML5 target')
            tex['u_addressing'] = 'clamp'
            tex['v_addressing'] = 'clamp'
    
    # if image.source == 'MOVIE': # Just append movie texture trait for now
    #     movie_trait = {}
    #     movie_trait['type'] = 'Script'
    #     movie_trait['class_name'] = 'armory.trait.internal.MovieTexture'
    #     movie_trait['parameters'] = [tex['file']]
    #     for o in self.materialToGameObjectDict[material]:
    #         o['traits'].append(movie_trait)
    #     tex['source'] = 'movie'
    #     tex['file'] = '' # MovieTexture will load the video

    return tex

def is_pow(num):
    return ((num & (num - 1)) == 0) and num != 0
