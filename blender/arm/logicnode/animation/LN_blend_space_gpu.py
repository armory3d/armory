from arm.logicnode.arm_advanced_draw import *
from arm.logicnode.arm_nodes import *
from bpy.props import *
from bpy.types import Node

class BlendSpaceNode(ArmLogicTreeNode):
    """Activates the output when the given event is received.

    @seeNode Send Event to Object
    @seeNode Send Event"""
    bl_idname = 'LNBlendSpaceNode'
    bl_label = 'Blend Space'
    arm_version = 1
    arm_section = 'custom'

    modal_run: BoolProperty(
        name="Enable or Disable",
        description="A bool property",
        default = False
    )

    advanced_draw_run: BoolProperty(
        name = "Advance draw enabled",
        description="",
        default = False
    )


    def stop_modal(self):
        print("Setting False")
        self.modal_run = False

    property0: FloatVectorProperty(
        name = "Point Coordionates",
        description="",
        default = (0.0, 0.0, 
                   0.0, 1.0,
                   1.0, 1.0,
                   1.0, 0.0,
                   0.0, 0.0,
                   0.0, 0.0,
                   0.0, 0.0, 
                   0.0, 0.0, 
                   0.0, 0.0, 
                   0.0, 0.0,
                   0.5, 0.5),
        size = 22
    )

    active_point_index: IntProperty(
        default = -1
    )

    active_point_index_ref: IntProperty(
        default = 0
    )

    gui_bounds: FloatVectorProperty(
        name = "GUI bounds",
        description = "",
        default = (0.0, 0.0, 0.0),
        size = 3
    )

    point_size: FloatProperty(
        name = "Point Size",
        description = "",
        default = 0.015
    )

    property1: BoolVectorProperty(
        name = "Point enabled for view",
        description = "",
        default = (True,True,True,True, False, False, False, False, False, False, True),
        size = 11
    )

    draw_handler_dict = {}
    modal_handler_dict = {}

    def __init__(self):
        array_nodes[str(id(self))] = self
        if self.advanced_draw_run:
            self.add_advanced_draw()
    
    def create_blend_space(self):
        self.blend_space = BlendSpaceGUI(self)
    
    def free(self):
        self.remove_advanced_draw()
    
    def get_blend_space_points(self):
        if bpy.context.space_data.edit_tree == self.get_tree():
            return self.blend_space.points
    
    def draw_advanced(self):
        if bpy.context.space_data.edit_tree == self.get_tree():
            self.blend_space.draw()

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_output('ArmNodeSocketAnimTree', 'Out')

    def add_advanced_draw(self):
        pass
        self.advanced_draw_run = True
        print(self.property1[0])
        print(len(self.property0))
        print('Adding')
        print(str(self.as_pointer()))
        handler = self.draw_handler_dict.get(str(self.as_pointer()))
        if handler is None:
            self.create_blend_space()
            editor = getattr(bpy.types, 'SpaceNodeEditor')
            handler = editor.draw_handler_add(self.draw_advanced, (), 'WINDOW', 'POST_VIEW')
            self.draw_handler_dict[str(self.as_pointer())] = handler
            print(self.draw_handler_dict)      
            self.modal_run = False  


    def remove_advanced_draw(self):
        pass
        self.advanced_draw_run = False
        print('Removing')
        print(str(self.as_pointer()))
        print(self.draw_handler_dict)
        handler = self.draw_handler_dict.get(str(self.as_pointer()))
        if handler is not None:
            print('Handler existing')
            editor = getattr(bpy.types, 'SpaceNodeEditor')
            editor.draw_handler_remove(handler, 'WINDOW')
            self.draw_handler_dict.pop(str(self.as_pointer()))

    def add_point(self):
        for i in range(len(self.property1)):
            if not self.property1[i]:
                self.property1[i] = True
                self.property0[i * 2] = 0.5
                self.property0[i * 2 + 1] = 0.5
                break  
    
    def remove_point(self):
        if self.active_point_index_ref < 10:
            self.property1[self.active_point_index_ref] = False
            self.active_point_index_ref = 10

        
    def draw_buttons(self, context, layout):
        pass
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        op = row.operator('arm.node_call_func', text='Show', icon='FULLSCREEN_ENTER', emboss=True, depress = self.advanced_draw_run)
        op.node_index = str(id(self))
        op.callback_name = 'add_advanced_draw'
        op = row.operator('arm.node_call_func', text='Hide', icon='FULLSCREEN_EXIT', emboss=True, depress = not self.advanced_draw_run)
        op.node_index = str(id(self))
        op.callback_name = 'remove_advanced_draw'
        if self.advanced_draw_run:
            col = layout.column()
            row = col.row(align=True)
            op = row.operator('arm.blend_space_operator', text = 'Edit', icon = 'EDITMODE_HLT', emboss = True, depress = self.modal_run)
            op.node_index = str(id(self))
            op = row.operator('arm.node_call_func', text = 'Exit Edit', icon = 'OBJECT_DATAMODE', emboss = True, depress = not self.modal_run)
            op.node_index = str(id(self))
            op.callback_name = 'stop_modal'
            if self.modal_run:
                col = layout.column()
                row = col.row(align=True)
                op = row.operator('arm.node_call_func', text = 'Add Point', icon = 'PLUS', emboss = True)
                op.node_index = str(id(self))
                op.callback_name = 'add_point'
                op = row.operator('arm.node_call_func', text = 'Remove Point', icon = 'X', emboss = True)
                op.node_index = str(id(self))
                op.callback_name = 'remove_point'
                cl =layout.column()
                actie_point = self.active_point_index_ref
                pos = ", Pos = " + str(round(self.property0[actie_point * 2], 2)) + ", " + str(round(self.property0[actie_point * 2 + 1], 2))
                if actie_point > 9:
                    cl.label(text = "Selected: Cursor" + pos)
                else:
                    cl.label(text = "Selected: " + str(self.active_point_index_ref + 1) + pos)
