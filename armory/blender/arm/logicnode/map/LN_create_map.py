from arm.logicnode.arm_nodes import *

class CreateMapNode(ArmLogicTreeNode):
    """Create Map"""
    bl_idname = 'LNCreateMapNode'
    bl_label = 'Create Map'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('string', 'String', 'String Map Key Type'),
                 ('int', 'Int', 'Int Map key type'),
                 ('enumvalue', 'EnumValue', 'EnumValue Map key type'),
                 ('object', 'Object', 'Object Map key type')],
        name='Key',
        default='string')

    property1: HaxeEnumProperty(
        'property1',
        items = [('string', 'String', 'String Map Value Type'),
                 ('vector', 'Vector', 'Vector Map Value Type'),
                 ('float', 'Float', 'Float Map Value Type'),
                 ('integer', 'Integer', 'Integer Map Value Type'),
                 ('boolean', 'Boolean', 'Boolean Map Value Type'),
                 ('dynamic', 'Dynamic', 'Dynamic Map Value Type')],
        name='Value',
        default='string')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')


    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'Map')
