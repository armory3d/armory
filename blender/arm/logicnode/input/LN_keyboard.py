from arm.logicnode.arm_nodes import *

class KeyboardNode(ArmLogicTreeNode):
    """Keyboard node"""
    bl_idname = 'LNMergedKeyboardNode'
    bl_label = 'Keyboard'
    arm_version = 1

    property0: EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released')],
        name='', default='Started')

    property1: EnumProperty(
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
                 ('escape', 'escape', 'escape'),
                 ('delete', 'delete', 'delete'),
                 ('back', 'back', 'back'),
                 ('up', 'up', 'up'),
                 ('right', 'right', 'right'),
                 ('left', 'left', 'left'),
                 ('down', 'down', 'down'),],
        name='', default='space')

    def init(self, context):
        super(KeyboardNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketBool', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

add_node(KeyboardNode, category=PKG_AS_CATEGORY, section='keyboard')
