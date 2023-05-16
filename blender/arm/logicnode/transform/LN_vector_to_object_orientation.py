from arm.logicnode.arm_nodes import *

class VectorToObjectOrientationNode(ArmLogicTreeNode):
    """Transform world coordinates into object oriented coordinates (in other words: apply object rotation to it).

    @seeNode World Vector to Object Space
    @seeNode Get World Orientation
    @seeNode Vector From Transform
    """
    bl_idname = 'LNVectorToObjectOrientationNode'
    bl_label = 'Vector to Object Orientation'
    arm_section = 'rotation'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmVectorSocket', 'World')

        self.add_output('ArmVectorSocket', 'Oriented')
