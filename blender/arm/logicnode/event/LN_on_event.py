from arm.logicnode.arm_nodes import *

class OnEventNode(ArmLogicTreeNode):
    """Activates the output when the given event is received.

    @seeNode Send Event to Object
    @seeNode Send Global Event"""
    bl_idname = 'LNOnEventNode'
    bl_label = 'On Event'
    arm_version = 2
    arm_section = 'custom'

    operators = {
        'init': 'Init',
        'update': 'Update',
        'custom': 'Custom'
    }

    def set_mode(self, context):
        if self.property1 != 'custom':
            if len(self.inputs) > 1:
                self.inputs.remove(self.inputs[0])
        else:
            if len(self.inputs) < 2:
                self.add_input('ArmNodeSocketAction', 'In')
                self.inputs.move(1, 0)

    # Use a new property to preserve compatibility
    property1: HaxeEnumProperty(
        'property1',
        items=[
            ('init', 'Init', 'Assigns an Event listener at runtime'),
            ('update', 'Update', 'Assigns an Event listener continuously'),
            None,
            ('custom', 'Custom', 'Assigns an Event listener everytime input is detected'),
        ],
        name='',
        description='Chosen method for assigning an Event listener',
        default='init',
        update=set_mode
    )

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'String In')

        self.add_output('ArmNodeSocketAction', 'Out')

        self.set_mode(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property1', text='')

    def draw_label(self) -> str:
        return f'{self.bl_label}: {self.operators[self.property1]}'

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        newnode = node_tree.nodes.new('LNOnEventNode')
        
        try:
            newnode.inputs[0].default_value_raw = self["property0"]
        except:
            pass

        for link in self.outputs[0].links:
            node_tree.links.new(newnode.outputs[0], link.to_socket)

        return newnode
