from typing import Union

import bpy
import mathutils

import arm.log as log
import arm.material.cycles as c
import arm.material.cycles_functions as c_functions
import arm.material.mat_state as mat_state
from arm.material.parser_state import ParserState, ParserContext
from arm.material.shader import floatstr, vec3str
import arm.utils

if arm.is_reload(__name__):
    log = arm.reload_module(log)
    c = arm.reload_module(c)
    c_functions = arm.reload_module(c_functions)
    mat_state = arm.reload_module(mat_state)
    arm.material.parser_state = arm.reload_module(arm.material.parser_state)
    from arm.material.parser_state import ParserState, ParserContext
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import floatstr, vec3str
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


def parse_attribute(node: bpy.types.ShaderNodeAttribute, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    out_type = 'float' if out_socket.type == 'VALUE' else 'vec3'

    if node.attribute_name == 'time':
        state.curshader.add_uniform('float time', link='_time')

        if out_socket == node.outputs[3]:
            return '1.0'
        return c.cast_value('time', from_type='float', to_type=out_type)

    # UV maps (higher priority) and vertex colors
    if node.attribute_type == 'GEOMETRY':

        # Alpha output. Armory doesn't support vertex colors with alpha
        # values yet and UV maps don't have an alpha channel
        if out_socket == node.outputs[3]:
            return '1.0'

        # UV maps
        mat = c.mat_get_material()
        mat_users = c.mat_get_material_users()

        if mat_users is not None and mat in mat_users:
            mat_user = mat_users[mat][0]

            # Curves don't have uv layers, so check that first
            if hasattr(mat_user.data, 'uv_layers'):
                lays = mat_user.data.uv_layers

                # First UV map referenced
                if len(lays) > 0 and node.attribute_name == lays[0].name:
                    state.con.add_elem('tex', 'short2norm')
                    state.dxdy_varying_input_value = True
                    return c.cast_value('vec3(texCoord.x, 1.0 - texCoord.y, 0.0)', from_type='vec3', to_type=out_type)

                # Second UV map referenced
                elif len(lays) > 1 and node.attribute_name == lays[1].name:
                    state.con.add_elem('tex1', 'short2norm')
                    state.dxdy_varying_input_value = True
                    return c.cast_value('vec3(texCoord1.x, 1.0 - texCoord1.y, 0.0)', from_type='vec3', to_type=out_type)

        # Vertex colors
        # TODO: support multiple vertex color sets
        state.con.add_elem('col', 'short4norm')
        state.dxdy_varying_input_value = True
        return c.cast_value('vcolor', from_type='vec3', to_type=out_type)

    # Check object properties
    # see https://developer.blender.org/rB6fdcca8de6 for reference
    mat = c.mat_get_material()
    mat_users = c.mat_get_material_users()
    if mat_users is not None and mat in mat_users:
        # Use first material user for now...
        mat_user = mat_users[mat][0]

        val = None
        # Custom properties first
        if node.attribute_name in mat_user:
            val = mat_user[node.attribute_name]
        # Blender properties
        elif hasattr(mat_user, node.attribute_name):
            val = getattr(mat_user, node.attribute_name)

        if val is not None:
            if isinstance(val, float):
                return c.cast_value(str(val), from_type='float', to_type=out_type)
            elif isinstance(val, int):
                return c.cast_value(str(val), from_type='int', to_type=out_type)
            elif isinstance(val, mathutils.Vector) and len(val) <= 4:
                out = val.to_4d()

                if out_socket == node.outputs[3]:
                    return c.to_vec1(out[3])
                return c.cast_value(c.to_vec3(out), from_type='vec3', to_type=out_type)

    # Default values, attribute name did not match
    if out_socket == node.outputs[3]:
        return '1.0'
    return c.cast_value('0.0', from_type='float', to_type=out_type)


def parse_rgb(node: bpy.types.ShaderNodeRGB, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    if node.arm_material_param:
        nn = 'param_' + c.node_name(node.name)
        v = out_socket.default_value
        value = [float(v[0]), float(v[1]), float(v[2])]
        state.curshader.add_uniform(f'vec3 {nn}', link=f'{node.name}', default_value=value, is_arm_mat_param=True)
        return nn
    else:
        return c.to_vec3(out_socket.default_value)


def parse_vertex_color(node: bpy.types.ShaderNodeVertexColor, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    state.con.add_elem('col', 'short4norm')
    return 'vcolor'


def parse_camera(node: bpy.types.ShaderNodeCameraData, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    # View Vector in camera space
    if out_socket == node.outputs[0]:
        state.dxdy_varying_input_value = True
        return 'vVecCam'

    # View Z Depth
    elif out_socket == node.outputs[1]:
        state.curshader.add_include('std/math.glsl')
        state.curshader.add_uniform('vec2 cameraProj', link='_cameraPlaneProj')
        state.dxdy_varying_input_value = True
        return 'linearize(gl_FragCoord.z, cameraProj)'

    # View Distance
    else:
        state.curshader.add_uniform('vec3 eye', link='_cameraPosition')
        state.dxdy_varying_input_value = True
        return 'distance(eye, wposition)'


def parse_geometry(node: bpy.types.ShaderNodeNewGeometry, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    # Position
    if out_socket == node.outputs[0]:
        state.dxdy_varying_input_value = True
        return 'wposition'
    # Normal
    elif out_socket == node.outputs[1]:
        state.dxdy_varying_input_value = True
        return 'n' if state.curshader.shader_type == 'frag' else 'wnormal'
    # Tangent
    elif out_socket == node.outputs[2]:
        state.dxdy_varying_input_value = True
        return 'wtangent'
    # True Normal
    elif out_socket == node.outputs[3]:
        state.dxdy_varying_input_value = True
        return 'n' if state.curshader.shader_type == 'frag' else 'wnormal'
    # Incoming
    elif out_socket == node.outputs[4]:
        state.dxdy_varying_input_value = True
        return 'vVec'
    # Parametric
    elif out_socket == node.outputs[5]:
        state.dxdy_varying_input_value = True
        return 'mposition'
    # Backfacing
    elif out_socket == node.outputs[6]:
        return '(1.0 - float(gl_FrontFacing))' if state.context == ParserContext.OBJECT else '0.0'
    # Pointiness
    elif out_socket == node.outputs[7]:
        return '0.0'
    # Random Per Island
    elif out_socket == node.outputs[8]:
        return '0.0'


def parse_hairinfo(node: bpy.types.ShaderNodeHairInfo, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    # Tangent Normal
    if out_socket == node.outputs[3]:
        return 'vec3(0.0)'
    else:
        # Is Strand
        # Intercept
        # Thickness
        # Random
        return '0.5'


def parse_objectinfo(node: bpy.types.ShaderNodeObjectInfo, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    # Location
    if out_socket == node.outputs[0]:
        if state.context == ParserContext.WORLD:
            return c.to_vec3((0.0, 0.0, 0.0))
        return 'wposition'

    # Color
    elif out_socket == node.outputs[1]:
        if state.context == ParserContext.WORLD:
            # Use world strength like Blender
            background_node = c.node_by_type(state.world.node_tree.nodes, 'BACKGROUND')
            if background_node is None:
                return c.to_vec3((0.0, 0.0, 0.0))
            return c.to_vec3([background_node.inputs[1].default_value] * 3)

        # TODO: Implement object color in Iron
        # state.curshader.add_uniform('vec3 objectInfoColor', link='_objectInfoColor')
        # return 'objectInfoColor'
        return c.to_vec3((1.0, 1.0, 1.0))

    # Alpha
    elif out_socket == node.outputs[2]:
        # TODO, see color output above
        return '0.0'

    # Object Index
    elif out_socket == node.outputs[3]:
        if state.context == ParserContext.WORLD:
            return '0.0'
        state.curshader.add_uniform('float objectInfoIndex', link='_objectInfoIndex')
        return 'objectInfoIndex'

    # Material Index
    elif out_socket == node.outputs[4]:
        if state.context == ParserContext.WORLD:
            return '0.0'
        state.curshader.add_uniform('float objectInfoMaterialIndex', link='_objectInfoMaterialIndex')
        return 'objectInfoMaterialIndex'

    # Random
    elif out_socket == node.outputs[5]:
        if state.context == ParserContext.WORLD:
            return '0.0'

        # Use random value per instance
        if mat_state.uses_instancing:
            state.vert.add_out(f'flat float irand')
            state.frag.add_in(f'flat float irand')
            state.vert.write(f'irand = fract(sin(gl_InstanceID) * 43758.5453);')
            return 'irand'

        state.curshader.add_uniform('float objectInfoRandom', link='_objectInfoRandom')
        return 'objectInfoRandom'


def parse_particleinfo(node: bpy.types.ShaderNodeParticleInfo, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    particles_on = arm.utils.get_rp().arm_particles == 'GPU'

    # Index
    if out_socket == node.outputs[0]:
        c.particle_info['index'] = True
        return 'p_index' if particles_on else '0.0'

    # TODO: Random
    if out_socket == node.outputs[1]:
        c.particle_info['random'] = True
        return 'p_random' if particles_on else '0.0'

    # Age
    elif out_socket == node.outputs[2]:
        c.particle_info['age'] = True
        return 'p_age' if particles_on else '0.0'

    # Lifetime
    elif out_socket == node.outputs[3]:
        c.particle_info['lifetime'] = True
        return 'p_lifetime' if particles_on else '0.0'

    # Location
    if out_socket == node.outputs[4]:
        c.particle_info['location'] = True
        return 'p_location' if particles_on else 'vec3(0.0)'

    # Size
    elif out_socket == node.outputs[5]:
        c.particle_info['size'] = True
        return 'p_size' if particles_on else '1.0'

    # Velocity
    elif out_socket == node.outputs[6]:
        c.particle_info['velocity'] = True
        return 'p_velocity' if particles_on else 'vec3(0.0)'

    # Angular Velocity
    elif out_socket == node.outputs[7]:
        c.particle_info['angular_velocity'] = True
        return 'vec3(0.0)'


def parse_tangent(node: bpy.types.ShaderNodeTangent, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    state.dxdy_varying_input_value = True
    return 'wtangent'


def parse_texcoord(node: bpy.types.ShaderNodeTexCoord, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    #obj = node.object
    #instance = node.from_instance
    if out_socket == node.outputs[0]: # Generated - bounds
        state.dxdy_varying_input_value = True
        return 'bposition'
    elif out_socket == node.outputs[1]: # Normal
        state.dxdy_varying_input_value = True
        return 'n'
    elif out_socket == node.outputs[2]: # UV
        if state.context == ParserContext.WORLD:
            return 'vec3(0.0)'
        state.con.add_elem('tex', 'short2norm')
        state.dxdy_varying_input_value = True

        if bpy.app.version >= (4, 5, 0):
            return 'vec3(texCoord.x, texCoord.y, 0.0)'
        else:
            return 'vec3(texCoord.x, 1.0 - texCoord.y, 0.0)'

    elif out_socket == node.outputs[3]: # Object
        state.dxdy_varying_input_value = True
        return 'mposition'
    elif out_socket == node.outputs[4]: # Camera
        return 'vec3(0.0)' # 'vposition'
    elif out_socket == node.outputs[5]: # Window
        # TODO: Don't use gl_FragCoord here, it uses different axes on different graphics APIs
        state.frag.add_uniform('vec2 screenSize', link='_screenSize')
        state.dxdy_varying_input_value = True
        return f'vec3(gl_FragCoord.xy / screenSize, 0.0)'
    elif out_socket == node.outputs[6]: # Reflection
        if state.context == ParserContext.WORLD:
            state.dxdy_varying_input_value = True
            return 'n'
        return 'vec3(0.0)'


def parse_uvmap(node: bpy.types.ShaderNodeUVMap, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    # instance = node.from_instance
    state.con.add_elem('tex', 'short2norm')
    mat = c.mat_get_material()
    mat_users = c.mat_get_material_users()

    state.dxdy_varying_input_value = True

    if mat_users is not None and mat in mat_users:
        mat_user = mat_users[mat][0]
        if hasattr(mat_user.data, 'uv_layers'):
            layers = mat_user.data.uv_layers
            # Second UV map referenced
            if len(layers) > 1 and node.uv_map == layers[1].name:
                state.con.add_elem('tex1', 'short2norm')
                return 'vec3(texCoord1.x, 1.0 - texCoord1.y, 0.0)'

    return 'vec3(texCoord.x, 1.0 - texCoord.y, 0.0)'


def parse_fresnel(node: bpy.types.ShaderNodeFresnel, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    state.curshader.add_function(c_functions.str_fresnel)
    ior = c.parse_value_input(node.inputs[0])
    if node.inputs[1].is_linked:
        dotnv = 'dot({0}, vVec)'.format(c.parse_vector_input(node.inputs[1]))
    else:
        dotnv = 'dotNV'

    state.dxdy_varying_input_value = True
    return 'fresnel({0}, {1})'.format(ior, dotnv)


def parse_layerweight(node: bpy.types.ShaderNodeLayerWeight, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    blend = c.parse_value_input(node.inputs[0])
    if node.inputs[1].is_linked:
        dotnv = 'dot({0}, vVec)'.format(c.parse_vector_input(node.inputs[1]))
    else:
        dotnv = 'dotNV'

    state.dxdy_varying_input_value = True

    # Fresnel
    if out_socket == node.outputs[0]:
        state.curshader.add_function(c_functions.str_fresnel)
        return 'fresnel(1.0 / (1.0 - {0}), {1})'.format(blend, dotnv)
    # Facing
    elif out_socket == node.outputs[1]:
        return '(1.0 - pow({0}, ({1} < 0.5) ? 2.0 * {1} : 0.5 / (1.0 - {1})))'.format(dotnv, blend)


def parse_lightpath(node: bpy.types.ShaderNodeLightPath, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    # https://github.com/blender/blender/blob/master/source/blender/gpu/shaders/material/gpu_shader_material_light_path.glsl
    if out_socket == node.outputs['Is Camera Ray']:
        return '1.0'
    elif out_socket == node.outputs['Is Shadow Ray']:
        return '0.0'
    elif out_socket == node.outputs['Is Diffuse Ray']:
        return '1.0'
    elif out_socket == node.outputs['Is Glossy Ray']:
        return '1.0'
    elif out_socket == node.outputs['Is Singular Ray']:
        return '0.0'
    elif out_socket == node.outputs['Is Reflection Ray']:
        return '0.0'
    elif out_socket == node.outputs['Is Transmission Ray']:
        return '0.0'
    elif out_socket == node.outputs['Ray Length']:
        return '1.0'
    elif out_socket == node.outputs['Ray Depth']:
        return '0.0'
    elif out_socket == node.outputs['Diffuse Depth']:
        return '0.0'
    elif out_socket == node.outputs['Glossy Depth']:
        return '0.0'
    elif out_socket == node.outputs['Transparent Depth']:
        return '0.0'
    elif out_socket == node.outputs['Transmission Depth']:
        return '0.0'

    log.warn(f'Light Path node: unsupported output {out_socket.identifier}.')
    return '0.0'


def parse_value(node: bpy.types.ShaderNodeValue, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    if node.arm_material_param:
        nn = 'param_' + c.node_name(node.name)
        value = node.outputs[0].default_value
        is_arm_mat_param = True
        state.curshader.add_uniform('float {0}'.format(nn), link='{0}'.format(node.name), default_value=value, is_arm_mat_param=is_arm_mat_param)
        return nn
    else:
        return c.to_vec1(node.outputs[0].default_value)


def parse_wireframe(node: bpy.types.ShaderNodeWireframe, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    # node.use_pixel_size
    # size = c.parse_value_input(node.inputs[0])
    return '0.0'
