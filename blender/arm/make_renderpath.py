import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import sys
import json
import platform
import subprocess
import arm.make_compositor as make_compositor
import arm.assets as assets
import arm.utils
import arm.nodes as nodes

def build_node_trees(assets_path):
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    fp = os.path.sep.join(s)
    os.chdir(fp)

    rpdat = arm.utils.get_rp()

    # Make sure Assets dir exists
    if not os.path.exists(arm.utils.build_dir() + '/compiled/Assets/renderpaths'):
        os.makedirs(arm.utils.build_dir() + '/compiled/Assets/renderpaths')
    
    build_node_trees.assets_path = assets_path
    if rpdat.arm_material_model != 'Mobile':
        # Always include
        assets.add(assets_path + 'brdf.png')
        assets.add_embedded_data('brdf.png')
    
    node_group = bpy.data.node_groups['armory_default']
    build_node_tree(rpdat, node_group)

def build_node_tree(rpdat, node_group):
    build_node_tree.rpdat = rpdat
    output = {}
    dat = {}
    output['renderpath_datas'] = [dat]
    
    path = arm.utils.build_dir() + '/compiled/Assets/renderpaths/'
    node_group_name = node_group.name.replace('.', '_')
    
    rn = get_root_node(node_group)
    if rn == None:
        return

    dat['name'] = node_group_name

    # Store main context names
    dat['mesh_context'] = 'mesh'
    dat['shadows_context'] = 'shadowmap'
    
    dat['render_targets'], dat['depth_buffers'] = preprocess_renderpath(rn, node_group)
    dat['stages'] = []
    
    buildNode(dat['stages'], rn, node_group)

    asset_path = path + node_group_name + '.arm'
    arm.utils.write_arm(asset_path, output)
    assets.add(asset_path)

def make_set_target(stage, node_group, node, currentNode=None, target_index=1, viewport_scale=1.0):
    if currentNode == None:
        currentNode = node
    
    stage['command'] = 'set_target'

    # First param is viewport scale
    if len(stage['params']) == 0:
        stage['params'].append(str(viewport_scale))

    currentNode = nodes.find_node_by_link(node_group, currentNode, currentNode.inputs[target_index])
    
    if currentNode.bl_idname == 'TargetNodeType' or currentNode.bl_idname == 'ShadowMapNodeType':
        targetId = currentNode.inputs[0].default_value
        stage['params'].append(targetId)
        # Store current target size
        buildNode.last_set_target_w = currentNode.inputs[1].default_value
        buildNode.last_set_target_h = currentNode.inputs[2].default_value
    
    elif currentNode.bl_idname == 'GBufferNodeType':
        # Set all linked targets
        for i in range(0, 5):
            if currentNode.inputs[i].is_linked:
                make_set_target(stage, node_group, node, currentNode, target_index=i)
    
    elif currentNode.bl_idname == 'NodeReroute':
        make_set_target(stage, node_group, node, currentNode, target_index=0)
    
    else: # Framebuffer
        targetId = ''
        stage['params'].append(targetId)

def make_set_viewport(stage, node_group, node):
    stage['command'] = 'set_viewport'
    stage['params'].append(node.inputs[1].default_value) # W
    stage['params'].append(node.inputs[2].default_value) # H

def make_clear_target(stage, color_val=None, depth_val=None, stencil_val=None):
    stage['command'] = 'clear_target'
    if color_val != None:
        stage['params'].append('color')
        if color_val == -1: # Clear to world background color
            stage['params'].append('-1')
        else:
            stage['params'].append(str(arm.utils.to_hex(color_val)))
    if depth_val != None:
        stage['params'].append('depth')
        stage['params'].append(str(depth_val))
    if stencil_val != None:
        stage['params'].append('stencil')
        stage['params'].append(str(stencil_val))

def make_clear_image(stage, image_name, color_val):
    stage['command'] = 'clear_image'
    stage['params'].append(image_name)
    stage['params'].append(str(arm.utils.to_hex(color_val)))

def make_generate_mipmaps(stage, node_group, node):
    stage['command'] = 'generate_mipmaps'

    # TODO: support reroutes
    link = nodes.find_link(node_group, node, node.inputs[1])
    targetNode = link.from_node

    stage['params'].append(targetNode.inputs[0].default_value)

def make_draw_meshes(stage, node_group, node):
    stage['command'] = 'draw_meshes'
    # Context
    context = node.inputs[1].default_value
    # Store shadowmap size
    if context == 'shadowmap':
        bpy.data.worlds['Arm'].arm_shadowmap_size_cache = buildNode.last_set_target_w
    stage['params'].append(context)
    # Order
    order = node.inputs[2].default_value
    stage['params'].append(order)

def make_draw_rects(stage, node_group, node):
    stage['command'] = 'draw_rects'
    context = node.inputs[1].default_value
    stage['params'].append(context)
 
def make_draw_decals(stage, node_group, node):
    stage['command'] = 'draw_decals'
    context = node.inputs[1].default_value
    stage['params'].append(context)

def make_bind_target(stage, node_group, node, constant_name, currentNode=None, target_index=1):
    if currentNode == None:
        currentNode = node
        
    stage['command'] = 'bind_target'
    
    link = nodes.find_link(node_group, currentNode, currentNode.inputs[target_index])
    currentNode = link.from_node
    
    if currentNode.bl_idname == 'NodeReroute':
        make_bind_target(stage, node_group, node, constant_name, currentNode=currentNode, target_index=0)
    
    elif currentNode.bl_idname == 'GBufferNodeType':
        for i in range(0, 5):
            if currentNode.inputs[i].is_linked:
                targetNode = nodes.find_node_by_link(node_group, currentNode, currentNode.inputs[i])
                targetId = targetNode.inputs[0].default_value
                # if i == 0 and targetNode.inputs[3].default_value == True: # Depth
                if targetNode.inputs[3].is_linked: # Depth
                    db_node = nodes.find_node_by_link(node_group, targetNode, targetNode.inputs[3])
                    db_id = db_node.inputs[0].default_value
                    stage['params'].append('_' + db_id)
                    stage['params'].append(constant_name + 'D')
                stage['params'].append(targetId) # Color buffer
                stage['params'].append(constant_name + str(i))
    
    elif currentNode.bl_idname == 'TargetNodeType' or currentNode.bl_idname == 'ImageNodeType' or currentNode.bl_idname == 'Image3DNodeType':     
        targetId = currentNode.inputs[0].default_value
        stage['params'].append(targetId)
        stage['params'].append(constant_name)

    elif currentNode.bl_idname == 'ShadowMapNodeType':
        targetId = currentNode.inputs[0].default_value
        stage['params'].append(targetId)
        stage['params'].append(constant_name)
        
    elif currentNode.bl_idname == 'DepthBufferNodeType':
        targetId = '_' + currentNode.inputs[0].default_value
        stage['params'].append(targetId)
        stage['params'].append(constant_name)

def make_draw_material_quad(stage, node_group, node, context_index=1):
    stage['command'] = 'draw_material_quad'
    material_context = node.inputs[context_index].default_value
    stage['params'].append(material_context)
    # Include data and shaders
    shader_context = node.inputs[context_index].default_value
    scon = shader_context.split('/')
    dir_name = scon[2]
    # No world defs for material passes
    data_name = scon[2]
    assets.add_shader2(dir_name, data_name)

def make_draw_quad(stage, node_group, node, context_index=1, shader_context=None):
    stage['command'] = 'draw_shader_quad'
    # Append world defs to get proper context
    wrd = bpy.data.worlds['Arm']
    world_defs = wrd.world_defs
    if shader_context == None:
        shader_context = node.inputs[context_index].default_value
    scon = shader_context.split('/')
    stage['params'].append(scon[0] + world_defs + '/' + scon[1] + world_defs + '/' + scon[2])
    # Include data and shaders
    dir_name = scon[0]
    # Append world defs
    data_name = scon[1] + world_defs
    assets.add_shader2(dir_name, data_name)

def make_draw_world(stage, node_group, node, dome=True):
    if dome:
        stage['command'] = 'draw_skydome'
    else:
        stage['command'] = 'draw_material_quad'
    # stage['params'].append(wname + '_material/' + wname + '_material/world')
    stage['params'].append('_worldMaterial') # Link to active world
    # Link assets
    if '_EnvClouds' in bpy.data.worlds['Arm'].world_defs:
        assets.add(build_node_trees.assets_path + 'noise256.png')
        assets.add_embedded_data('noise256.png')

def make_draw_compositor(stage, node_group, node, with_fxaa=False):
    scon = 'compositor_pass'
    wrd = bpy.data.worlds['Arm']
    world_defs = wrd.world_defs
    compositor_defs = make_compositor.parse_defs(bpy.data.scenes[0].node_tree) # Thrown in scene 0 for now
    compositor_defs += '_CTone' + wrd.arm_tonemap
    # Additional compositor flags
    compo_depth = False # Read depth
    # compo_pos = False # Construct position from depth
    if with_fxaa: # FXAA directly in compositor, useful for forward path
        compositor_defs += '_CFXAA'
    if wrd.arm_letterbox:
        compositor_defs += '_CLetterbox'
    if wrd.arm_grain:
        compositor_defs += '_CGrain'
    if bpy.data.scenes[0].cycles.film_exposure != 1.0:
        compositor_defs += '_CExposure'
    if wrd.arm_fog:
        compositor_defs += '_CFog'
        # compo_pos = True
    if len(bpy.data.cameras) > 0 and bpy.data.cameras[0].dof_distance > 0.0:
        compositor_defs += '_CDOF'
        compo_depth = True
    # if compo_pos:
        # compositor_defs += '_CPos'
        # compo_depth = True
    if compo_depth:
        compositor_defs += '_CDepth'

    if wrd.arm_lens_texture != '':
        compositor_defs += '_CLensTex'
        assets.add_embedded_data('lenstexture.jpg')

    if wrd.arm_fisheye:
        compositor_defs += '_CFishEye'

    if wrd.arm_vignette:
        compositor_defs += '_CVignette'

    wrd.compo_defs = compositor_defs

    defs = world_defs + compositor_defs
    data_name = scon + defs
    
    stage['command'] = 'draw_shader_quad'
    stage['params'].append(data_name + '/' + data_name + '/' + scon)
    # Include data and shaders
    assets.add_shader2(scon, data_name)
    # Link assets
    # assets.add(build_node_trees.assets_path + 'noise256.png')
    # assets.add_embedded_data('noise256.png')

def make_draw_grease_pencil(stage, node_group, node):
    stage['command'] = 'draw_grease_pencil'
    context = node.inputs[1].default_value
    stage['params'].append(context)

def make_call_function(stage, node_group, node):
    stage['command'] = 'call_function'
    fstr = node.inputs[1].default_value
    stage['params'].append(fstr)

def make_branch_function(stage, node_group, node):
    make_call_function(stage, node_group, node)
    
def process_call_function(stage, stages, node, node_group):
    # Step till merge node
    stage['returns_true'] = []
    if node.outputs[0].is_linked:
        stageNode = nodes.find_node_by_link_from(node_group, node, node.outputs[0])
        buildNode(stage['returns_true'], stageNode, node_group)
    
    stage['returns_false'] = []
    margeNode = None
    if node.outputs[1].is_linked:
        stageNode = nodes.find_node_by_link_from(node_group, node, node.outputs[1])
        margeNode = buildNode(stage['returns_false'], stageNode, node_group)
    
    # Continue using top level stages after merge node
    if margeNode != None:
        afterMergeNode = nodes.find_node_by_link_from(node_group, margeNode, margeNode.outputs[0])
        buildNode(stages, afterMergeNode, node_group)

def make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[3, 5, 7], bind_target_constants=None, shader_context=None, viewport_scale=1.0, with_clear=False, with_draw_quad=True):
    # Set target
    if target_index != None and node.inputs[target_index].is_linked:
        stage = {}
        stage['params'] = []
        make_set_target(stage, node_group, node, target_index=target_index, viewport_scale=viewport_scale)
        stages.append(stage)
    # Optinal clear
    if with_clear:
        stage = {}
        stage['params'] = []
        make_clear_target(stage, color_val=[0.0, 0.0, 0.0, 1.0])
        stages.append(stage)
    # Bind targets
    stage = {}
    stage['params'] = []
    buildNode.last_bind_target = stage
    bind_target_used = False
    for i in range(0, len(bind_target_indices)):
        index = bind_target_indices[i]
        if len(node.inputs) > index and node.inputs[index].is_linked:
            bind_target_used = True
            if bind_target_constants == None:
                constant_name = node.inputs[index + 1].default_value
            else:
                constant_name = bind_target_constants[i]
            make_bind_target(stage, node_group, node, constant_name, target_index=index)   
    if bind_target_used:
        stages.append(stage)
        stage = {}
        stage['params'] = []
    # Draw quad
    if with_draw_quad:
        make_draw_quad(stage, node_group, node, context_index=2, shader_context=shader_context)
        stages.append(stage)

def make_ssao_pass(stages, node_group, node):
    rpdat = build_node_tree.rpdat
    sc = 0.5 if rpdat.arm_ssao_half_res else 1.0
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[3, 4], bind_target_constants=['gbufferD', 'gbuffer0'], shader_context='ssao_pass/ssao_pass/ssao_pass', viewport_scale=sc)
    make_quad_pass(stages, node_group, node, target_index=2, bind_target_indices=[1, 4], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_x', viewport_scale=sc)
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2, 4], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_y')
    assets.add(build_node_trees.assets_path + 'noise8.png')
    assets.add_embedded_data('noise8.png')

def make_ssao_reproject_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[3, 4, 2, 5], bind_target_constants=['gbufferD', 'gbuffer0', 'slast', 'sveloc'], shader_context='ssao_reproject_pass/ssao_reproject_pass/ssao_reproject_pass')
    make_quad_pass(stages, node_group, node, target_index=2, bind_target_indices=[1, 4], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_x')
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2, 4], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_y')
    assets.add(build_node_trees.assets_path + 'noise8.png')
    assets.add_embedded_data('noise8.png')

def make_apply_ssao_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=2, bind_target_indices=[4, 5], bind_target_constants=['gbufferD', 'gbuffer0'], shader_context='ssao_pass/ssao_pass/ssao_pass')
    make_quad_pass(stages, node_group, node, target_index=3, bind_target_indices=[2, 5], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_x')
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[3, 5], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_y_blend')
    assets.add(build_node_trees.assets_path + 'noise8.png')
    assets.add_embedded_data('noise8.png')

def make_ssr_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=2, bind_target_indices=[4, 5, 6], bind_target_constants=['tex', 'gbufferD', 'gbuffer0'], shader_context='ssr_pass/ssr_pass/ssr_pass')
    make_quad_pass(stages, node_group, node, target_index=3, bind_target_indices=[2, 6], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_adaptive_pass/blur_adaptive_pass/blur_adaptive_pass_x')
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[3, 6], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_adaptive_pass/blur_adaptive_pass/blur_adaptive_pass_y3_blend')

def make_bloom_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=2, bind_target_indices=[4], bind_target_constants=['tex'], shader_context='bloom_pass/bloom_pass/bloom_pass')
    make_quad_pass(stages, node_group, node, target_index=3, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='blur_gaus_pass/blur_gaus_pass/blur_gaus_pass_x')
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[3], bind_target_constants=['tex'], shader_context='blur_gaus_pass/blur_gaus_pass/blur_gaus_pass_y_blend')

def make_motion_blur_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2, 3, 4], bind_target_constants=['tex', 'gbufferD', 'gbuffer0'], shader_context='motion_blur_pass/motion_blur_pass/motion_blur_pass')

def make_motion_blur_velocity_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2, 3, 4], bind_target_constants=['tex', 'gbuffer0', 'sveloc'], shader_context='motion_blur_veloc_pass/motion_blur_veloc_pass/motion_blur_veloc_pass')

def make_copy_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='copy_pass/copy_pass/copy_pass')

def make_materialid_to_depth(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='matid_to_depth/matid_to_depth/matid_to_depth')

def make_blend_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='blend_pass/blend_pass/blend_pass')

def make_combine_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2, 3], bind_target_constants=['tex', 'tex2'], shader_context='combine_pass/combine_pass/combine_pass')

def make_histogram_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='histogram_pass/histogram_pass/histogram_pass')

def make_blur_basic_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=2, bind_target_indices=[1], bind_target_constants=['tex'], shader_context='blur_pass/blur_pass/blur_pass_x')
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='blur_pass/blur_pass/blur_pass_y')

def make_debug_normals_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='debug_normals_pass/debug_normals_pass/debug_normals_pass')

def make_fxaa_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='fxaa_pass/fxaa_pass/fxaa_pass')

def make_ss_resolve(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='supersample_resolve/supersample_resolve/supersample_resolve')

def make_smaa_pass(stages, node_group, node):
    stage = {}
    stage['params'] = []
    make_set_target(stage, node_group, node, target_index=2)
    stages.append(stage)
    
    stage = {}
    stage['params'] = []
    make_clear_target(stage, color_val=[0.0, 0.0, 0.0, 0.0])
    stages.append(stage)
    
    make_quad_pass(stages, node_group, node, target_index=None, bind_target_indices=[4], bind_target_constants=['colorTex'], shader_context='smaa_edge_detect/smaa_edge_detect/smaa_edge_detect')
    
    stage = {}
    stage['params'] = []
    make_set_target(stage, node_group, node, target_index=3)
    stages.append(stage)

    stage = {}
    stage['params'] = []
    make_clear_target(stage, color_val=[0.0, 0.0, 0.0, 0.0])
    stages.append(stage)
    
    make_quad_pass(stages, node_group, node, target_index=None, bind_target_indices=[2], bind_target_constants=['edgesTex'], shader_context='smaa_blend_weight/smaa_blend_weight/smaa_blend_weight')
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[4, 3, 5], bind_target_constants=['colorTex', 'blendTex', 'sveloc'], shader_context='smaa_neighborhood_blend/smaa_neighborhood_blend/smaa_neighborhood_blend')
    assets.add(build_node_trees.assets_path + 'smaa_area.png')
    assets.add(build_node_trees.assets_path + 'smaa_search.png')
    assets.add_embedded_data('smaa_area.png')
    assets.add_embedded_data('smaa_search.png')

def make_taa_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2, 3, 4], bind_target_constants=['tex', 'tex2', 'sveloc'], shader_context='taa_pass/taa_pass/taa_pass')

def make_sss_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[3, 4, 5], bind_target_constants=['tex', 'gbufferD', 'gbuffer1'], shader_context='sss_pass/sss_pass/sss_pass_x')
    make_quad_pass(stages, node_group, node, target_index=2, bind_target_indices=[3, 4, 5], bind_target_constants=['tex', 'gbufferD', 'gbuffer1'], shader_context='sss_pass/sss_pass/sss_pass_y')

def make_water_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2, 3], bind_target_constants=['gbufferD', 'shadowMap'], shader_context='water_pass/water_pass/water_pass')

def make_deferred_light_pass(stages, node_group, node):
    rpdat = build_node_tree.rpdat
    if rpdat.arm_voxelgi_shadows or rpdat.arm_voxelgi_refraction:
        make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2, 3, 4], bind_target_constants=['gbuffer', 'shadowMap', 'voxels'], shader_context='', with_draw_quad=False)
    else:
        make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2, 3], bind_target_constants=['gbuffer', 'shadowMap'], shader_context='', with_draw_quad=False)
    stage = {}
    stage['command'] = 'call_function'
    stage['params'] = ['iron.data.RenderPath.lampIsSun']
    # Draw fs quad
    stage_true = {}
    stage_true['params'] = []
    make_draw_quad(stage_true, node_group, node, context_index=2, shader_context='deferred_light_quad/deferred_light_quad/deferred_light_quad')
    # Draw lamp volume
    stage_false = {}
    stage_false['params'] = []
    make_draw_quad(stage_false, node_group, node, context_index=2, shader_context='deferred_light/deferred_light/deferred_light')
    stage_false['command'] = 'draw_lamp_volume'
    stage['returns_true'] = [stage_true]
    stage['returns_false'] = [stage_false]
    stages.append(stage)

def make_volumetric_light_pass(stages, node_group, node):
    # make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[5, 6], bind_target_constants=['gbufferD', 'shadowMap'], shader_context='volumetric_light/volumetric_light/volumetric_light_blend')
    make_quad_pass(stages, node_group, node, target_index=2, bind_target_indices=[5, 6], bind_target_constants=['gbufferD', 'shadowMap'], shader_context='', with_draw_quad=False)
    stage = {}
    stage['command'] = 'call_function'
    stage['params'] = ['iron.data.RenderPath.lampIsSun']
    # Draw fs quad
    stage_true = {}
    stage_true['params'] = []
    make_draw_quad(stage_true, node_group, node, context_index=2, shader_context='volumetric_light_quad/volumetric_light_quad/volumetric_light_quad')
    # Draw lamp volume
    stage_false = {}
    stage_false['params'] = []
    make_draw_quad(stage_false, node_group, node, context_index=2, shader_context='volumetric_light/volumetric_light/volumetric_light')
    stage_false['command'] = 'draw_lamp_volume'
    stage['returns_true'] = [stage_true]
    stage['returns_false'] = [stage_false]
    stages.append(stage)
    # Blur
    make_quad_pass(stages, node_group, node, target_index=3, bind_target_indices=[2, 4], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_x')
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[3, 4], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_y_blend_add')

def make_deferred_indirect_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2, 3, 4], bind_target_constants=['gbuffer', 'ssaotex', 'voxels'], shader_context='deferred_indirect/deferred_indirect/deferred_indirect')

def make_translucent_resolve_pass(stages, node_group, node):
    make_quad_pass(stages, node_group, node, target_index=1, bind_target_indices=[2], bind_target_constants=['gbuffer'], shader_context='translucent_resolve/translucent_resolve/translucent_resolve')

# Returns merge node
def buildNode(stages, node, node_group):
    stage = {}
    stage['params'] = []
    
    append_stage = True
    
    if node.bl_idname == 'MergeStagesNodeType':
        return node
    
    elif node.bl_idname == 'SetTargetNodeType':
        buildNode.last_bind_target = None
        make_set_target(stage, node_group, node)

    elif node.bl_idname == 'SetViewportNodeType':
        make_set_viewport(stage, node_group, node)

    elif node.bl_idname == 'ClearTargetNodeType':
        color_val = None
        depth_val = None
        stencil_val = None
        if node.inputs[1].default_value == True:
            if node.inputs[2].is_linked: # Assume background color node is linked
                color_val = -1 # Clear to world.background_color
            else:
                color_val = node.inputs[2].default_value
        if node.inputs[3].default_value == True:
            depth_val = node.inputs[4].default_value
        if node.inputs[5].default_value == True:
            stencil_val = node.inputs[6].default_value
        make_clear_target(stage, color_val=color_val, depth_val=depth_val, stencil_val=stencil_val)
    
    elif node.bl_idname == 'ClearImageNodeType':
        image_node = node.inputs[1].links[0].from_node
        image_name = image_node.inputs[0].default_value
        color_val = node.inputs[2].default_value
        make_clear_image(stage, image_name, color_val)

    elif node.bl_idname == 'GenerateMipmapsNodeType':
        make_generate_mipmaps(stage, node_group, node)

    elif node.bl_idname == 'DrawMeshesNodeType':
        make_draw_meshes(stage, node_group, node)
    
    elif node.bl_idname == 'DrawRectsNodeType':
        make_draw_rects(stage, node_group, node)

    elif node.bl_idname == 'DrawDecalsNodeType':
        make_draw_decals(stage, node_group, node)
        
    elif node.bl_idname == 'BindTargetNodeType':
        if buildNode.last_bind_target is not None:
            stage = buildNode.last_bind_target
            append_stage = False
        buildNode.last_bind_target = stage
        constant_name = node.inputs[2].default_value
        make_bind_target(stage, node_group, node, constant_name)
        
    elif node.bl_idname == 'DrawMaterialQuadNodeType':
        make_draw_material_quad(stage, node_group, node)
        
    elif node.bl_idname == 'DrawQuadNodeType':
        make_draw_quad(stage, node_group, node)
    
    elif node.bl_idname == 'DrawWorldNodeType':
        # Bind depth for quad
        # if node.inputs[1].is_linked:
        #     stage = {}
        #     stage['params'] = []
        #     buildNode.last_bind_target = stage
        #     if node.inputs[1].is_linked:
        #         make_bind_target(stage, node_group, node, target_index=1, constant_name='gbufferD')
        #     stages.append(stage)
        stage = {}
        stage['params'] = []
        # Draw quad
        # make_draw_world(stage, node_group, node, dome=False)
        # Draw dome
        make_draw_world(stage, node_group, node, dome=True)
    
    elif node.bl_idname == 'DrawCompositorNodeType' or node.bl_idname == 'DrawCompositorWithFXAANodeType':
        # Set target
        if node.inputs[1].is_linked:
            make_set_target(stage, node_group, node)
            stages.append(stage)
        # Bind targets
        if node.inputs[2].is_linked or node.inputs[3].is_linked or node.inputs[4].is_linked or (len(node.inputs) > 5 and node.inputs[5].is_linked):
            stage = {}
            stage['params'] = []
            buildNode.last_bind_target = stage
            if node.inputs[2].is_linked:
                make_bind_target(stage, node_group, node, target_index=2, constant_name='tex')
            if node.inputs[3].is_linked:
                make_bind_target(stage, node_group, node, target_index=3, constant_name='gbufferD')
            if node.inputs[4].is_linked:
                make_bind_target(stage, node_group, node, target_index=4, constant_name='gbuffer0')
            if (len(node.inputs) > 5 and node.inputs[5].is_linked):
                make_bind_target(stage, node_group, node, target_index=5, constant_name='histogram')
            stages.append(stage)
        # Draw quad
        stage = {}
        stage['params'] = []
        with_fxaa = node.bl_idname == 'DrawCompositorWithFXAANodeType'
        make_draw_compositor(stage, node_group, node, with_fxaa=with_fxaa)
    
    elif node.bl_idname == 'DrawGreasePencilNodeType':
        stage = {}
        stage['params'] = []
        make_draw_grease_pencil(stage, node_group, node)

    elif node.bl_idname == 'BranchFunctionNodeType':
        make_branch_function(stage, node_group, node)
        stages.append(stage)
        process_call_function(stage, stages, node, node_group)
        return
        
    elif node.bl_idname == 'LoopStagesNodeType':
        # Just repeats the commands
        append_stage = False
        if node.outputs[1].is_linked:
            count = node.inputs[2].default_value
            for i in range(0, count):
                loopNode = nodes.find_node_by_link_from(node_group, node, node.outputs[1])
                buildNode(stages, loopNode, node_group)
    
    elif node.bl_idname == 'LoopLampsNodeType':
        append_stage = False
        stage['command'] = 'loop_lamps'
        stages.append(stage)
        stage['returns_true'] = []
        if node.outputs[1].is_linked:
            loopNode = nodes.find_node_by_link_from(node_group, node, node.outputs[1])
            buildNode(stage['returns_true'], loopNode, node_group)
    
    elif node.bl_idname == 'DrawStereoNodeType':
        append_stage = False
        stage['command'] = 'draw_stereo'
        stages.append(stage)
        stage['returns_true'] = []
        if node.outputs[1].is_linked:
            loopNode = nodes.find_node_by_link_from(node_group, node, node.outputs[1])
            buildNode(stage['returns_true'], loopNode, node_group)

    elif node.bl_idname == 'CallFunctionNodeType':
        make_call_function(stage, node_group, node)
    
    elif node.bl_idname == 'QuadPassNodeType':
        make_quad_pass(stages, node_group, node)
        append_stage = False

    elif node.bl_idname == 'SSAOPassNodeType':
        make_ssao_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'SSAOReprojectPassNodeType':
        make_ssao_reproject_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'ApplySSAOPassNodeType':
        make_apply_ssao_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'SSRPassNodeType':
        make_ssr_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'BloomPassNodeType':
        make_bloom_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'MotionBlurPassNodeType':
        make_motion_blur_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'MotionBlurVelocityPassNodeType':
        make_motion_blur_velocity_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'CopyPassNodeType':
        make_copy_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'MatIDToDepthNodeType':
        make_materialid_to_depth(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'BlendPassNodeType':
        make_blend_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'CombinePassNodeType':
        make_combine_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'HistogramPassNodeType':
        make_histogram_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'BlurBasicPassNodeType':
        make_blur_basic_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'DebugNormalsPassNodeType':
        make_debug_normals_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'FXAAPassNodeType':
        make_fxaa_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'SSResolveNodeType':
        make_ss_resolve(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'SMAAPassNodeType':
        make_smaa_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'TAAPassNodeType':
        make_taa_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'SSSPassNodeType':
        make_sss_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'WaterPassNodeType':
        make_water_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'DeferredLightPassNodeType':
        make_deferred_light_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'DeferredIndirectPassNodeType':
        make_deferred_indirect_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'VolumetricLightPassNodeType':
        make_volumetric_light_pass(stages, node_group, node)
        append_stage = False
    elif node.bl_idname == 'TranslucentResolvePassNodeType':
        make_translucent_resolve_pass(stages, node_group, node)
        append_stage = False

    if append_stage:
        stages.append(stage)
    
    # Build next stage
    if node.outputs[0].is_linked:
        stageNode = nodes.find_node_by_link_from(node_group, node, node.outputs[0])
        buildNode(stages, stageNode, node_group)

    return None

# Used to merge bind target nodes into one stage
buildNode.last_bind_target = None
# Used to determine shadowmap size
buildNode.last_set_target_w = 0
buildNode.last_set_target_h = 0

def get_root_node(node_group):
    # Find first node linked to begin node
    rn = None
    for n in node_group.nodes:
        if n.bl_idname == 'BeginNodeType':
            rn = nodes.find_node_by_link_from(node_group, n, n.outputs[0])
            break
    return rn

dynRes_added = False
def preprocess_renderpath(root_node, node_group):
    global dynRes_added
    dynRes_added = False
    render_targets = []
    render_targets3D = []
    depth_buffers = []
    preprocess_renderpath.velocity_def_added = False
    traverse_renderpath(root_node, node_group, render_targets, depth_buffers)
    return render_targets, depth_buffers
    
def traverse_renderpath(node, node_group, render_targets, depth_buffers):
    # Gather defs from linked nodes
    wrd = bpy.data.worlds['Arm']
    if node.bl_idname == 'TAAPassNodeType' or node.bl_idname == 'MotionBlurVelocityPassNodeType' or node.bl_idname == 'SSAOReprojectPassNodeType':
        if preprocess_renderpath.velocity_def_added == False:
            assets.add_khafile_def('arm_veloc')
            wrd.world_defs += '_Veloc'
            preprocess_renderpath.velocity_def_added = True
        if node.bl_idname == 'TAAPassNodeType':
            assets.add_khafile_def('arm_taa')
            # wrd.world_defs += '_TAA'
    elif node.bl_idname == 'SMAAPassNodeType':
        wrd.world_defs += '_SMAA'

    elif node.bl_idname == 'SSSPassNodeType':
        wrd.world_defs += '_SSS'

    elif node.bl_idname == 'HistogramPassNodeType':
        wrd.world_defs += '_Hist'

    elif node.bl_idname == 'SSAOPassNodeType' or node.bl_idname == 'ApplySSAOPassNodeType' or node.bl_idname == 'SSAOReprojectPassNodeType':
        wrd.world_defs += '_SSAO'

    elif node.bl_idname == 'DrawStereoNodeType':
        assets.add_khafile_def('arm_vr')
        wrd.world_defs += '_VR'
        assets.add(build_node_trees.assets_path + 'vr.png')
        assets.add_embedded_data('vr.png')

    elif node.bl_idname == 'CallFunctionNodeType':
        global dynRes_added
        fstr = node.inputs[1].default_value
        if not dynRes_added and fstr.startswith('armory.renderpath.DynamicResolutionScale'):
            wrd.world_defs += '_DynRes'
            dynRes_added = True

    # Collect render targets
    if node.bl_idname == 'SetTargetNodeType' or node.bl_idname == 'BindTargetNodeType' or node.bl_idname == 'QuadPassNodeType' or node.bl_idname == 'DrawCompositorNodeType' or node.bl_idname == 'DrawCompositorWithFXAANodeType':
        if node.inputs[1].is_linked:
            tnode = nodes.find_node_by_link(node_group, node, node.inputs[1])
            parse_render_target(tnode, node_group, render_targets, depth_buffers)

    # Traverse loops
    elif node.bl_idname == 'LoopStagesNodeType' or node.bl_idname == 'LoopLampsNodeType' or node.bl_idname == 'DrawStereoNodeType':
        if node.outputs[1].is_linked:
            loop_node = nodes.find_node_by_link_from(node_group, node, node.outputs[1])
            traverse_renderpath(loop_node, node_group, render_targets, depth_buffers)
    
    # Prebuilt
    elif node.bl_idname == 'MotionBlurPassNodeType' or node.bl_idname == 'MotionBlurVelocityPassNodeType' or node.bl_idname == 'CopyPassNodeType' or node.bl_idname == 'MatIDToDepthNodeType' or node.bl_idname == 'BlendPassNodeType' or node.bl_idname == 'CombinePassNodeType' or node.bl_idname == 'HistogramPassNodeType' or node.bl_idname == 'DebugNormalsPassNodeType' or node.bl_idname == 'FXAAPassNodeType' or node.bl_idname == 'SSResolveNodeType' or node.bl_idname == 'TAAPassNodeType' or node.bl_idname == 'WaterPassNodeType' or node.bl_idname == 'DeferredLightPassNodeType' or node.bl_idname == 'DeferredIndirectPassNodeType' or node.bl_idname == 'VolumetricLightPassNodeType' or node.bl_idname == 'TranslucentResolvePassNodeType':
        if node.inputs[1].is_linked:
            tnode = nodes.find_node_by_link(node_group, node, node.inputs[1])
            parse_render_target(tnode, node_group, render_targets, depth_buffers)
    elif node.bl_idname == 'SSRPassNodeType' or node.bl_idname == 'ApplySSAOPassNodeType' or node.bl_idname == 'BloomPassNodeType' or node.bl_idname == 'SMAAPassNodeType':
        for i in range(1, 4):
            if node.inputs[i].is_linked:
                tnode = nodes.find_node_by_link(node_group, node, node.inputs[i])
                parse_render_target(tnode, node_group, render_targets, depth_buffers)
    elif node.bl_idname == 'SSAOPassNodeType' or node.bl_idname == 'SSAOReprojectPassNodeType' or node.bl_idname == 'SSSPassNodeType' or node.bl_idname == 'BlurBasicPassNodeType':
        for i in range(1, 3):
            if node.inputs[i].is_linked:
                tnode = nodes.find_node_by_link(node_group, node, node.inputs[i])
                parse_render_target(tnode, node_group, render_targets, depth_buffers)

    # Next stage
    if node.outputs[0].is_linked:
        stagenode = nodes.find_node_by_link_from(node_group, node, node.outputs[0])
        traverse_renderpath(stagenode, node_group, render_targets, depth_buffers)
        
def parse_render_target(node, node_group, render_targets, depth_buffers):
    if node.bl_idname == 'NodeReroute':
        tnode = nodes.find_node_by_link(node_group, node, node.inputs[0])
        parse_render_target(tnode, node_group, render_targets, depth_buffers)
        
    elif node.bl_idname == 'TargetNodeType': # or node.bl_idname == 'ShadowMapNodeType': # Create SM dynamically instead
        # Target already exists
        id = node.inputs[0].default_value
        for t in render_targets:
            if t['name'] == id:
                return
        
        depth_buffer_id = None
        if node.bl_idname == 'TargetNodeType' and node.inputs[3].is_linked:
            # Find depth buffer
            depth_node = nodes.find_node_by_link(node_group, node, node.inputs[3])
            depth_buffer_id = depth_node.inputs[0].default_value
            # Append depth buffer
            found = False
            for db in depth_buffers:
                if db['name'] == depth_buffer_id:
                    found = True
                    break 
            if found == False:
                db = {}
                db['name'] = depth_buffer_id
                if depth_node.inputs[1] != '':
                    db['format'] = depth_node.inputs[1].default_value
                depth_buffers.append(db)    
        # Get scale
        scale = 1.0
        if node.inputs[1].is_linked: # Assume Screen node
            size_node = nodes.find_node_by_link(node_group, node, node.inputs[1])
            while size_node.bl_idname == 'NodeReroute': # Step through reroutes
                size_node = nodes.find_node_by_link(node_group, size_node, size_node.inputs[0])
            scale = size_node.inputs[0].default_value
            
        # Append target
        if node.bl_idname == 'TargetNodeType':
            target = make_render_target(node, scale, depth_buffer_id=depth_buffer_id)
            render_targets.append(target)
        else: # ShadowMapNodeType
            target = make_shadowmap_target(node, scale)
            render_targets.append(target)
    
    elif node.bl_idname == 'ImageNodeType' or node.bl_idname == 'Image3DNodeType':
        # Target already exists
        id = node.inputs[0].default_value
        for t in render_targets:
            if t['name'] == id:
                return

        # Get scale
        scale = 1.0
        if node.inputs[1].is_linked: # Assume Screen node
            size_node = nodes.find_node_by_link(node_group, node, node.inputs[1])
            while size_node.bl_idname == 'NodeReroute': # Step through reroutes
                size_node = nodes.find_node_by_link(node_group, size_node, size_node.inputs[0])
            scale = size_node.inputs[0].default_value

        if node.bl_idname == 'ImageNodeType':
            target = make_image_target(node, scale)
        else:
            target = make_image3d_target(node, scale)
        render_targets.append(target)

    elif node.bl_idname == 'GBufferNodeType':
        for i in range(0, 5):
            if node.inputs[i].is_linked:
                n = nodes.find_node_by_link(node_group, node, node.inputs[i])
                parse_render_target(n, node_group, render_targets, depth_buffers)

def make_render_target(n, scale, depth_buffer_id=None):
    target = {}
    target['name'] = n.inputs[0].default_value
    target['width'] = n.inputs[1].default_value
    target['height'] = n.inputs[2].default_value
    target['format'] = n.inputs[4].default_value
    if n.inputs[5].default_value:
        target['ping_pong'] = True
    if scale != 1.0:
        target['scale'] = scale    
    if depth_buffer_id != None:
        target['depth_buffer'] = depth_buffer_id
    # Manual resolution
    rpdat = build_node_tree.rpdat
    if target['width'] == 0 and rpdat.arm_rp_resolution != 'Display':
        target['displayp'] = int(rpdat.arm_rp_resolution)
    return target

def make_shadowmap_target(n, scale, postfix=''):
    target = {}
    target['name'] = n.inputs[0].default_value + postfix
    target['width'] = n.inputs[1].default_value
    target['height'] = n.inputs[2].default_value
    target['format'] = n.inputs[3].default_value
    if scale != 1.0:
        target['scale'] = scale    
    return target

def make_image_target(n, scale):
    target = {}
    target['is_image'] = True
    target['name'] = n.inputs[0].default_value
    target['width'] = n.inputs[1].default_value
    target['height'] = n.inputs[2].default_value
    target['format'] = n.inputs[3].default_value
    if scale != 1.0:
        target['scale'] = scale    
    return target

def make_image3d_target(n, scale):
    target = {}
    target['is_image'] = True
    target['name'] = n.inputs[0].default_value
    target['width'] = n.inputs[1].default_value
    target['height'] = n.inputs[2].default_value
    target['depth'] = n.inputs[3].default_value
    target['format'] = n.inputs[4].default_value
    if scale != 1.0:
        target['scale'] = scale    
    return target
