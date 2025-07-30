from arm.logicnode.arm_nodes import *

class SetParticleSpeedNode(ArmLogicTreeNode):
    """Sets the speed of the given particle source."""
    bl_idname = 'LNSetParticleSpeedNode'
    bl_label = 'Set Particle Speed'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmIntSocket', 'Slot')
        self.add_input('ArmFloatSocket', 'Speed', default_value=1.0)

        self.add_output('ArmNodeSocketAction', 'Out')


    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)
