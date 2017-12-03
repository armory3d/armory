import os
import shutil
import subprocess

from .arm import assets
from .arm.utils import get_sdk_path, krom_paths

def export_sdf(bobject, fp):
    # if hasattr(bobject.data, 'arm_sdfgen') and bobject.data.arm_sdfgen:
        # o['sdf_ref'] = 'sdf_' + oid

    if hasattr(bobject.data, 'arm_sdfgen') and bobject.data.arm_sdfgen:
        # Copy input
        sdk_path = get_sdk_path()
        sdfgen_path = sdk_path + '/armory/tools/sdfgen'
        shutil.copy(fp, sdfgen_path + '/krom/mesh.arm')
        # Extract basecolor
        # Assume Armpry PBR with linked texture for now
        # mat = bobject.material_slots[0].material
        # img = None
        # for n in mat.node_tree.nodes:
            # if n.type == 'GROUP' and n.node_tree.name.startswith('Armory PBR') and n.inputs[0].is_linked:
                # img = n.inputs[0].links[0].from_node.image
                # fp_img = bpy.path.abspath(img.filepath)
                # shutil.copy(fp_img, sdfgen_path + '/krom/mesh.png')
        # Run
        krom_location, krom_path = krom_paths()
        krom_dir = sdfgen_path + '/krom'
        krom_res = sdfgen_path + '/krom'
        subprocess.check_output([krom_path, krom_dir, krom_res, '--nosound', '--nowindow'])
        # Copy output
        sdf_path = fp.replace('/mesh_', '/sdf_')
        shutil.copy('out.bin', sdf_path)
        assets.add(sdf_path)
        os.remove('out.bin')
        os.remove(sdfgen_path + '/krom/mesh.arm')
        # if img != None:
            # os.remove(sdfgen_path + '/krom/mesh.png')
