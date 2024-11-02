from arm.logicnode.arm_nodes import *

class RestartActionNode(ArmLogicTreeNode):
    """Restarts the action"""
    bl_idname = 'LNRestartActionNode'
    bl_label = 'Restart Action'
    bl_width_default = 200
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Action ID')
        
        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNRestartActionNode', self.arm_version, 'LNRestartActionNode', 2,
            in_socket_mapping={}, out_socket_mapping={}
        )
