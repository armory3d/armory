from arm.logicnode.arm_nodes import *

class CameraSetNode(ArmLogicTreeNode):
    """Set the post-processing effects of a camera."""
    bl_idname = 'LNCameraSetNode'
    bl_label = 'Set Camera Post Process'
    arm_version = 3

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'F-stop', default_value=1.0)#0
        self.add_input('ArmFloatSocket', 'Shutter Time', default_value=2.8333)#1
        self.add_input('ArmFloatSocket', 'ISO', default_value=100.0)#2
        self.add_input('ArmFloatSocket', 'Exposure Compensation', default_value=0.0)#3
        self.add_input('ArmFloatSocket', 'Fisheye Distortion', default_value=0.01)#4
        self.add_input('ArmBoolSocket', 'Auto Focus', default_value=True)#5
        self.add_input('ArmFloatSocket', 'DoF Distance', default_value=10.0)#6
        self.add_input('ArmFloatSocket', 'DoF Length', default_value=160.0)#7
        self.add_input('ArmFloatSocket', 'DoF F-Stop', default_value=128.0)#8
        self.add_input('ArmBoolSocket', 'Tonemapping', default_value=False)#9
        self.add_input('ArmFloatSocket', 'Distort', default_value=2.0)#10
        self.add_input('ArmFloatSocket', 'Film Grain', default_value=2.0)#11

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 2):
            raise LookupError()

        newnode = node_tree.nodes.new('LNCameraSetNode')

        for link in self.inputs[10].links:
            node_tree.links.new(newnode.inputs[10], link.to_socket)

        return newnode
