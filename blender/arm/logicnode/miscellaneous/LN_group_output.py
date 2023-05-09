import bpy

import arm.utils
import arm.node_utils
from arm.logicnode.arm_nodes import *
import arm.logicnode.miscellaneous.LN_call_group as LN_call_group


class GroupOutputsNode(ArmLogicTreeNode):
    """Output for a node group."""
    bl_idname = 'LNGroupOutputsNode'
    bl_label = 'Group Output Node'
    arm_section = 'group'
    arm_version = 3

    def __init__(self):
        self.register_id()

    # Active socket selected
    active_input: IntProperty(name='active_input', description='', default=0)

    # Flag to store invalid links
    invalid_link: BoolProperty(name='invalid_link', description='', default=False)

    # Override copy prevention in certain situations such as copying entire group
    copy_override: BoolProperty(name='copy override', description='', default=False)

    def init(self, context):
        tree = bpy.context.space_data.edit_tree
        node_count = 0
        for node in tree.nodes:
            if node.bl_idname == 'LNGroupOutputsNode':
                node_count += 1
        if node_count > 1:
            arm.log.warn("Only one group output node per node tree is allowed")
            self.mute = True
        else:
            super().init(context)

    # Prevent copying of group node
    def copy(self, node):
        if not self.copy_override:
            self.mute = True
            self.inputs.clear()
        self.copy_override = False

    def arm_init(self, context):
        if not self.mute:
            self.add_socket()

    # Called when link is created
    def insert_link(self, link):
        to_socket = link.to_socket
        from_node = link.from_node
        from_socket = None
        # Recursively search for other socket in case of reroutes
        if from_node.type == 'REROUTE':
            _, from_socket = arm.node_utils.input_get_connected_node(to_socket)
        else:
            from_socket = link.from_socket
        if from_socket is not None:
            index = self.get_socket_index(to_socket)
            # If socket connected to ArmAnySocket, link is invalid
            if from_socket.bl_idname == 'ArmAnySocket':
                self.invalid_link = True
            else:
                call_group_nodes = self.get_call_group_nodes()
                for node in call_group_nodes:
                    # Change socket type according to the new link
                    node.change_output_socket(from_socket.bl_idname, index, link.to_socket.display_label)

    # Use update method to remove invalid links
    def update(self):
        super().update()
        if self.invalid_link:
            self.remove_invalid_links()

    # Called when name of the socket is changed
    def socket_name_update(self, socket):
        index = self.get_socket_index(socket)
        # Update socket names of the related call group nodes
        call_node_groups = self.get_call_group_nodes()
        for node in call_node_groups:
            out_socket = node.outputs[index]
            if out_socket.bl_idname == 'ArmAnySocket':
                out_socket.display_label = socket.display_label
            else:
                out_socket.name = socket.display_label

    # Recursively search and remove invalid links
    def remove_invalid_links(self):
        for input in self.inputs:
            for link in input.links:
                if link.from_socket.bl_idname == 'ArmAnySocket':
                    tree = self.get_tree()
                    tree.links.remove(link)
                    break
        self.invalid_link = False

    # Function to move socket up and handle the same in related call group nodes
    def move_socket_up(self):
        if self.active_input > 0:
            self.inputs.move(self.active_input, self.active_input - 1)
            call_node_groups = self.get_call_group_nodes()
            for nodes in call_node_groups:
                nodes.outputs.move(self.active_input, self.active_input - 1)
            self.active_input = self.active_input - 1

    # Function to move socket down and handle the same in related call group nodes
    def move_socket_down(self):
        if self.active_input < len(self.inputs) - 1:
            self.inputs.move(self.active_input, self.active_input + 1)
            call_node_groups = self.get_call_group_nodes()
            for nodes in call_node_groups:
                nodes.outputs.move(self.active_input, self.active_input + 1)
            self.active_input = self.active_input + 1

    # Function to recursively get related call group nodes
    def get_call_group_nodes(self):
        call_group_nodes = []
        # Return empty list if node is muted
        if self.mute:
            return call_group_nodes
        for tree in bpy.data.node_groups:
            if tree.bl_idname == "ArmLogicTreeType" or tree.bl_idname == "ArmGroupTree":
                for node in tree.nodes:
                    if node.bl_idname == 'LNCallGroupNode':
                        if node.group_tree == self.get_tree():
                            call_group_nodes.append(node)
        return call_group_nodes

    # Function to add a socket and handle the same in the related call group nodes
    def add_socket(self):
        self.add_input('ArmAnySocket','',)
        call_group_nodes = self.get_call_group_nodes()
        for node in call_group_nodes:
            node.add_output('ArmAnySocket','')

    # Function to remove a socket and handle the same in the related call group nodes
    def remove_socket(self):
        self.inputs.remove(self.inputs[-1])
        call_group_nodes = self.get_call_group_nodes()
        for node in call_group_nodes:
            node.outputs.remove(node.outputs[-1])
        if self.active_input > len(self.inputs) - 1:
            self.active_input = self.active_input - 1

    # Function to add a socket at certain index and 
    # handle the same in the related call group nodes
    def add_socket_ext(self):
        index = self.active_input + 1
        self.insert_input('ArmAnySocket', index, '')
        call_group_nodes = self.get_call_group_nodes()
        for node in call_group_nodes:
            node.insert_output('ArmAnySocket', index, '')

    # Function to remove a socket at certain index and 
    # handle the same in the related call group nodes
    def remove_socket_ext(self):
        self.inputs.remove(self.inputs[self.active_input])
        call_group_nodes = self.get_call_group_nodes()
        for node in call_group_nodes:
            node.outputs.remove(node.outputs[self.active_input])
        if self.active_input > len(self.inputs) - 1:
            self.active_input = len(self.inputs) - 1

    # Handle deletion of group input node
    def free(self):
        call_group_nodes = self.get_call_group_nodes()
        for node in call_group_nodes:
            node.outputs.clear()

    # Draw node UI
    def draw_buttons(self, context, layout):
        if self.mute:
            layout.enabled = False
        row = layout.row(align=True)
        op = row.operator('arm.node_call_func', text='New', icon='PLUS', emboss=True)
        op.node_index = self.get_id_str()
        op.callback_name = 'add_socket'
        if len(self.inputs) > 1:
            op2 = row.operator('arm.node_call_func', text='', icon='X', emboss=True)
            op2.node_index = self.get_id_str()
            op2.callback_name = 'remove_socket'

    # Draw side panel UI
    def draw_buttons_ext(self, context, layout):
        if self.mute:
            layout.enabled = False
        node = context.active_node
        split = layout.row()
        split.template_list('ARM_UL_interface_sockets', 'IN', node, 'inputs', node, 'active_input')
        ops_col = split.column()
        add_remove_col = ops_col.column(align=True)
        props = add_remove_col.operator('arm.node_call_func', icon='ADD', text="")
        props.node_index = self.get_id_str()
        props.callback_name = 'add_socket_ext'
        if len(self.inputs) > 1:
            props = add_remove_col.operator('arm.node_call_func', icon='REMOVE', text="")
            props.node_index = self.get_id_str()
            props.callback_name = 'remove_socket_ext'

        ops_col.separator()

        up_down_col = ops_col.column(align=True)
        props = up_down_col.operator('arm.node_call_func', icon='TRIA_UP', text="")
        props.node_index = self.get_id_str()
        props.callback_name = 'move_socket_up'
        props = up_down_col.operator('arm.node_call_func', icon='TRIA_DOWN', text="")
        props.node_index = self.get_id_str()
        props.callback_name = 'move_socket_down'

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1, 2):
            raise LookupError()

        return node_tree.nodes.new('LNGroupOutputsNode')