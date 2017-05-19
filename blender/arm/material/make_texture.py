import bpy
import os
import arm.log as log
import arm.utils
import arm.assets as assets
import arm.material.mat_state as mat_state
import arm.make_state as state
import shutil

def make(image_node, tex_name, matname=None):
    wrd = bpy.data.worlds['Arm']
    tex = {}
    tex['name'] = tex_name
    image = image_node.image
    if matname == None:
        matname = mat_state.material.name

    if image == None:
        return None

    if image.filepath == '':
        log.warn(matname + '/' + image.name + ' - file path not found')
        return None

    # Reference image name
    texpath = arm.utils.asset_path(image.filepath)
    texfile = arm.utils.extract_filename(image.filepath)
    tex['file'] = arm.utils.safestr(texfile)
    s = tex['file'].rsplit('.', 1)
    
    if len(s) == 1:
        log.warn(matname + '/' + image.name + ' - file extension required for image name')
        return None

    ext = s[1].lower()
    do_convert = ext != 'jpg' and ext != 'png' and ext != 'hdr' and ext != 'mp4' # Convert image
    if do_convert:
        tex['file'] = tex['file'].rsplit('.', 1)[0] + '.jpg'
        # log.warn(matname + '/' + image.name + ' - image format is not (jpg/png/hdr), converting to jpg.')

    if image.packed_file != None or not is_ascii(texfile):
        # Extract packed data / copy non-ascii texture
        unpack_path = arm.utils.get_fp() + '/build/compiled/Assets/unpacked'
        if not os.path.exists(unpack_path):
            os.makedirs(unpack_path)
        unpack_filepath = unpack_path + '/' + tex['file']
        
        if do_convert:
            if not os.path.isfile(unpack_filepath):
                arm.utils.write_image(image, unpack_filepath)
        else:

            # Write bytes if size is different or file does not exist yet
            if image.packed_file != None:
                if not os.path.isfile(unpack_filepath) or os.path.getsize(unpack_filepath) != image.packed_file.size:
                    with open(unpack_filepath, 'wb') as f:
                        f.write(image.packed_file.data)
            # Copy non-ascii texture
            else:
                if not os.path.isfile(unpack_filepath) or os.path.getsize(unpack_filepath) != os.path.getsize(texpath):
                    shutil.copy(texpath, unpack_filepath)

        assets.add(unpack_filepath)

    else:
        if not os.path.isfile(arm.utils.asset_path(image.filepath)):
            log.warn('Material ' + matname + '/' + image.name + ' - file not found(' + image.filepath + ')')
            return None

        if do_convert:
            converted_path = arm.utils.get_fp() + '/build/compiled/Assets/unpacked/' + tex['file']
            # TODO: delete cache when file changes
            if not os.path.isfile(converted_path):
                arm.utils.write_image(image, converted_path)
            assets.add(converted_path)
        else:
            # Link image path to assets
            # TODO: Khamake converts .PNG to .jpg? Convert ext to lowercase on windows
            if arm.utils.get_os() == 'win':
                s = image.filepath.rsplit('.', 1)
                assets.add(arm.utils.asset_path(s[0] + '.' + s[1].lower()))
            else:
                assets.add(arm.utils.asset_path(image.filepath))


    # if image_format != 'RGBA32':
        # tex['format'] = image_format
    
    interpolation = image_node.interpolation
    texfilter = wrd.texture_filtering_state
    if texfilter == 'Anisotropic':
        interpolation = 'Smart'
    elif texfilter == 'Linear':
        interpolation = 'Linear'
    elif texfilter == 'Point':
        interpolation = 'Closest'
    
    # TODO: Blender seems to load full images on size request, cache size instead
    powimage = is_pow(image.size[0]) and is_pow(image.size[1])

    if state.target == 'html5' and powimage == False and (image_node.interpolation == 'Cubic' or image_node.interpolation == 'Smart'):
        log.warn(matname + '/' + image.name + ' - non power of 2 texture using ' + image_node.interpolation + ' interpolation requires WebGL2')

    if interpolation == 'Cubic': # Mipmap linear
        tex['mipmap_filter'] = 'linear'
        tex['generate_mipmaps'] = True
    elif interpolation == 'Smart': # Mipmap anisotropic
        tex['min_filter'] = 'anisotropic'
        tex['mipmap_filter'] = 'linear'
        tex['generate_mipmaps'] = True
    elif interpolation == 'Closest':
        tex['min_filter'] = 'point'
        tex['mag_filter'] = 'point'
    # else defaults to linear

    if image_node.extension != 'REPEAT': # Extend or clip
        tex['u_addressing'] = 'clamp'
        tex['v_addressing'] = 'clamp'
    else:
        if state.target == 'html5' and powimage == False:
            log.warn(matname + '/' + image.name + ' - non power of 2 texture using repeat mode requires WebGL2')
            # tex['u_addressing'] = 'clamp'
            # tex['v_addressing'] = 'clamp'
    
    if image.source == 'MOVIE': # Just append movie texture trait for now
        movie_trait = {}
        movie_trait['type'] = 'Script'
        movie_trait['class_name'] = 'armory.trait.internal.MovieTexture'
        movie_trait['parameters'] = [tex['file']]
        for o in mat_state.mat_armusers[mat_state.material]:
            o['traits'].append(movie_trait)
        tex['source'] = 'movie'
        tex['file'] = '' # MovieTexture will load the video

    return tex

def is_pow(num):
    return ((num & (num - 1)) == 0) and num != 0

def is_ascii(s):
    return len(s) == len(s.encode())
