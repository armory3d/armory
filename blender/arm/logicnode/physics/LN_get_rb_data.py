from arm.logicnode.arm_nodes import *

class GetRigidBodyDataNode(ArmLogicTreeNode):
    """Returns the data of the given rigid body."""
    bl_idname = 'LNGetRigidBodyDataNode'
    bl_label = 'Get RB Data'
    arm_version = 1

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Is RB')
        self.outputs.new('NodeSocketInt', 'Collision Group')
        self.outputs.new('NodeSocketInt', 'Collision Mask')
        self.outputs.new('NodeSocketBool', 'Is Animated')
        self.outputs.new('NodeSocketBool', 'Is Static')
        self.outputs.new('NodeSocketFloat', 'Angular Damping')
        self.outputs.new('NodeSocketFloat', 'Linear Damping')
        self.outputs.new('NodeSocketFloat', 'Friction')
        self.outputs.new('NodeSocketFloat', 'Mass')
        #self.outputs.new('NodeSocketString', 'Collision Shape')
        #self.outputs.new('NodeSocketInt', 'Activation State')
        #self.outputs.new('NodeSocketBool', 'Is Gravity Enabled')
        #self.outputs.new(NodeSocketVector', Angular Factor')
        #self.outputs.new('NodeSocketVector', Linear Factor')

add_node(GetRigidBodyDataNode, category=PKG_AS_CATEGORY, section='props')
