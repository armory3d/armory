from arm.logicnode.arm_nodes import *


@deprecated('Get Cursor Location')
class MouseCoordsNode(ArmLogicTreeNode):
    """Deprecated. It is recommended to use 'Get Cursor Location' node and the 'Get Mouse Movement' node instead."""
    bl_idname = 'LNMouseCoordsNode'
    bl_label = 'Mouse Coords'
    bl_description = "Please use the \"Get Cursor Location\" and \"Get Mouse Movement\" nodes instead"
    arm_category = 'Input'
    arm_section = 'mouse'
    arm_version = 2

    def arm_init(self, context):
        self.add_output('ArmVectorSocket', 'Coords')
        self.add_output('ArmVectorSocket', 'Movement')
        self.add_output('ArmIntSocket', 'Wheel')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        all_new_nodes = []
        if len(self.outputs[0].links) > 0:
            # "coords": use the cursor coordinates
            newmain = node_tree.nodes.new('LNGetCursorLocationNode')
            new_secondary = node_tree.nodes.new('LNVectorNode')
            node_tree.links.new(newmain.outputs[0], new_secondary.inputs[0])
            node_tree.links.new(newmain.outputs[1], new_secondary.inputs[1])
            for link in self.outputs[0].links:
                node_tree.links.new(new_secondary.outputs[0], link.to_socket)
            all_new_nodes += [newmain, new_secondary]

        if len(self.outputs[1].links) > 0 or len(self.outputs[2].links) > 0:
            # "movement": use the mouse movement
            # "wheel": use data from mouse movement as well
            newmain = node_tree.nodes.new('LNGetMouseMovementNode')
            all_new_nodes.append(newmain)
            if len(self.outputs[1].links) > 0:
                new_secondary = node_tree.nodes.new('LNVectorNode')
                all_new_nodes.append(new_secondary)
                node_tree.links.new(newmain.outputs[0], new_secondary.inputs[0])
                node_tree.links.new(newmain.outputs[1], new_secondary.inputs[1])
                for link in self.outputs[1].links:
                    node_tree.links.new(new_secondary.outputs[0], link.to_socket)

            for link in self.outputs[2].links:
                node_tree.links.new(newmain.outputs[2], link.to_socket)

        return all_new_nodes
