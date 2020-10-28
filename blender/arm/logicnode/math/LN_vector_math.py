from arm.logicnode.arm_nodes import *

class VectorMathNode(ArmLogicTreeNode):
    """Operates vectors. Some operations uses only the first input."""
    bl_idname = 'LNVectorMathNode'
    bl_label = 'Vector Math'
    arm_section = 'vector'
    arm_version = 1

    property0: EnumProperty(
        items = [('Add', 'Add', 'Add'),
                 ('Dot Product', 'Dot Product', 'Dot Product'),
                 ('Multiply', 'Multiply', 'Multiply'),
                 ('Normalize', 'Normalize', 'Normalize'),
                 ('Subtract', 'Subtract', 'Subtract'),
                 ('Average', 'Average', 'Average'),
                 ('Cross Product', 'Cross Product', 'Cross Product'),
                 ('Length', 'Length', 'Length'),
                 ('Distance', 'Distance', 'Distance'),
                 ('Reflect', 'Reflect', 'Reflect'),
                 ],
        name='', default='Add')

    def init(self, context):
        super(VectorMathNode, self).init(context)
        self.add_input('NodeSocketVector', 'Vector 1', default_value=[0.0, 0.0, 0.0])
        self.add_input('NodeSocketVector', 'Vector 2', default_value=[0.0, 0.0, 0.0])
        self.add_output('NodeSocketVector', 'Result')
        self.add_output('NodeSocketFloat', 'Distance')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
