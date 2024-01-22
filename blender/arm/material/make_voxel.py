import bpy

import arm.utils
import arm.assets as assets
import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
import arm.material.make_particle as make_particle
import arm.make_state as state

import arm.utils
import arm.assets as assets
import arm.material.mat_state as mat_state

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    assets = arm.reload_module(assets)
    mat_state = arm.reload_module(mat_state)
else:
    arm.enable_reload(__name__)

def make(context_id):
    rpdat = arm.utils.get_rp()
    if rpdat.rp_voxels == 'Voxel AO':
        con = make_ao(context_id)

    assets.vs_equal(con, assets.shader_cons['voxel_vert'])
    assets.fs_equal(con, assets.shader_cons['voxel_frag'])
    assets.gs_equal(con, assets.shader_cons['voxel_geom'])

    return con

def make_ao(context_id):
    con_voxel = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'always', 'cull_mode': 'none', 'color_writes_red': [False], 'color_writes_green': [False], 'color_writes_blue': [False], 'color_writes_alpha': [False], 'conservative_raster': False })
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()

    vert = con_voxel.make_vert()
    frag = con_voxel.make_frag()
    geom = con_voxel.make_geom()
    tesc = None
    tese = None

    geom.ins = vert.outs
    frag.ins = geom.outs

    frag.add_include('compiled.inc')
    geom.add_include('compiled.inc')
    frag.add_include('std/math.glsl')
    frag.add_include('std/imageatomic.glsl')
    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')
    frag.add_uniform('layout(r8) writeonly image3D voxels')

    vert.add_include('compiled.inc')
    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_out('vec3 voxpositionGeom')

    vert.add_uniform('vec3 eyeLook', '_cameraLook')
    vert.add_uniform('vec3 eye', '_cameraPosition')
    vert.add_uniform('int clipmapLevel', '_clipmapLevel')

    vert.write('vec3 P = vec3(W * vec4(pos.xyz, 1.0));')
    vert.write('vec3 clipmap_center = floor(eye + eyeLook);')
    vert.write('float voxelSize = voxelgiVoxelSize * pow(2.0, clipmapLevel);')
    vert.write('voxpositionGeom = (P - clipmap_center) / voxelSize * 1.0 / voxelgiResolution.x;')

    geom.add_out('vec3 voxposition')

    geom.write('vec3 p1 = voxpositionGeom[1] - voxpositionGeom[0];')
    geom.write('vec3 p2 = voxpositionGeom[2] - voxpositionGeom[0];')
    geom.write('vec3 p = abs(cross(p1, p2));')
    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    voxposition = voxpositionGeom[i];')
    geom.write('    if (p.z > p.x && p.z > p.y) {')
    geom.write('        gl_Position = vec4(voxposition.x, voxposition.y, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else if (p.x > p.y && p.x > p.z) {')
    geom.write('        gl_Position = vec4(voxposition.y, voxposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else {')
    geom.write('        gl_Position = vec4(voxposition.x, voxposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    EmitVertex();')
    geom.write('}')
    geom.write('EndPrimitive();')

    frag.write('if (abs(voxposition.z) > ' + rpdat.rp_voxelgi_resolution_z + ' || abs(voxposition.x) > 1 || abs(voxposition.y) > 1) return;')

    frag.add_uniform('int clipmapLevel', '_clipmapLevel')
    frag.write('vec3 uvw = (voxposition * 0.5 + 0.5);')
    frag.write('uvw.y = uvw.y + clipmapLevel;')
    frag.write('uvw = uvw * voxelgiResolution.x;')
    frag.write('imageStore(voxels, ivec3(uvw), vec4(1.0));')

    return con_voxel
