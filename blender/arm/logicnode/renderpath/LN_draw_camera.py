from arm.logicnode.arm_nodes import *

class DrawCameraNode(ArmLogicTreeNode):
    """to do"""
    bl_idname = 'LNDrawCameraNode'
    bl_label = 'Draw Camera'
    arm_section = 'draw'
    arm_version = 1
    
    num_choices: IntProperty(default=2, min=0)
    
    def __init__(self):
        super(DrawCameraNode, self).__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Activated/Desativated', default_value = True)
        self.add_input('ArmNodeSocketObject', 'Camera 1 (Scene Active Camera)')
        self.add_input('ArmIntSocket', 'X')
        self.add_input('ArmIntSocket', 'Y')
        self.add_input('ArmIntSocket', 'W')
        self.add_input('ArmIntSocket', 'H')   

        self.add_output('ArmNodeSocketAction', 'Out')
            
    def add_sockets(self):
        self.add_input('ArmNodeSocketObject', 'Camera '+str(self.num_choices))
        self.add_input('ArmIntSocket', 'X')
        self.add_input('ArmIntSocket', 'Y')
        self.add_input('ArmIntSocket', 'W')
        self.add_input('ArmIntSocket', 'H')
        self.num_choices += 1
        
    def remove_sockets(self):
        if self.num_choices >= 3:
            self.inputs.remove(self.inputs.values()[-1])    
            self.inputs.remove(self.inputs.values()[-1])
            self.inputs.remove(self.inputs.values()[-1])
            self.inputs.remove(self.inputs.values()[-1])
            self.inputs.remove(self.inputs.values()[-1]) 
            self.num_choices -= 1
        
    def draw_buttons(self, context, layout):
        
        row = layout.row(align=True)
        
        op = row.operator('arm.node_call_func', text='Add Camera (X, Y, W, H)', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'add_sockets'

        op = row.operator('arm.node_call_func', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'remove_sockets'
        