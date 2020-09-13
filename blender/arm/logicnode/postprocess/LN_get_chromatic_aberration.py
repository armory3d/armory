from arm.logicnode.arm_nodes import *

class ChromaticAberrationGetNode(ArmLogicTreeNode):
    """Get Chromatic Aberration Effect"""
    bl_idname = 'LNChromaticAberrationGetNode'
    bl_label = 'Get ChromaticAberration'
    arm_version = 1

    def init(self, context):
        super(ChromaticAberrationGetNode, self).init(context)
        self.add_output('NodeSocketFloat', 'Strength')
        self.add_output('NodeSocketFloat', 'Samples')

add_node(ChromaticAberrationGetNode, category=PKG_AS_CATEGORY)
