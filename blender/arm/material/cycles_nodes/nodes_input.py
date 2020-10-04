import bpy

import arm.material.cycles as cycles
from arm.material.shader import vec3str
import arm.utils


def parse_attribute(node: bpy.types.ShaderNodeAttribute, out_socket: bpy.types.NodeSocket) -> vec3str:
    # Color
    if out_socket == node.outputs[0]:
        # Vertex colors only for now
        cycles.con.add_elem('col', 'short4norm')
        return 'vcolor'

    # Vector
    else:
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


def parse_camera(node: bpy.types.ShaderNodeCameraData, out_socket: bpy.types.NodeSocket) -> vec3str:
    # View Vector in camera space
    return 'vVecCam'


def parse_geometry(node: bpy.types.ShaderNodeNewGeometry, out_socket: bpy.types.NodeSocket) -> vec3str:
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


def parse_hairinfo(node: bpy.types.ShaderNodeHairInfo, out_socket: bpy.types.NodeSocket) -> vec3str:
    # Tangent Normal
    return 'vec3(0.0)'


def parse_objectinfo(node: bpy.types.ShaderNodeObjectInfo, out_socket: bpy.types.NodeSocket) -> vec3str:
    return 'wposition'


def parse_particleinfo(node: bpy.types.ShaderNodeParticleInfo, out_socket: bpy.types.NodeSocket) -> vec3str:
    if out_socket == node.outputs[3]: # Location
        cycles.particle_info['location'] = True
        return 'p_location' if arm.utils.get_rp().arm_particles == 'On' else 'vec3(0.0)'
    elif out_socket == node.outputs[5]: # Velocity
        cycles.particle_info['velocity'] = True
        return 'p_velocity' if arm.utils.get_rp().arm_particles == 'On' else 'vec3(0.0)'
    elif out_socket == node.outputs[6]: # Angular Velocity
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
    #instance = node.from_instance
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
