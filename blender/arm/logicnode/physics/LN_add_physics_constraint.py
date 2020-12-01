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
                #X ang limits
                self.add_input('NodeSocketBool', 'X angle')
                #Y ang limits
                self.add_input('NodeSocketBool', 'Y angle')
                #Z ang limits
                self.add_input('NodeSocketBool', 'Z angle')
                #limits
                self.add_input('ArmNodeSocketArray', 'Limits')
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
                #X ang limits
                self.add_input('NodeSocketBool', 'X angle')
                #Y ang limits
                self.add_input('NodeSocketBool', 'Y angle')
                #Z ang limits
                self.add_input('NodeSocketBool', 'Z angle')
                #X lin spring
                self.add_input('NodeSocketBool', 'X linear')
                #Y lin spring
                self.add_input('NodeSocketBool', 'Y linear')
                #Z lin spring
                self.add_input('NodeSocketBool', 'Z linear')
                #X ang spring
                self.add_input('NodeSocketBool', 'X angle')
                #Y ang spring
                self.add_input('NodeSocketBool', 'Y angle')
                #Z ang spring
                self.add_input('NodeSocketBool', 'Z angle')
                #limits
                self.add_input('ArmNodeSocketArray', 'Limits')
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

        if (self.get_count_in(self.property0) == 5):
            grid0 = layout.grid_flow(row_major=True, columns=1, align=True)
            grid0.label(text="Limits:")
            grid0.label(text="Linear lower [X, Y, Z]")
            grid0.label(text="Linear upper [X, Y, Z]")
            grid0.label(text="Angular lower [X, Y, Z]")
            grid0.label(text="Angular upper [X, Y, Z]")
            row00 = layout.row()
            row10 = row00.column()
            row00.alignment = 'CENTER'
            row00.label(text = "")
            row01 = row00.split()
            row01.alignment = 'CENTER'
            row01.label(text = "Limits")
            row02 = row01.split()
            row02.alignment = 'CENTER'
            row02.label(text = "Springs")
            #row1
            row10.alignment = 'CENTER'
            row10.label(text = 'X')

            #row11 = row01.column()
            #row11.alignment = 'CENTER'
            #row11.label(text = "Linear X")
            #row12 = row11.split()
            #row12.alignment = 'CENTER'
            #row12.label(text = "Angular X")

            #row13 = row02.column()
            #row13.alignment = 'CENTER'
            #row13.label(text = "Linear X")
            #row14 = row13.split()
            #row14.alignment = 'CENTER'
            #row14.label(text = "Angular X")


            grid1 = layout.grid_flow(row_major=True, columns=5, align=True)
            ##row 1
            grid1.label(text="")
            grid1.label(text="Linear")
            grid1.label(text="Angular")
            grid1.label(text="Linear")
            grid1.label(text="Angular")
            ##row 2
            grid1.label(text="X")
            grid1.label(text="Linear X")
            grid1.label(text="Angular X")
            grid1.label(text="Linear X")
            grid1.label(text="Angular X")
            ##row 2
            grid1.label(text="Y")
            grid1.label(text="Linear Y")
            grid1.label(text="Angular Y")
            grid1.label(text="Linear Y")
            grid1.label(text="Angular Y")
            ##row 3
            grid1.label(text="Z")
            grid1.label(text="Linear Z")
            grid1.label(text="Angular Z")
            grid1.label(text="Linear Z")
            grid1.label(text="Angular Z")

        
        if (self.get_count_in(self.property0) == 6):
            grid0 = layout.grid_flow(row_major=True, columns=1, align=True)
            grid0.label(text="Limits:")
            grid0.label(text="Linear lower [X, Y, Z]")
            grid0.label(text="Linear upper [X, Y, Z]")
            grid0.label(text="Angular lower [X, Y, Z]")
            grid0.label(text="Angular upper [X, Y, Z]")
            grid0.label(text="Linear Stiffness [X, Y, Z]")
            grid0.label(text="Linear Damping [X, Y, Z]")
            grid0.label(text="Angular Stiffness [X, Y, Z]")
            grid0.label(text="Angular Damping [X, Y, Z]")

