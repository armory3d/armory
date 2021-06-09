from arm.logicnode.arm_nodes import *

class SetMaterialRgbParamNode(ArmLogicTreeNode):
    """Set a color or vector value material parameter to the specified object. If `per object` is disabled, value will be set to all objects with this material"""
    bl_idname = 'LNSetMaterialRgbParamNode'
    bl_label = 'Set Material RGB Param'
    arm_section = 'params'
    arm_version = 2

    property0: BoolProperty(
        name="Per Object",
        description="Set property per object",
        default=False
    )

    def init(self, context):
        super(SetMaterialRgbParamNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Material')
        self.add_input('NodeSocketString', 'Node')
        self.add_input('NodeSocketColor', 'Color')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement(
            'LNSetMaterialRgbParamNode', self.arm_version, 'LNSetMaterialRgbParamNode', 2,
            in_socket_mapping={0:0, 1:2, 2:3, 3:4}, out_socket_mapping={0:0}
        )
