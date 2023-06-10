from arm.logicnode.arm_nodes import *


@deprecated('Set Canvas Color')
class CanvasSetProgressBarColorNode(ArmLogicTreeNode):
    """Sets the color of the given UI element."""
    bl_idname = 'LNCanvasSetProgressBarColorNode'
    bl_label = 'Set Canvas Progress Bar Color'
    arm_version = 2
    arm_category = 'Canvas'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        newnode = node_tree.nodes.new('LNCanvasSetColorNode')

        newnode.property0 = 'color_progress'

        NodeReplacement.replace_input_socket(node_tree, self.inputs[0], newnode.inputs[0])
        NodeReplacement.replace_input_socket(node_tree, self.inputs[1], newnode.inputs[1])
        NodeReplacement.replace_input_socket(node_tree, self.inputs[2], newnode.inputs[2])

        NodeReplacement.replace_output_socket(node_tree, self.outputs[0], newnode.outputs[0])

        return newnode
