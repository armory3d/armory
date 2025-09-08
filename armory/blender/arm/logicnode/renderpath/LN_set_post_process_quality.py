from arm.logicnode.arm_nodes import *

class RpConfigNode(ArmLogicTreeNode):
    """Sets the post process quality."""
    bl_idname = 'LNRpConfigNode'
    bl_label = 'Set Post Process Quality'
    arm_version = 2
    property0: HaxeEnumProperty(
        'property0',
        items = [('SSGI', 'SSGI', 'SSGI'),
                 ('SSR', 'SSR', 'SSR'),
                 ('Bloom', 'Bloom', 'Bloom'),
                 ('CA', 'CA', 'CA'),
                 ('GI', 'GI', 'GI'),
                 ('Motion Blur', 'Motion Blur', 'Motion Blur')
                 ],
        name='', default='SSGI')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Enable')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)

