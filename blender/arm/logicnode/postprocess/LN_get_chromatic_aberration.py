from arm.logicnode.arm_nodes import *

class ChromaticAberrationGetNode(ArmLogicTreeNode):
    """Get Chromatic Aberration Effect"""
    bl_idname = 'LNChromaticAberrationGetNode'
    bl_label = 'Get ChromaticAberration'

    def init(self, context):
        self.add_output('NodeSocketFloat', 'Strength')
        self.add_output('NodeSocketFloat', 'Samples')

add_node(ChromaticAberrationGetNode, category=PKG_AS_CATEGORY)
