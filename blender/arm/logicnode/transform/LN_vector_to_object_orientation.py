from arm.logicnode.arm_nodes import *

class VectorToObjectOrientationNode(ArmLogicTreeNode):
    """Transform world coordinates into object oriented coordinates (in other words: apply object rotation to it).

    @seeNode World Vector to Object Space
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

        self.add_output('NodeSocketVector', 'Oriented')
