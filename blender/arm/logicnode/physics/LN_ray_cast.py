from arm.logicnode.arm_nodes import *

class RayCastNode(ArmLogicTreeNode):
    """Casts a physics ray and returns the first object that is hit by
    this ray.

    @seeNode Mask

    @input From: the location from where to start the ray, in world
        coordinates
    @input To: the target location of the ray, in world coordinates
    @input Collision Group Mask: A bit mask value to specify which
        objects are considered

    @output Rigid Body: the object that was hit
    @output Hit: the hit position in world coordinates
    @output Normal: the surface normal of the hit position relative to
        the world
    """
    bl_idname = 'LNCastPhysicsRayNode'
    bl_label = 'Ray Cast'
    arm_version = 1

    def init(self, context):
        super(RayCastNode, self).init(context)
        self.add_input('NodeSocketVector', 'From')
        self.add_input('NodeSocketVector', 'To')
        self.add_input('NodeSocketInt', 'Collision Group Mask')
        self.add_output('ArmNodeSocketObject', 'RB')
        self.add_output('NodeSocketVector', 'Hit')
        self.add_output('NodeSocketVector', 'Normal')

add_node(RayCastNode, category=PKG_AS_CATEGORY, section='ray')
