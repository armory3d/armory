import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *
import arm.utils

class MaterialNode(Node, ArmLogicTreeNode):
    '''Material node'''
    bl_idname = 'LNMaterialNode'
    bl_label = 'Material'
    bl_icon = 'QUESTION'

    @property
    def property0_get(self):
        if self.property0 == None:
            return ''
        if self.property0.name not in bpy.data.materials:
            return self.property0.name
        return arm.utils.asset_name(bpy.data.materials[self.property0.name])
    
    property0: PointerProperty(name='', type=bpy.types.Material)
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', 'Material')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, 'materials', icon='NONE', text='')

add_node(MaterialNode, category='Variable')
