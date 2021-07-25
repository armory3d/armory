from arm.logicnode.arm_nodes import *

class OnInputMapNode(ArmLogicTreeNode):
    """Send a signal if any input map key is started or released."""
    bl_idname = 'LNOnInputMapNode'
    bl_label = 'On Input Map'
    arm_version = 1

    def init(self, context):
        super(OnInputMapNode, self).init(context)
        self.add_input('NodeSocketString', 'Input Map')

        self.add_output('ArmNodeSocketAction', 'Started')
        self.add_output('ArmNodeSocketAction', 'Released')
        self.add_output('NodeSocketFloat', 'Value')
        self.add_output('NodeSocketString', 'Key Pressed')