import bpy
import arm.utils
import arm.assets as assets
import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
import arm.material.make_particle as make_particle
import arm.make_state as state

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    assets = arm.reload_module(assets)
    mat_state = arm.reload_module(mat_state)
else:
    arm.enable_reload(__name__)

def make(context_id):
    rpdat = arm.utils.get_rp()
    con = make_ao(context_id)

    assets.vs_equal(con, assets.shader_cons['voxel_vert'])
    assets.fs_equal(con, assets.shader_cons['voxel_frag'])
    assets.gs_equal(con, assets.shader_cons['voxel_geom'])

    return con

def make_ao(context_id):
    con_voxel = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'always', 'cull_mode': 'none', 'color_writes_red': [False], 'color_writes_green': [False], 'color_writes_blue': [False], 'color_write_alpha': False, 'conservative_raster': False })
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()

    vert = con_voxel.make_vert()
    frag = con_voxel.make_frag()
    geom = con_voxel.make_geom()
    tesc = None
    tese = None

    if arm.utils.get_gapi() == 'direct3d11':
        for e in con_voxel.data['vertex_elements']:
            if e['name'] == 'nor':
                con_voxel.data['vertex_elements'].remove(e)
                break

        # No geom shader compiler for hlsl yet
        vert.noprocessing = True
        frag.noprocessing = True
        geom.noprocessing = True

        vert.add_uniform('mat4 W', '_worldMatrix')
        vert.write('uniform float4x4 W;')
        if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
            vert.add_uniform('vec3 eyeSnap', '_cameraPositionSnap')
            vert.write('uniform float3 eyeSnap;')
        vert.write('struct SPIRV_Cross_Input { float4 pos : TEXCOORD0; };')
        vert.write('struct SPIRV_Cross_Output { float4 svpos : SV_POSITION; };')
        vert.write('SPIRV_Cross_Output main(SPIRV_Cross_Input stage_input) {')
        vert.write('  SPIRV_Cross_Output stage_output;')
        voxHalfExt = str(round(rpdat.arm_voxelgi_dimensions / 2.0))
        if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
            vert.write('  stage_output.svpos.xyz = (mul(float4(stage_input.pos.xyz, 1.0), W).xyz - eyeSnap) / float3(' + voxHalfExt + ', ' + voxHalfExt + ', ' + voxHalfExt + ');')
        else:
            vert.write('  stage_output.svpos.xyz = mul(float4(stage_input.pos.xyz, 1.0), W).xyz / float3(' + voxHalfExt + ', ' + voxHalfExt + ', ' + voxHalfExt + ');')
        vert.write('  stage_output.svpos.w = 1.0;')
        vert.write('  return stage_output;')
        vert.write('}')

        geom.write('struct SPIRV_Cross_Input { float4 svpos : SV_POSITION; };')
        geom.write('struct SPIRV_Cross_Output { float3 wpos : TEXCOORD0; float4 svpos : SV_POSITION; };')
        geom.write('[maxvertexcount(3)]')
        geom.write('void main(triangle SPIRV_Cross_Input stage_input[3], inout TriangleStream<SPIRV_Cross_Output> output) {')
        geom.write('  float3 p1 = stage_input[1].svpos.xyz - stage_input[0].svpos.xyz;')
        geom.write('  float3 p2 = stage_input[2].svpos.xyz - stage_input[0].svpos.xyz;')
        geom.write('  float3 p = abs(cross(p1, p2));')
        geom.write('  for (int i = 0; i < 3; ++i) {')
        geom.write('    SPIRV_Cross_Output stage_output;')
        geom.write('    stage_output.wpos = stage_input[i].svpos.xyz;')
        geom.write('    if (p.z > p.x && p.z > p.y) {')
        geom.write('      stage_output.svpos = float4(stage_input[i].svpos.x, stage_input[i].svpos.y, 0.0, 1.0);')
        geom.write('    }')
        geom.write('    else if (p.x > p.y && p.x > p.z) {')
        geom.write('      stage_output.svpos = float4(stage_input[i].svpos.y, stage_input[i].svpos.z, 0.0, 1.0);')
        geom.write('    }')
        geom.write('    else {')
        geom.write('      stage_output.svpos = float4(stage_input[i].svpos.x, stage_input[i].svpos.z, 0.0, 1.0);')
        geom.write('    }')
        geom.write('    output.Append(stage_output);')
        geom.write('  }')
        geom.write('}')

        frag.add_uniform('layout(r8) writeonly image3D voxels')
        frag.write('RWTexture3D<float> voxels;')
        frag.write('struct SPIRV_Cross_Input { float3 wpos : TEXCOORD0; };')
        frag.write('struct SPIRV_Cross_Output { float4 FragColor : SV_TARGET0; };')
        frag.write('void main(SPIRV_Cross_Input stage_input) {')
        frag.write('  if (abs(stage_input.wpos.z) > ' + rpdat.rp_voxelgi_resolution_z + ' || abs(stage_input.wpos.x) > 1 || abs(stage_input.wpos.y) > 1) return;')
        voxRes = str(rpdat.rp_voxelgi_resolution)
        voxResZ = str(int(int(rpdat.rp_voxelgi_resolution) * float(rpdat.rp_voxelgi_resolution_z)))
        frag.write('  voxels[int3(' + voxRes + ', ' + voxRes + ', ' + voxResZ + ') * (stage_input.wpos * 0.5 + 0.5)] = 1.0;')
        frag.write('')
        frag.write('}')
    else:
        geom.ins = vert.outs
        frag.ins = geom.outs

        frag.add_include('compiled.inc')
        frag.add_include('std/math.glsl')
        frag.add_include('std/imageatomic.glsl')
        frag.write_header('#extension GL_ARB_shader_image_load_store : enable')

        frag.add_uniform('layout(r8) writeonly image3D voxels')

        vert.add_include('compiled.inc')
        vert.add_uniform('mat4 W', '_worldMatrix')
        vert.add_out('vec3 voxpositionGeom')

        if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
            vert.add_uniform('vec3 eyeSnap', '_cameraPositionSnap')
            vert.write('voxpositionGeom = (vec3(W * vec4(pos.xyz, 1.0)) - eyeSnap) / voxelgiHalfExtents;')
        else:
            vert.write('voxpositionGeom = vec3(W * vec4(pos.xyz, 1.0)) / voxelgiHalfExtents;')

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
        frag.write('imageStore(voxels, ivec3(voxelgiResolution * (voxposition * 0.5 + 0.5)), vec4(1.0));')

    return con_voxel
