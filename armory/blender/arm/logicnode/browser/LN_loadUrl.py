from arm.logicnode.arm_nodes import *

class LoadUrlNode(ArmLogicTreeNode):
    """Load the given URL in a new or existing tab (works only for web browsers).

    @input URL: use a complete url or partial for a subpage.
    @input New: open a new window or redirect existing one.
    @input Use values: W,H,L,T: open a new window using Width, Height, Left and Top values.
    @input Width: width for New window.
    @input Height: height for New window.
    @input Left: distance from left for New window position.
    @input Top: distance from top for New window position.

    @output True: for New returns true if the window is opened.
    @output False: for New returns false if the window is not opened (popup blocked).
    """
    bl_idname = 'LNLoadUrlNode'
    bl_label = 'Load URL'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'URL')
        self.add_input('ArmBoolSocket', 'New Window', default_value=True)
        self.add_input('ArmBoolSocket', 'Use values: W,H,L,T', default_value=False)
        self.add_input('ArmIntSocket', 'Width', default_value= 500)
        self.add_input('ArmIntSocket', 'Height', default_value= 500)
        self.add_input('ArmIntSocket', 'Left')
        self.add_input('ArmIntSocket', 'Top')
 
        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
