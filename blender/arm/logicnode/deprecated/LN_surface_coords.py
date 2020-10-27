from arm.logicnode.arm_nodes import *

class SurfaceCoordsNode(ArmLogicTreeNode):
    """Deprecated. Is recommended to use 'Get Touch Location' and 'Get Touch Movement' node instead."""
    bl_idname = 'LNSurfaceCoordsNode'
    bl_label = 'Surface Coords'
    bl_description = "Please use the \"Get Touch Movement\" and \"Get Touch Location\" nodes instead"
    bl_icon = 'ERROR'
    arm_category = 'input'
    arm_section = 'surface'
    arm_is_obsolete = 'is_obsolete'
    arm_version = 2

    def init(self, context):
        super(SurfaceCoordsNode, self).init(context)
        self.add_output('NodeSocketVector', 'Coords')
        self.add_output('NodeSocketVector', 'Movement')
