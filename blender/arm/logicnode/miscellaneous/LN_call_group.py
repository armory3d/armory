import bpy

import arm.utils
from arm.logicnode.arm_nodes import *


class CallGroupNode(ArmLogicTreeNode):
    """Calls the given group of nodes."""
    bl_idname = 'LNCallGroupNode'
    bl_label = 'Call Node Group'
    arm_section = 'group'
    arm_version = 2

    @property
    def property0(self):
        return arm.utils.safesrc(bpy.data.worlds['Arm'].arm_project_package) + '.node.' + arm.utils.safesrc(self.property0_.name)

    def update_inputs(self, node, context):
        for output in node.outputs:
            _, c_socket = arm.node_utils.output_get_connected_node(output)
            if c_socket is not None:
                self.add_input(c_socket.bl_idname, c_socket.name)
            else:
                self.add_input('ArmAnySocket', '')

    def update_outputs(self, node, context):
        for inp in node.inputs:
            _, c_socket = arm.node_utils.input_get_connected_node(inp)
            if c_socket is not None:
                self.add_output(c_socket.bl_idname, c_socket.name)
            else:
                self.add_output('ArmAnySocket', '')

    def update_sockets(self, context):
        for inp in self.inputs:
            self.inputs.remove(inp)
        for output in self.outputs:
            self.outputs.remove(output)
        if self.property0_ is not None:
            for node in self.property0_.nodes:
                if node.bl_idname == 'LNGroupInputsNode':
                    self.update_inputs(node, context)
                    break
            for node in self.property0_.nodes:
                if node.bl_idname == 'LNGroupOutputsNode':
                    self.update_outputs(node, context)
                    break

    property0_: HaxePointerProperty('property0', name='Group', type=bpy.types.NodeTree, update=update_sockets)

    def arm_init(self, context):
        pass

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_', bpy.data, 'node_groups', icon='NONE', text='')

    @classmethod
    def update_all(cls):
        """Called by group input and group output nodes when all call
        node inputs should update their sockets.
        """
        for tree in bpy.data.node_groups:
            if tree.bl_idname == "ArmLogicTreeType":
                for node in tree.nodes:
                    if isinstance(node, cls):
                        node.update_sockets(bpy.context)
