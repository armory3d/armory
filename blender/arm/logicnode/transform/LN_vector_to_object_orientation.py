from arm.logicnode.arm_nodes import *

class VectorToObjectOrientationNode(ArmLogicTreeNode):
    """Converts the given world oriented vector to an object oriented vector. The object scale is taken in count.

    @seeNode Get World Orientation
    @seeNode Vector From Transform
    """
    bl_idname = 'LNVectorToObjectOrientationNode'
    bl_label = 'Vector to Object Orientation'
    arm_section = 'location'
    arm_version = 1

    def init(self, context):
        super(VectorToObjectOrientationNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'World')

        self.add_output('NodeSocketVector', 'Local')
