import bpy
from bpy.types import NodeTree
from bpy.props import *
import nodeitems_utils
from nodeitems_utils import NodeCategory
from arm.logicnode import *
import webbrowser

registered_nodes = []

class ArmLogicTree(NodeTree):
    '''Logic nodes'''
    bl_idname = 'ArmLogicTreeType'
    bl_label = 'Logic Node Tree'
    bl_icon = 'GAME'

class LogicNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType'

def register_nodes():
    global registered_nodes

    # Re-register all nodes for now..
    if len(registered_nodes) > 0:
        unregister_nodes()

    for n in arm_nodes.nodes:
        registered_nodes.append(n)
        bpy.utils.register_class(n)

    node_categories = [
        LogicNodeCategory('LogicLogicNodes', 'Logic', items=arm_nodes.category_items['Logic']),
        LogicNodeCategory('LogicEventNodes', 'Event', items=arm_nodes.category_items['Event']),
        LogicNodeCategory('LogicActionNodes', 'Action', items=arm_nodes.category_items['Action']),
        LogicNodeCategory('LogicValueNodes', 'Value', items=arm_nodes.category_items['Value']),
        LogicNodeCategory('LogicVariableNodes', 'Variable', items=arm_nodes.category_items['Variable']),
        LogicNodeCategory('LogicInputNodes', 'Input', items=arm_nodes.category_items['Input']),
        LogicNodeCategory('LogicArrayNodes', 'Array', items=arm_nodes.category_items['Array']),
        LogicNodeCategory('LogicAnimationNodes', 'Animation', items=arm_nodes.category_items['Animation']),
        LogicNodeCategory('LogicPhysicsNodes', 'Physics', items=arm_nodes.category_items['Physics']),
        LogicNodeCategory('LogicNavmeshNodes', 'Navmesh', items=arm_nodes.category_items['Navmesh']),
        LogicNodeCategory('LogicSoundNodes', 'Sound', items=arm_nodes.category_items['Sound']),
        LogicNodeCategory('LogicNativeNodes', 'Native', items=arm_nodes.category_items['Native']),
        LogicNodeCategory('LogicCanvasNodes', 'Canvas', items=arm_nodes.category_items['Canvas']),
    ]

    nodeitems_utils.register_node_categories('ArmLogicNodes', node_categories)

def unregister_nodes():
    global registered_nodes
    for n in registered_nodes:
        bpy.utils.unregister_class(n)
    registered_nodes = []
    nodeitems_utils.unregister_node_categories('ArmLogicNodes')

class ArmLogicNodePanel(bpy.types.Panel):
    bl_label = 'Armory Logic Node'
    bl_idname = 'ArmLogicNodePanel'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        if context.active_node != None and context.active_node.bl_idname.startswith('LN'):
            layout.prop(context.active_node, 'arm_logic_id')
            layout.prop(context.active_node, 'arm_watch')
            layout.operator('arm.open_node_source')

class ArmOpenNodeSource(bpy.types.Operator):
    '''Expose Haxe source'''
    bl_idname = 'arm.open_node_source'
    bl_label = 'Open Node Source'
 
    def execute(self, context):
        if context.active_node != None and context.active_node.bl_idname.startswith('LN'):
            name = context.active_node.bl_idname[2:]
            webbrowser.open('https://github.com/armory3d/armory/tree/master/Sources/armory/logicnode/' + name + '.hx')
        return{'FINISHED'}

def register():
    bpy.utils.register_class(ArmLogicTree)
    bpy.utils.register_class(ArmLogicNodePanel)
    bpy.utils.register_class(ArmOpenNodeSource)
    register_nodes()

def unregister():
    unregister_nodes()
    bpy.utils.unregister_class(ArmLogicTree)
    bpy.utils.unregister_class(ArmLogicNodePanel)
    bpy.utils.unregister_class(ArmOpenNodeSource)
