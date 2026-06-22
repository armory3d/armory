from arm.logicnode.arm_nodes import *

class GoToLocationNode(ArmLogicTreeNode):
    """Makes a NavMesh agent go to location.

    @input In: Start navigation.
    @input Object: The object to navigate. Object must have `NavAgent` trait applied.
    @input Location: Closest point on the navmesh to navigate to.
    @input Speed: Rate of movement.
    @input Turn Duration: Rate of turn.
    @input Height Offset: Height of the object from the navmesh.
    @input Use Raycast: Use physics ray cast to get more precise z positioning.
    @input Ray Cast Depth: Depth of ray cast from the object origin.
    @input Ray Cast Mask: Ray cast mask for collision detection.

    @output Out: Executed immidiately after start of the navigation.
    @output Tick Position: Executed at every step of navigation translation.
    @output Tick Rotation: Executed at every step of navigation rotation.
    """
    bl_idname = 'LNGoToLocationNode'
    bl_label = 'Go to Location'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmVectorSocket', 'Location')
        self.add_input('ArmFloatSocket', 'Speed', 5.0)
        self.add_input('ArmFloatSocket', 'Turn Duration', 0.4)
        self.add_input('ArmFloatSocket', 'Height Offset', 0.0)
        self.add_input('ArmBoolSocket','Use Raycast')
        self.add_input('ArmFloatSocket', 'Ray Cast Depth', -5.0)
        self.add_input('ArmIntSocket', 'Ray Cast Mask', 1)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Tick Position')
        self.add_output('ArmNodeSocketAction', 'Tick Rotation')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)

