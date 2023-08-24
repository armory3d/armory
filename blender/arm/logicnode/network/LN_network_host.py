from arm.logicnode.arm_nodes import *


class NetworkHostNode(ArmLogicTreeNode):
    """Network host for other clients to connect"""
    bl_idname = 'LNNetworkHostNode'
    bl_label = 'Create Host'
    arm_version = 1
    ssl_ind = 4

    def update_ssl(self, context):
        """This is a helper method to allow declaring the `secure`
        property before the update_sockets() method. It's not required
        but then you would need to move the declaration of `secure`
        further down."""
        self.update_sockets(context)

    property0: HaxeBoolProperty(
        'property0',
        name="Secure",
        description="Enable SSL encryption",
        default=False,
        update=update_ssl
    )


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Domain',  default_value="127.0.0.1")
        self.add_input('ArmIntSocket', 'Port',  default_value=8001)
        self.add_input('ArmIntSocket', 'Max Conn.', default_value=25)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'Connection')

        self.update_sockets(context)

    def update_sockets(self, context):
        # It's bad to remove from a list during iteration so we use
        # this helper list here
        remove_list = []

        # Remove dynamically placed input sockets
        for i in range(NetworkHostNode.ssl_ind, len(self.inputs)):
            remove_list.append(self.inputs[i])
        for i in remove_list:
            self.inputs.remove(i)

        # Add dynamic input sockets
        if self.property0:
            self.add_input('ArmStringSocket', 'Certificate')
            self.add_input('ArmStringSocket', 'Private Key')


    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
    
    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        in_socket_mapping={0:0, 1:1, 2:2, 3:3}
        if self.property0:
            in_socket_mapping.update({4:4, 5:5})

        return NodeReplacement(
            'LNNetworkHostNode', self.arm_version, 'LNNetworkHostNode', 4,
            in_socket_mapping=in_socket_mapping,
            out_socket_mapping={0:0, 1:1},
            property_mapping={'property0':'property0'})
