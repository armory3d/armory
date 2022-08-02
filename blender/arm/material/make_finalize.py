import bpy

import arm
import arm.material.make_tess as make_tess
from arm.material.shader import ShaderContext

if arm.is_reload(__name__):
    make_tess = arm.reload_module(make_tess)
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import ShaderContext
else:
    arm.enable_reload(__name__)


def make(con_mesh: ShaderContext):
    vert = con_mesh.vert
    frag = con_mesh.frag
    geom = con_mesh.geom
    tesc = con_mesh.tesc
    tese = con_mesh.tese

    # Additional values referenced in cycles
    # TODO: enable from cycles.py
    if frag.contains('dotNV') and not frag.contains('float dotNV'):
        frag.write_init('float dotNV = max(dot(n, vVec), 0.0);')

        # n is not always defined yet (in some shadowmap shaders e.g.)
        if not frag.contains('vec3 n'):
            vert.add_out('vec3 wnormal')
            vert.add_uniform('mat3 N', '_normalMatrix')
            vert.write_attrib('wnormal = normalize(N * vec3(nor.xy, pos.w));')
            frag.write_attrib('vec3 n = normalize(wnormal);')

            # If not yet added, add nor vertex data
            vertex_elems = con_mesh.data['vertex_elements']
            has_normals = False
            for elem in vertex_elems:
                if elem['name'] == 'nor':
                    has_normals = True
                    break
            if not has_normals:
                vertex_elems.append({'name': 'nor', 'data': 'short2norm'})

    write_wpos = False
    if frag.contains('vVec') and not frag.contains('vec3 vVec'):
        if tese is not None:
            tese.add_out('vec3 eyeDir')
            tese.add_uniform('vec3 eye', '_cameraPosition')
            tese.write('eyeDir = eye - wposition;')

        else:
            if not vert.contains('wposition'):
                write_wpos = True
            vert.add_out('vec3 eyeDir')
            vert.add_uniform('vec3 eye', '_cameraPosition')
            vert.write('eyeDir = eye - wposition;')
        frag.write_attrib('vec3 vVec = normalize(eyeDir);')

    export_wpos = False
    if frag.contains('wposition') and not frag.contains('vec3 wposition'):
        export_wpos = True
    if tese is not None:
        export_wpos = True
    if vert.contains('wposition'):
        write_wpos = True

    if export_wpos:
        vert.add_uniform('mat4 W', '_worldMatrix')
        vert.add_out('vec3 wposition')
        vert.write_attrib('wposition = vec4(W * spos).xyz;')
    elif write_wpos:
        vert.add_uniform('mat4 W', '_worldMatrix')
        vert.write_attrib('vec3 wposition = vec4(W * spos).xyz;')

    frag_mpos = (frag.contains('mposition') and not frag.contains('vec3 mposition')) or vert.contains('mposition')
    if frag_mpos:
        vert.add_out('vec3 mposition')
        vert.add_uniform('float posUnpack', link='_posUnpack')
        vert.write_attrib('mposition = spos.xyz * posUnpack;')

    if tese is not None:
        if frag_mpos:
            make_tess.interpolate(tese, 'mposition', 3, declare_out=True)
        elif tese.contains('mposition') and not tese.contains('vec3 mposition'):
            vert.add_out('vec3 mposition')
            vert.write_pre = True
            vert.add_uniform('float posUnpack', link='_posUnpack')
            vert.write('mposition = spos.xyz * posUnpack;')
            vert.write_pre = False
            make_tess.interpolate(tese, 'mposition', 3, declare_out=False)

    frag_bpos = (frag.contains('bposition') and not frag.contains('vec3 bposition')) or vert.contains('bposition')
    if frag_bpos:
        vert.add_out('vec3 bposition')
        vert.add_uniform('vec3 dim', link='_dim')
        vert.add_uniform('vec3 hdim', link='_halfDim')
        vert.add_uniform('float posUnpack', link='_posUnpack')
        vert.write_attrib('bposition = (spos.xyz * posUnpack + hdim) / dim;')
        vert.write_attrib('if (dim.z == 0) bposition.z = 0;')
        vert.write_attrib('if (dim.y == 0) bposition.y = 0;')
        vert.write_attrib('if (dim.x == 0) bposition.x = 0;')

    if tese is not None:
        if frag_bpos:
            make_tess.interpolate(tese, 'bposition', 3, declare_out=True)
        elif tese.contains('bposition') and not tese.contains('vec3 bposition'):
            vert.add_out('vec3 bposition')
            vert.add_uniform('vec3 dim', link='_dim')
            vert.add_uniform('vec3 hdim', link='_halfDim')
            vert.add_uniform('float posUnpack', link='_posUnpack')
            vert.write_attrib('bposition = (spos.xyz * posUnpack + hdim) / dim;')
            make_tess.interpolate(tese, 'bposition', 3, declare_out=False)

    frag_wtan = (frag.contains('wtangent') and not frag.contains('vec3 wtangent')) or vert.contains('wtangent')
    if frag_wtan:
        # Indicate we want tang attrib in finalizer to prevent TBN generation
        con_mesh.add_elem('tex', 'short2norm')
        con_mesh.add_elem('tang', 'short4norm')
        vert.add_out('vec3 wtangent')
        vert.write_pre = True
        vert.write('wtangent = normalize(N * tang.xyz);')
        vert.write_pre = False

    if tese is not None:
        if frag_wtan:
            make_tess.interpolate(tese, 'wtangent', 3, declare_out=True)
        elif tese.contains('wtangent') and not tese.contains('vec3 wtangent'):
            vert.add_out('vec3 wtangent')
            vert.write_pre = True
            vert.write('wtangent = normalize(N * tang.xyz);')
            vert.write_pre = False
            make_tess.interpolate(tese, 'wtangent', 3, declare_out=False)

    if frag.contains('vVecCam'):
        vert.add_out('vec3 eyeDirCam')
        vert.add_uniform('mat4 WV', '_worldViewMatrix')
        vert.write('eyeDirCam = vec4(WV * spos).xyz; eyeDirCam.z *= -1;')
        frag.write_attrib('vec3 vVecCam = normalize(eyeDirCam);')

    if frag.contains('nAttr'):
        vert.add_out('vec3 nAttr')
        vert.write_attrib('nAttr = vec3(nor.xy, pos.w);')

    wrd = bpy.data.worlds['Arm']
    if '_Legacy' in wrd.world_defs:
        frag.replace('sampler2DShadow', 'sampler2D')
        frag.replace('samplerCubeShadow', 'samplerCube')
