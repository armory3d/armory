from arm.logicnode.arm_nodes import *

class DrawPolygonNode(ArmLogicTreeNode):
    """to do"""
    bl_idname = 'LNDrawPolygonNode'
    bl_label = 'Draw Polygon'
    arm_section = 'draw'
    arm_version = 1

    num_choices: IntProperty(default=1, min=0)
    
    def __init__(self):
        super(DrawPolygonNode, self).__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Activated/Desativated', default_value = True)
        self.add_input('ArmBoolSocket', 'Filled', default_value = False)
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'Strength')
        self.add_input('ArmIntSocket', 'X0')
        self.add_input('ArmIntSocket', 'Y0')

        self.add_output('ArmNodeSocketAction', 'Out')
    
    def add_sockets(self):
        self.add_input('ArmIntSocket', 'X'+str(self.num_choices))
        self.add_input('ArmIntSocket', 'Y'+str(self.num_choices))
        self.num_choices += 1
        
    def remove_sockets(self):
        if self.num_choices > 1:
            self.inputs.remove(self.inputs.values()[-1])    
            self.inputs.remove(self.inputs.values()[-1])
            self.num_choices -= 1
    
    def draw_buttons(self, context, layout):
        
        row = layout.row(align=True)
        
        op = row.operator('arm.node_call_func', text='Add Point', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'add_sockets'

        op = row.operator('arm.node_call_func', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'remove_sockets'
        