import bpy
from bpy.types import NodeTree
from bpy.props import *
import nodeitems_utils
from nodeitems_utils import NodeCategory
from arm.logicnode import *

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
        LogicNodeCategory('LogicEventNodes', 'Event', items=arm_nodes.category_items['Event']),
        LogicNodeCategory('LogicValueNodes', 'Value', items=arm_nodes.category_items['Value']),
        LogicNodeCategory('LogicVariableNodes', 'Variable', items=arm_nodes.category_items['Variable']),
        LogicNodeCategory('LogicLogicNodes', 'Logic', items=arm_nodes.category_items['Logic']),
        LogicNodeCategory('LogicOperatorNodes', 'Operator', items=arm_nodes.category_items['Operator']),
        LogicNodeCategory('LogicNativeNodes', 'Native', items=arm_nodes.category_items['Native']),
        LogicNodeCategory('LogicPhysicsNodes', 'Physics', items=arm_nodes.category_items['Physics']),
        LogicNodeCategory('LogicNavmeshNodes', 'Navmesh', items=arm_nodes.category_items['Navmesh']),
    ]

    nodeitems_utils.register_node_categories('ArmLogicNodes', node_categories)

def unregister_nodes():
    global registered_nodes
    for n in registered_nodes:
        bpy.utils.unregister_class(n)
    registered_nodes = []
    nodeitems_utils.unregister_node_categories('ArmLogicNodes')

def register():
    bpy.utils.register_class(ArmLogicTree)
    register_nodes()

def unregister():
    unregister_nodes()
    bpy.utils.unregister_class(ArmLogicTree)
