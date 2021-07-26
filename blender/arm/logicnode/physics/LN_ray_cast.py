from arm.logicnode.arm_nodes import *

class RayCastNode(ArmLogicTreeNode):
    """Casts a physics ray and returns the first object that is hit by
    this ray.

    @seeNode Mask

    @input From: the location from where to start the ray, in world
        coordinates
    @input To: the target location of the ray, in world coordinates
    @input Mask: a bit mask value to specify which
        objects are considered

    @output RB: the object that was hit
    @output Hit: the hit position in world coordinates
    @output Normal: the surface normal of the hit position relative to
        the world
    """
    bl_idname = 'LNCastPhysicsRayNode'
    bl_label = 'Ray Cast'
    arm_section = 'ray'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'From')
        self.add_input('ArmVectorSocket', 'To')
        self.add_input('ArmIntSocket', 'Mask', default_value=1)

        self.add_output('ArmNodeSocketObject', 'RB')
        self.add_output('ArmVectorSocket', 'Hit')
        self.add_output('ArmVectorSocket', 'Normal')
