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
            if output.is_linked:
                self.add_input(output.links[0].to_socket.bl_idname, output.links[0].to_socket.name)
            else:
                self.add_input('ArmAnySocket', '')

    def update_outputs(self, node, context):
        for input in node.inputs:
            if input.is_linked:
                self.add_output(input.links[0].from_socket.bl_idname, input.links[0].from_socket.name)
            else:
                self.add_output('ArmAnySocket', '')

    def update_sockets(self, context):
        for input in self.inputs:
            self.inputs.remove(input)
        for output in self.outputs:
            self.outputs.remove(output)
        if self.property0_ is not None:
            for node in self.property0_.nodes:
                if (node.bl_idname == 'LNGroupInputNode'):
                    self.update_inputs(node, context)
                    break
            for node in self.property0_.nodes:
                if (node.bl_idname == 'LNGroupOutputNode'):
                    self.update_outputs(node, context)
                    break

    property0_: HaxePointerProperty('property0', name='Group', type=bpy.types.NodeTree, update=update_sockets)
    
    def arm_init(self, context):
        pass

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_', bpy.data, 'node_groups', icon='NONE', text='')
