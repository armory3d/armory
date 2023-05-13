from arm.logicnode.arm_nodes import *

class EvaluateRootMotionNode(ArmLogicTreeNode):
    """Calculates the root motion bone in an armature object."""
    bl_idname = 'LNEvaluateRootMotionNode'
    bl_label = 'Evaluate Root Motion'
    arm_version = 1

    property0: HaxeEnumProperty(
            'property0',
            items = [('X', 'X', 'X'),
                     ('Y', 'Y', 'Y'),
                     ('Z', 'Z', 'Z')],
            name='', default='Z')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Reset')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimTree', 'Action')
        
        self.add_input('ArmStringSocket', 'Bone')

        self.add_output('ArmNodeSocketAnimTree', 'Result')

    def draw_buttons(self, context, layout):
        layout.label(text='Root Motion Lock axis:')
        layout.prop(self, 'property0')