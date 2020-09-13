from arm.logicnode.arm_nodes import *

class GetRigidBodyDataNode(ArmLogicTreeNode):
    """Get Rigid Body Data node"""
    bl_idname = 'LNGetRigidBodyDataNode'
    bl_label = 'Get Rigid Body Data'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Rigid Body')
        #self.outputs.new('NodeSocketString', 'Collision Shape')
        self.outputs.new('NodeSocketInt', 'Collision Group')
        self.outputs.new('NodeSocketInt', 'Collision Mask')
        self.outputs.new('NodeSocketBool', 'Animated')
        self.outputs.new('NodeSocketBool', 'Static')
        self.outputs.new('NodeSocketFloat', 'Angular Damping')
        self.outputs.new('NodeSocketFloat', 'Linear Damping')
        self.outputs.new('NodeSocketFloat', 'Friction')
        self.outputs.new('NodeSocketFloat', 'Mass')

add_node(GetRigidBodyDataNode, category=PKG_AS_CATEGORY, section='props')
