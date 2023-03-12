import bpy

import arm.utils
from arm.logicnode.arm_nodes import *


class CallGroupNode(ArmLogicTreeNode):
    """Calls the given group of nodes."""
    bl_idname = 'LNCallGroupNode'
    bl_label = 'Call Node Group'
    arm_section = 'group'
    arm_version = 3

    def __init__(self):
        self.register_id()

    def arm_init(self, context):
        pass

    # Function to add input sockets and re-link sockets
    def update_inputs(self, tree, node, inp_sockets, in_links):
        count = 0
        for output in node.outputs:
            _, c_socket = arm.node_utils.output_get_connected_node(output)
            if c_socket is not None:
                current_socket = self.add_input(c_socket.bl_idname, output.name)
                if(count < len(in_links)):
                    # Preserve default values in input sockets
                    inp_sockets[count].copy_defaults(current_socket)
                    for link in in_links[count]:
                        tree.links.new(link, current_socket)
            else:
                current_socket = self.add_input('ArmAnySocket', output.name)
                current_socket.display_label = output.name
                if(count < len(in_links)):
                    for link in in_links[count]:
                        tree.links.new(link, current_socket)
            count = count + 1

    # Function to add output sockets and re-link sockets
    def update_outputs(self, tree, node, out_links):
        count = 0
        for input in node.inputs:
            _, c_socket = arm.node_utils.input_get_connected_node(input)
            if c_socket is not None:
                current_socket = self.add_output(c_socket.bl_idname, input.name)
                if(count < len(out_links)):
                    for link in out_links[count]:
                        nlink = tree.links.new(current_socket, link)
                        nlink.is_valid = True
                        nlink.is_muted = False
            else:
                current_socket = self.add_output('ArmAnySocket', input.name)
                current_socket.display_label = input.name
                if(count < len(out_links)):
                    for link in out_links[count]:
                        tree.links.new(current_socket, link)
            count = count + 1
    
    def remove_tree(self):
        self.group_tree = None

    def update_sockets(self, context):
        # List to store from and to sockets of connected nodes
        from_socket_list = []
        to_socket_list = []
        inp_socket_list = []
        tree = self.get_tree()

        # Loop through each input socket
        for inp in self.inputs:
            link_per_socket = []
            #Loop through each link to the socket
            for link in inp.links:
                link_per_socket.append(link.from_socket)
            from_socket_list.append(link_per_socket)
            inp_socket_list.append(inp)

        # Loop through each output socket
        for out in self.outputs:
            link_per_socket = []
            # Loop through each link to the socket
            for link in out.links:
                link_per_socket.append(link.to_socket)
            to_socket_list.append(link_per_socket)

        # Remove all output sockets
        for output in self.outputs:
            self.outputs.remove(output)
        # Search for Group Input/Output
        if self.group_tree is not None:
            for node in self.group_tree.nodes:
                if node.bl_idname == 'LNGroupInputsNode':
                    # Update input sockets
                    self.update_inputs(tree, node, inp_socket_list, from_socket_list)
                    break
            for node in self.group_tree.nodes:
                if node.bl_idname == 'LNGroupOutputsNode':
                    # Update output sockets
                    self.update_outputs(tree, node, to_socket_list)
                    break
        #Remove all old input sockets after setting defaults
        for inp in inp_socket_list:
            self.inputs.remove(inp)

    # Prperty to store group tree pointer
    group_tree: PointerProperty(name='Group', type=bpy.types.NodeTree, update=update_sockets)

    def draw_label(self) -> str:
        if self.group_tree is not None:
            return f'Group: {self.group_tree.name}'
        return self.bl_label

    # Draw node UI
    def draw_buttons(self, context, layout):
        col = layout.column()
        row_name = col.row(align=True)
        row_add = col.row(align=True)
        row_ops = col.row()
        if self.group_tree is None:
            op = row_add.operator('arm.add_group_tree', icon='PLUS', text='New Group')
            op.node_index = self.get_id_str()
        op = row_name.operator('arm.search_group_tree', text='', icon='VIEWZOOM')
        op.node_index = self.get_id_str()
        if self.group_tree:
            row_name.prop(self.group_tree, 'name', text='')
            row_copy = row_name.split(align=True)
            row_copy.alignment = 'CENTER'
            fake_user = 1 if self.group_tree.use_fake_user else 0
            op = row_copy.operator('arm.copy_group_tree', text=str(self.group_tree.users - fake_user))
            op.node_index = self.get_id_str()
            row_name.prop(self.group_tree, 'use_fake_user', text='')
            op = row_name.operator('arm.node_call_func', icon='X', text='')
            op.node_index = self.get_id_str()
            op.callback_name = 'remove_tree'
        row_ops.enabled = not self.group_tree is None
        op = row_ops.operator('arm.edit_group_tree', icon='FULLSCREEN_ENTER', text='Edit tree')
        op.node_index = self.get_id_str()

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1, 2):
            raise LookupError()

        return node_tree.nodes.new('LNCallGroupNode')