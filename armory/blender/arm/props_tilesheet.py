import bpy
from bpy.props import *


class ArmTilesheetEventListItem(bpy.types.PropertyGroup):
    """An event triggered on a specific frame within a tilesheet action."""
    name: StringProperty(
        name="Event Name",
        description="Name of the event to trigger",
        default="event")

    frame_prop: IntProperty(
        name="Frame",
        description="Frame number when this event triggers",
        default=0,
        min=0)


class ArmTilesheetActionListItem(bpy.types.PropertyGroup):
    """An action (animation sequence) within a tilesheet with per-action properties."""
    name: StringProperty(
        name="Name",
        description="Name of this tilesheet action",
        default="Untitled")

    start_prop: IntProperty(
        name="Start",
        description="Starting frame index",
        default=0)

    end_prop: IntProperty(
        name="End",
        description="Ending frame index",
        default=0)

    loop_prop: BoolProperty(
        name="Loop",
        description="Whether this action should loop",
        default=True)

    tilesx_prop: IntProperty(
        name="Tiles X",
        description="Number of horizontal tiles for this action",
        default=1,
        min=1)

    tilesy_prop: IntProperty(
        name="Tiles Y",
        description="Number of vertical tiles for this action",
        default=1,
        min=1)

    framerate_prop: IntProperty(
        name="Frame Rate",
        description="Animation frame rate for this action (frames per second)",
        default=4,
        min=1)

    mesh_prop: StringProperty(
        name="Mesh",
        description="Optional mesh data to swap to when playing this action (brings its own material/texture/UVs)",
        default="")

    # Events list for this action
    events: CollectionProperty(type=ArmTilesheetEventListItem)
    events_index: IntProperty(name="Event Index", default=0)


class ARM_UL_TilesheetActionList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'PLAY'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)


class ArmTilesheetActionListNewItem(bpy.types.Operator):
    """Add a new action to the tilesheet"""
    bl_idname = "arm_tilesheetactionlist.new_item"
    bl_label = "Add Action"

    def execute(self, context):
        obj = context.object
        if obj is None:
            return {'CANCELLED'}
        obj.arm_tilesheet_actionlist.add()
        obj.arm_tilesheet_actionlist_index = len(obj.arm_tilesheet_actionlist) - 1
        return {'FINISHED'}


class ArmTilesheetActionListDeleteItem(bpy.types.Operator):
    """Delete the selected action from the tilesheet"""
    bl_idname = "arm_tilesheetactionlist.delete_item"
    bl_label = "Delete Action"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and len(obj.arm_tilesheet_actionlist) > 0

    def execute(self, context):
        obj = context.object
        action_list = obj.arm_tilesheet_actionlist
        index = obj.arm_tilesheet_actionlist_index

        action_list.remove(index)

        if index > 0:
            index = index - 1

        obj.arm_tilesheet_actionlist_index = index
        return {'FINISHED'}


class ArmTilesheetActionListMoveItem(bpy.types.Operator):
    """Move an action in the list"""
    bl_idname = "arm_tilesheetactionlist.move_item"
    bl_label = "Move Action"
    bl_options = {'INTERNAL'}

    direction: EnumProperty(
        items=(
            ('UP', 'Up', ""),
            ('DOWN', 'Down', "")
        ))

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and len(obj.arm_tilesheet_actionlist) > 0

    def execute(self, context):
        obj = context.object
        action_list = obj.arm_tilesheet_actionlist
        index = obj.arm_tilesheet_actionlist_index
        list_length = len(action_list) - 1

        if self.direction == 'UP':
            new_index = max(0, index - 1)
        else:  # DOWN
            new_index = min(list_length, index + 1)

        action_list.move(index, new_index)
        obj.arm_tilesheet_actionlist_index = new_index
        return {'FINISHED'}


class ArmTilesheetEventListNewItem(bpy.types.Operator):
    """Add a new event to the current action"""
    bl_idname = "arm_tilesheetactionlist.new_event"
    bl_label = "Add Event"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and len(obj.arm_tilesheet_actionlist) > 0

    def execute(self, context):
        obj = context.object
        if obj.arm_tilesheet_actionlist_index < 0:
            return {'CANCELLED'}
        action = obj.arm_tilesheet_actionlist[obj.arm_tilesheet_actionlist_index]
        action.events.add()
        action.events_index = len(action.events) - 1
        return {'FINISHED'}


class ArmTilesheetEventListDeleteItem(bpy.types.Operator):
    """Delete the selected event from the current action"""
    bl_idname = "arm_tilesheetactionlist.delete_event"
    bl_label = "Delete Event"

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is None or len(obj.arm_tilesheet_actionlist) == 0:
            return False
        if obj.arm_tilesheet_actionlist_index < 0:
            return False
        action = obj.arm_tilesheet_actionlist[obj.arm_tilesheet_actionlist_index]
        return len(action.events) > 0

    def execute(self, context):
        obj = context.object
        action = obj.arm_tilesheet_actionlist[obj.arm_tilesheet_actionlist_index]
        events = action.events
        index = action.events_index

        events.remove(index)

        if index > 0:
            action.events_index = index - 1

        return {'FINISHED'}


class ARM_PT_TilesheetPanel(bpy.types.Panel):
    bl_label = "Armory Tilesheet"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def draw_header(self, context):
        obj = context.object
        self.layout.prop(obj, "arm_tilesheet_enabled", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        obj = context.object

        layout.enabled = obj.arm_tilesheet_enabled

        # Default action dropdown
        layout.prop_search(obj, "arm_tilesheet_default_action", obj, "arm_tilesheet_actionlist", text="Default Action")

        row = layout.row()
        row.prop(obj, "arm_tilesheet_flipx")
        row.prop(obj, "arm_tilesheet_flipy")

        # Actions list
        layout.separator()
        layout.label(text="Actions")
        rows = 2
        if len(obj.arm_tilesheet_actionlist) > 1:
            rows = 4
        row = layout.row()
        row.template_list("ARM_UL_TilesheetActionList", "The_List", obj, "arm_tilesheet_actionlist", obj, "arm_tilesheet_actionlist_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_tilesheetactionlist.new_item", icon='ADD', text="")
        col.operator("arm_tilesheetactionlist.delete_item", icon='REMOVE', text="")

        if len(obj.arm_tilesheet_actionlist) > 1:
            col.separator()
            op = col.operator("arm_tilesheetactionlist.move_item", icon='TRIA_UP', text="")
            op.direction = 'UP'
            op = col.operator("arm_tilesheetactionlist.move_item", icon='TRIA_DOWN', text="")
            op.direction = 'DOWN'

        # Selected action details (per-action properties)
        if obj.arm_tilesheet_actionlist_index >= 0 and len(obj.arm_tilesheet_actionlist) > 0:
            adat = obj.arm_tilesheet_actionlist[obj.arm_tilesheet_actionlist_index]
            box = layout.box()
            # Grid dimensions
            row = box.row()
            row.use_property_split = False
            row.prop(adat, "tilesx_prop")
            row.prop(adat, "tilesy_prop")
            # Frame range
            row = box.row()
            row.use_property_split = False
            row.prop(adat, "start_prop")
            row.prop(adat, "end_prop")
            # Framerate and loop
            box.prop(adat, "framerate_prop")
            box.prop(adat, "loop_prop")
            # Optional mesh (dropdown from bpy.data.meshes)
            box.prop_search(adat, "mesh_prop", bpy.data, "meshes", text="Mesh")

            # Events section
            box.separator()
            box.label(text="Events")
            row = box.row()
            col = row.column()
            for i, evt in enumerate(adat.events):
                evt_row = col.row(align=True)
                evt_row.prop(evt, "name", text="")
                evt_row.prop(evt, "frame_prop", text="Frame")
            row = box.row(align=True)
            row.operator("arm_tilesheetactionlist.new_event", icon='ADD', text="Add Event")
            row.operator("arm_tilesheetactionlist.delete_event", icon='REMOVE', text="Remove Event")


__REG_CLASSES = (
    ArmTilesheetEventListItem,
    ArmTilesheetActionListItem,
    ARM_UL_TilesheetActionList,
    ArmTilesheetActionListNewItem,
    ArmTilesheetActionListDeleteItem,
    ArmTilesheetActionListMoveItem,
    ArmTilesheetEventListNewItem,
    ArmTilesheetEventListDeleteItem,
    ARM_PT_TilesheetPanel,
)
__reg_classes, unregister = bpy.utils.register_classes_factory(__REG_CLASSES)


def register():
    __reg_classes()

    # Tilesheet properties on Object (one tilesheet per object)
    bpy.types.Object.arm_tilesheet_enabled = BoolProperty(
        name="Tilesheet",
        description="Enable tilesheet animation for this object",
        default=False)

    bpy.types.Object.arm_tilesheet_default_action = StringProperty(
        name="Default Action",
        description="Default action to play on start",
        default="")

    bpy.types.Object.arm_tilesheet_flipx = BoolProperty(
        name="Flip X",
        description="Flip the tilesheet horizontally",
        default=False)

    bpy.types.Object.arm_tilesheet_flipy = BoolProperty(
        name="Flip Y",
        description="Flip the tilesheet vertically",
        default=False)

    bpy.types.Object.arm_tilesheet_actionlist = CollectionProperty(type=ArmTilesheetActionListItem)
    bpy.types.Object.arm_tilesheet_actionlist_index = IntProperty(
        name="Action Index",
        default=0)
