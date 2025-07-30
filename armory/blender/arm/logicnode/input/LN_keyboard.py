from arm.logicnode.arm_nodes import *

class KeyboardNode(ArmLogicTreeNode):
    """Activates the output on the given keyboard button event."""
    bl_idname = 'LNMergedKeyboardNode'
    bl_label = 'Keyboard'
    arm_section = 'keyboard'
    arm_version = 2

    property0: HaxeEnumProperty(
        'property0',
        items = [('started', 'Started', 'The keyboard button starts to be pressed'),
                 ('down', 'Down', 'The keyboard button is pressed'),
                 ('released', 'Released', 'The keyboard button stops being pressed')],
        name='', default='down')

    property1: HaxeEnumProperty(
        'property1',
        items = [('a', 'a', 'a'),
                 ('b', 'b', 'b'),
                 ('c', 'c', 'c'),
                 ('d', 'd', 'd'),
                 ('e', 'e', 'e'),
                 ('f', 'f', 'f'),
                 ('g', 'g', 'g'),
                 ('h', 'h', 'h'),
                 ('i', 'i', 'i'),
                 ('j', 'j', 'j'),
                 ('k', 'k', 'k'),
                 ('l', 'l', 'l'),
                 ('m', 'm', 'm'),
                 ('n', 'n', 'n'),
                 ('o', 'o', 'o'),
                 ('p', 'p', 'p'),
                 ('q', 'q', 'q'),
                 ('r', 'r', 'r'),
                 ('s', 's', 's'),
                 ('t', 't', 't'),
                 ('u', 'u', 'u'),
                 ('v', 'v', 'v'),
                 ('w', 'w', 'w'),
                 ('x', 'x', 'x'),
                 ('y', 'y', 'y'),
                 ('z', 'z', 'z'),
                 ('0', '0', '0'),
                 ('1', '1', '1'),
                 ('2', '2', '2'),
                 ('3', '3', '3'),
                 ('4', '4', '4'),
                 ('5', '5', '5'),
                 ('6', '6', '6'),
                 ('7', '7', '7'),
                 ('8', '8', '8'),
                 ('9', '9', '9'),
                 ('.', 'period', 'period'),
                 (',', 'comma', 'comma'),
                 ('space', 'space', 'space'),
                 ('backspace', 'backspace', 'backspace'),
                 ('tab', 'tab', 'tab'),
                 ('enter', 'enter', 'enter'),
                 ('shift', 'shift', 'shift'),
                 ('control', 'control', 'control'),
                 ('alt', 'alt', 'alt'),
                 ('capslock', 'capslock', 'capslock'),
                 ('escape', 'escape', 'escape'),
                 ('delete', 'delete', 'delete'),
                 ('back', 'back', 'back'),
                 ('up', 'up', 'up'),
                 ('right', 'right', 'right'),
                 ('left', 'left', 'left'),
                 ('down', 'down', 'down'),],
        name='', default='space')

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmBoolSocket', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

    def draw_label(self) -> str:
        return f'{self.bl_label}: {self.property1}'

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)
