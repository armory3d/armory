import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SceneRootNode(Node, ArmLogicTreeNode):
    '''Scene root node'''
    bl_idname = 'LNSceneRootNode'
    bl_label = 'Scene Root'
    bl_icon = 'QUESTION'
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(SceneRootNode, category='Variable')
