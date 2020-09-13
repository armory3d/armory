from arm.logicnode.arm_nodes import *

class VectorMathNode(ArmLogicTreeNode):
    """Vector math node"""
    bl_idname = 'LNVectorMathNode'
    bl_label = 'Vector Math'
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
        self.add_input('NodeSocketVector', 'Vector', default_value=[0.5, 0.5, 0.5])
        self.add_input('NodeSocketVector', 'Vector', default_value=[0.5, 0.5, 0.5])
        self.add_output('NodeSocketVector', 'Vector')
        self.add_output('NodeSocketFloat', 'Value')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(VectorMathNode, category=PKG_AS_CATEGORY, section='vector')
