from arm.logicnode.arm_nodes import *

class AddPhysicsConstraintNode(ArmLogicTreeNode):
    """Add a physics constraint to an object"""
    bl_idname = 'LNAddPhysicsConstraintNode'
    bl_label = 'Add Physics Constraint'
    arm_sction = 'add'
    arm_version = 1

    @staticmethod
    def get_enum_id_value(obj, prop_name, value):
        return obj.bl_rna.properties[prop_name].enum_items[value].identifier

    @staticmethod
    def get_count_in(type_name):
        return {
            'Fixed': 0, 
            'Point': 1, 
            'Hinge': 2, 
            'Slider': 3,
            'Piston': 4, 
            'Generic': 5, 
            'Spring': 6, 
        }.get(type_name, 0)

    def get_enum(self):   
        return self.get('property0', 0)

    def set_enum(self, value):
        # Checking the selection of another type
        select_current = self.get_enum_id_value(self, 'property0', value)
        select_prev = self.property0
        #Check if a different type is selected
        if select_prev != select_current:
            print('New value selected')
            # Arguements for type Fixed
            if (self.get_count_in(select_current) == 0):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])
            # Arguements for type Point
            if (self.get_count_in(select_current) == 1):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])
            #Arguements for type Hinge
            if (self.get_count_in(select_current) == 2):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])
                #Z ang limits
                self.add_input('NodeSocketBool', 'Z angle')
                self.add_input('NodeSocketFloat', 'Z ang lower', -45.0)
                self.add_input('NodeSocketFloat', 'Z ang upper', 45.0)
            #Arguements for type Slider
            if (self.get_count_in(select_current) == 3):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])
                #X lin limits
                self.add_input('NodeSocketBool', 'X linear')
                self.add_input('NodeSocketFloat', 'X lin lower')
                self.add_input('NodeSocketFloat', 'X lin upper')
            #Arguements for type Piston
            if (self.get_count_in(select_current) == 4):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])
                #X lin limits
                self.add_input('NodeSocketBool', 'X linear')
                self.add_input('NodeSocketFloat', 'X lin lower')
                self.add_input('NodeSocketFloat', 'X lin upper')
                #X ang limits
                self.add_input('NodeSocketBool', 'X angle')
                self.add_input('NodeSocketFloat', 'X ang lower', -45.0)
                self.add_input('NodeSocketFloat', 'X ang upper', 45.0)
            #Arguements for type Generic
            if (self.get_count_in(select_current) == 5):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])
                #X lin limits
                self.add_input('NodeSocketBool', 'X linear')
                #Y lin limits
                self.add_input('NodeSocketBool', 'Y linear')
                #Z lin limits
                self.add_input('NodeSocketBool', 'Z linear')
                #lower limits
                self.add_input('NodeSocketVector', 'lin lower')
                #upper limits
                self.add_input('NodeSocketVector', 'lin upper')
                #X ang limits
                self.add_input('NodeSocketBool', 'X angle')
                #Y ang limits
                self.add_input('NodeSocketBool', 'Y angle')
                #Z ang limits
                self.add_input('NodeSocketBool', 'Z angle')
                #lower limits
                self.add_input('NodeSocketVector', 'ang lower', [-45.0, -45.0, -45.0])
                #upper limits
                self.add_input('NodeSocketVector', 'ang upper', [45.0, 45.0, 45.0])
            #Arguements for type GenericSpring
            if (self.get_count_in(select_current) == 6):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])
                #X lin limits
                self.add_input('NodeSocketBool', 'X linear')
                #Y lin limits
                self.add_input('NodeSocketBool', 'Y linear')
                #Z lin limits
                self.add_input('NodeSocketBool', 'Z linear')
                #lower limits
                self.add_input('NodeSocketVector', 'lin lower')
                #upper limits
                self.add_input('NodeSocketVector', 'lin upper')
                #X ang limits
                self.add_input('NodeSocketBool', 'X angle')
                #Y ang limits
                self.add_input('NodeSocketBool', 'Y angle')
                #Z ang limits
                self.add_input('NodeSocketBool', 'Z angle')
                #lower limits
                self.add_input('NodeSocketVector', 'ang lower', [-45.0, -45.0, -45.0])
                #upper limits
                self.add_input('NodeSocketVector', 'ang upper', [45.0, 45.0, 45.0])
                #X lin spring
                self.add_input('NodeSocketBool', 'X linear')
                #Y lin spring
                self.add_input('NodeSocketBool', 'Y linear')
                #Z lin spring
                self.add_input('NodeSocketBool', 'Z linear')
                #linear stiffness
                self.add_input('NodeSocketVector', 'lin stiffness', [10.0, 10.0, 10.0])
                #linear damping
                self.add_input('NodeSocketVector', 'lin damping', [0.5, 0.5, 0.5])
                #X ang spring
                self.add_input('NodeSocketBool', 'X angle')
                #Y ang spring
                self.add_input('NodeSocketBool', 'Y angle')
                #Z ang spring
                self.add_input('NodeSocketBool', 'Z angle')
                #angular stiffness
                self.add_input('NodeSocketVector', 'ang stiffness', [10.0, 10.0, 10.0])
                #angular damping
                self.add_input('NodeSocketVector', 'ang damping', [0.5, 0.5, 0.5])
        self['property0'] = value

    property0: EnumProperty(
        items = [('Fixed', 'Fixed', 'Fixed'),
                 ('Point', 'Point', 'Point'),
                 ('Hinge', 'Hinge', 'Hinge'),
                 ('Slider', 'Slider', 'Slider'),
                 ('Piston', 'Piston', 'Piston'),
                 ('Generic', 'Generic', 'Generic'),
                 ('Spring', 'Spring', 'Spring')],
        name='Type', default='Fixed', set=set_enum, get=get_enum)
    
    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        super(AddPhysicsConstraintNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Pivot Object')
        self.add_input('ArmNodeSocketObject', 'RB 1')
        self.add_input('ArmNodeSocketObject', 'RB 2')
        self.add_input('NodeSocketBool', 'Disable Collissions')
        self.add_input('NodeSocketBool', 'Breakable')
        self.add_input('NodeSocketFloat', 'Breaking Threshold')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
