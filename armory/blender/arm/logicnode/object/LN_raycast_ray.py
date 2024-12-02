from arm.logicnode.arm_nodes import *

class RaycastRayNode(ArmLogicTreeNode):
    """Cast a Ray (Origin and direction) to return the name, location and distance of the closest object
    in the object arrays

    @input Obj Array: Objects to detect. 
    @input Origin: ray origin.
    @input Direction: ray direction.
    
    @output True: if an object is detected.
    @output False: if none object is detected.
    @output Object: close object detected.
    @output Location: the position where the ray comes in contact with the ray.
    @output Distance: distance from origin to location. 
    """

    bl_idname = 'LNRaycastRayNode'
    bl_label = 'Raycast Ray'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Obj Array')
        self.add_input('ArmVectorSocket', 'Origin')
        self.add_input('ArmVectorSocket', 'Direction')
        
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')
        self.add_output('ArmNodeSocketObject', 'Object')
        self.add_output('ArmVectorSocket', 'Location')
        self.add_output('ArmFloatSocket', 'Distance')
