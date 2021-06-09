from arm.logicnode.arm_nodes import *

class SetMaterialValueParamNode(ArmLogicTreeNode):
    """Set a float value material parameter to the specified object. If `per object` is disabled, value will be set to all objects with this material"""
    bl_idname = 'LNSetMaterialValueParamNode'
    bl_label = 'Set Material Value Param'
    arm_section = 'params'
    arm_version = 2

    property0: BoolProperty(
        name="Per Object",
        description="Set property per object",
        default=False
    )

    def init(self, context):
        super(SetMaterialValueParamNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Material')
        self.add_input('NodeSocketString', 'Node')
        self.add_input('NodeSocketFloat', 'Float')

        self.add_output('ArmNodeSocketAction', 'Out')
    
    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement(
            'LNSetMaterialValueParamNode', self.arm_version, 'LNSetMaterialValueParamNode', 2,
            in_socket_mapping={0:0, 1:2, 2:3, 3:4}, out_socket_mapping={0:0}
        )
