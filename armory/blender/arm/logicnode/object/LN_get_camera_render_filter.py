from arm.logicnode.arm_nodes import *

class GetCameraRenderFilterNode(ArmLogicTreeNode):
    """
    Gets Camera Render Filter array with the names of the cameras
    that can render the mesh. If null all cameras can render the mesh.
    """
    bl_idname = 'LNGetCameraRenderFilterNode'
    bl_label = 'Get Object Camera Render Filter'
    arm_section = 'camera'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketArray', 'Array')
