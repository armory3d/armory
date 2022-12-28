from bpy.types import NodeSocketInterfaceInt
from arm.logicnode.arm_nodes import *

class CaseIndexNode(ArmLogicTreeNode):
    """this node can be used as an input for the select node that takes numeric indixes when cases are dynamic values or as an input for anything that requieres a numeric index.

    @input dynamic: the value to be compared
    
    @input value: cases values for the dynamic comparison
    
    @output index: Returns the index of the case dynamic comparison
    
    """
    
    bl_idname = 'LNCaseIndexNode'
    bl_label = 'Case Index'
    arm_version = 1
    min_inputs = 2

    def update_exec_mode(self, context):
        self.set_mode()

    num_choices: IntProperty(default=1, min=0)

    def __init__(self):
        super().__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.set_mode()

    def set_mode(self):
  
        self.add_input('ArmDynamicSocket', 'Dynamic')
        self.num_choices = 0

        self.add_output('ArmDynamicSocket', 'Value')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_call_func', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'add_input_func'

        column = row.column(align=True)
        op = column.operator('arm.node_call_func', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'remove_input_func'
        if len(self.inputs) == self.min_inputs:
            column.enabled = False

    def add_input_func(self):
        self.add_input('ArmDynamicSocket', f'Value {self.num_choices}')

        self.num_choices += 1

    def remove_input_func(self):
        if len(self.inputs) > self.min_inputs:
            self.inputs.remove(self.inputs[-1])
            self.num_choices -= 1

    def draw_label(self) -> str:
        if self.num_choices == 0:
            return self.bl_label

        return f'{self.bl_label}: [{self.num_choices-1}]'

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)
