import bpy
from typing import Union

import arm.material.cycles as cycles
import arm.material.cycles_functions as c_functions
from arm.material.shader import floatstr, vec3str
import arm.utils


def parse_attribute(node: bpy.types.ShaderNodeAttribute, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    # Color
    if out_socket == node.outputs[0]:
        # Vertex colors only for now
        cycles.con.add_elem('col', 'short4norm')
        return 'vcolor'

    # Vector
    elif out_socket == node.outputs[1]:
        # UV maps only for now
        cycles.con.add_elem('tex', 'short2norm')
        mat = cycles.mat_get_material()
        mat_users = cycles.mat_get_material_users()

        if mat_users is not None and mat in mat_users:
            mat_user = mat_users[mat][0]

            # No UV layers for Curve
            if hasattr(mat_user.data, 'uv_layers'):
                lays = mat_user.data.uv_layers

                # Second UV map referenced
                if len(lays) > 1 and node.attribute_name == lays[1].name:
                    cycles.con.add_elem('tex1', 'short2norm')
                    return 'vec3(texCoord1.x, 1.0 - texCoord1.y, 0.0)'

        return 'vec3(texCoord.x, 1.0 - texCoord.y, 0.0)'

    # Fac
    else:
        if node.attribute_name == 'time':
            cycles.curshader.add_uniform('float time', link='_time')
            return 'time'

            # Return 0.0 till drivers are implemented
        else:
            return '0.0'


def parse_rgb(node: bpy.types.ShaderNodeRGB, out_socket: bpy.types.NodeSocket) -> vec3str:
    if node.arm_material_param:
        nn = 'param_' + cycles.node_name(node.name)
        cycles.curshader.add_uniform(f'vec3 {nn}', link=f'{node.name}')
        return nn
    else:
        return cycles.to_vec3(out_socket.default_value)


def parse_vertex_color(node: bpy.types.ShaderNodeVertexColor, out_socket: bpy.types.NodeSocket) -> vec3str:
    cycles.con.add_elem('col', 'short4norm')
    return 'vcolor'


def parse_camera(node: bpy.types.ShaderNodeCameraData, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    # View Vector in camera space
    if out_socket == node.outputs[0]:
        return 'vVecCam'

    # View Z Depth
    elif out_socket == node.outputs[1]:
        cycles.curshader.add_include('std/math.glsl')
        cycles.curshader.add_uniform('vec2 cameraProj', link='_cameraPlaneProj')
        return 'linearize(gl_FragCoord.z, cameraProj)'

    # View Distance
    else:
        cycles.curshader.add_uniform('vec3 eye', link='_cameraPosition')
        return 'distance(eye, wposition)'


def parse_geometry(node: bpy.types.ShaderNodeNewGeometry, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    # Position
    if out_socket == node.outputs[0]:
        return 'wposition'
    # Normal
    elif out_socket == node.outputs[1]:
        return 'n' if cycles.curshader.shader_type == 'frag' else 'wnormal'
    # Tangent
    elif out_socket == node.outputs[2]:
        return 'wtangent'
    # True Normal
    elif out_socket == node.outputs[3]:
        return 'n' if cycles.curshader.shader_type == 'frag' else 'wnormal'
    # Incoming
    elif out_socket == node.outputs[4]:
        return 'vVec'
    # Parametric
    elif out_socket == node.outputs[5]:
        return 'mposition'
    # Backfacing
    elif out_socket == node.outputs[6]:
        return '(1.0 - float(gl_FrontFacing))'
    # Pointiness
    elif out_socket == node.outputs[7]:
        return '0.0'


def parse_hairinfo(node: bpy.types.ShaderNodeHairInfo, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    # Tangent Normal
    if out_socket == node.outputs[3]:
        return 'vec3(0.0)'
    else:
        # Is Strand
        # Intercept
        # Thickness
        # Random
        return '0.5'


def parse_objectinfo(node: bpy.types.ShaderNodeObjectInfo, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    # Location
    if out_socket == node.outputs[0]:
        return 'wposition'

    # TODO: Color
    elif out_socket == node.outputs[1]:
        return 'wposition' # cycles.to_vec3(object.color)

    # Object Index
    elif out_socket == node.outputs[2]:
        cycles.curshader.add_uniform('float objectInfoIndex', link='_objectInfoIndex')
        return 'objectInfoIndex'

    # Material Index
    elif out_socket == node.outputs[3]:
        cycles.curshader.add_uniform('float objectInfoMaterialIndex', link='_objectInfoMaterialIndex')
        return 'objectInfoMaterialIndex'

    # Random
    elif out_socket == node.outputs[4]:
        cycles.curshader.add_uniform('float objectInfoRandom', link='_objectInfoRandom')
        return 'objectInfoRandom'


def parse_particleinfo(node: bpy.types.ShaderNodeParticleInfo, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    particles_on = arm.utils.get_rp().arm_particles == 'On'

    # Index
    if out_socket == node.outputs[0]:
        cycles.particle_info['index'] = True
        return 'p_index' if particles_on else '0.0'

    # TODO: Random
    if out_socket == node.outputs[1]:
        return '0.0'

    # Age
    elif out_socket == node.outputs[2]:
        cycles.particle_info['age'] = True
        return 'p_age' if particles_on else '0.0'

    # Lifetime
    elif out_socket == node.outputs[3]:
        cycles.particle_info['lifetime'] = True
        return 'p_lifetime' if particles_on else '0.0'

    # Location
    if out_socket == node.outputs[4]:
        cycles.particle_info['location'] = True
        return 'p_location' if particles_on else 'vec3(0.0)'

    # Size
    elif out_socket == node.outputs[5]:
        cycles.particle_info['size'] = True
        return '1.0'

    # Velocity
    elif out_socket == node.outputs[6]:
        cycles.particle_info['velocity'] = True
        return 'p_velocity' if particles_on else 'vec3(0.0)'

    # Angular Velocity
    elif out_socket == node.outputs[7]:
        cycles.particle_info['angular_velocity'] = True
        return 'vec3(0.0)'


def parse_tangent(node: bpy.types.ShaderNodeTangent, out_socket: bpy.types.NodeSocket) -> vec3str:
    return 'wtangent'


def parse_texcoord(node: bpy.types.ShaderNodeTexCoord, out_socket: bpy.types.NodeSocket) -> vec3str:
    #obj = node.object
    #instance = node.from_instance
    if out_socket == node.outputs[0]: # Generated - bounds
        return 'bposition'
    elif out_socket == node.outputs[1]: # Normal
        return 'n'
    elif out_socket == node.outputs[2]: # UV
        cycles.con.add_elem('tex', 'short2norm')
        return 'vec3(texCoord.x, 1.0 - texCoord.y, 0.0)'
    elif out_socket == node.outputs[3]: # Object
        return 'mposition'
    elif out_socket == node.outputs[4]: # Camera
        return 'vec3(0.0)' # 'vposition'
    elif out_socket == node.outputs[5]: # Window
        return 'vec3(0.0)' # 'wvpposition'
    elif out_socket == node.outputs[6]: # Reflection
        return 'vec3(0.0)'


def parse_uvmap(node: bpy.types.ShaderNodeUVMap, out_socket: bpy.types.NodeSocket) -> vec3str:
    # instance = node.from_instance
    cycles.con.add_elem('tex', 'short2norm')
    mat = cycles.mat_get_material()
    mat_users = cycles.mat_get_material_users()
    if mat_users != None and mat in mat_users:
        mat_user = mat_users[mat][0]
        if hasattr(mat_user.data, 'uv_layers'):
            lays = mat_user.data.uv_layers
            # Second uvmap referenced
            if len(lays) > 1 and node.uv_map == lays[1].name:
                cycles.con.add_elem('tex1', 'short2norm')
                return 'vec3(texCoord1.x, 1.0 - texCoord1.y, 0.0)'
    return 'vec3(texCoord.x, 1.0 - texCoord.y, 0.0)'


def parse_fresnel(node: bpy.types.ShaderNodeFresnel, out_socket: bpy.types.NodeSocket) -> floatstr:
    cycles.curshader.add_function(c_functions.str_fresnel)
    ior = cycles.parse_value_input(node.inputs[0])
    if node.inputs[1].is_linked:
        dotnv = 'dot({0}, vVec)'.format(cycles.parse_vector_input(node.inputs[1]))
    else:
        dotnv = 'dotNV'
    return 'fresnel({0}, {1})'.format(ior, dotnv)


def parse_layerweight(node: bpy.types.ShaderNodeLayerWeight, out_socket: bpy.types.NodeSocket) -> floatstr:
    blend = cycles.parse_value_input(node.inputs[0])
    if node.inputs[1].is_linked:
        dotnv = 'dot({0}, vVec)'.format(cycles.parse_vector_input(node.inputs[1]))
    else:
        dotnv = 'dotNV'

    # Fresnel
    if out_socket == node.outputs[0]:
        cycles.curshader.add_function(c_functions.str_fresnel)
        return 'fresnel(1.0 / (1.0 - {0}), {1})'.format(blend, dotnv)
    # Facing
    elif out_socket == node.outputs[1]:
        return '(1.0 - pow({0}, ({1} < 0.5) ? 2.0 * {1} : 0.5 / (1.0 - {1})))'.format(dotnv, blend)


def parse_lightpath(node: bpy.types.ShaderNodeLightPath, out_socket: bpy.types.NodeSocket) -> floatstr:
    if out_socket == node.outputs[0]: # Is Camera Ray
        return '1.0'
    elif out_socket == node.outputs[1]: # Is Shadow Ray
        return '0.0'
    elif out_socket == node.outputs[2]: # Is Diffuse Ray
        return '1.0'
    elif out_socket == node.outputs[3]: # Is Glossy Ray
        return '1.0'
    elif out_socket == node.outputs[4]: # Is Singular Ray
        return '0.0'
    elif out_socket == node.outputs[5]: # Is Reflection Ray
        return '0.0'
    elif out_socket == node.outputs[6]: # Is Transmission Ray
        return '0.0'
    elif out_socket == node.outputs[7]: # Ray Length
        return '0.0'
    elif out_socket == node.outputs[8]: # Ray Depth
        return '0.0'
    elif out_socket == node.outputs[9]: # Transparent Depth
        return '0.0'
    elif out_socket == node.outputs[10]: # Transmission Depth
        return '0.0'


def parse_value(node: bpy.types.ShaderNodeValue, out_socket: bpy.types.NodeSocket) -> floatstr:
    if node.arm_material_param:
        nn = 'param_' + cycles.node_name(node.name)
        cycles.curshader.add_uniform('float {0}'.format(nn), link='{0}'.format(node.name))
        return nn
    else:
        return cycles.to_vec1(node.outputs[0].default_value)


def parse_wireframe(node: bpy.types.ShaderNodeWireframe, out_socket: bpy.types.NodeSocket) -> floatstr:
    # node.use_pixel_size
    # size = parse_value_input(node.inputs[0])
    return '0.0'
