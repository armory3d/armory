import bpy
from bpy.props import *


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


__REG_CLASSES = (
    ArmTilesheetActionListItem,
    ARM_UL_TilesheetActionList,
    ArmTilesheetActionListNewItem,
    ArmTilesheetActionListDeleteItem,
    ArmTilesheetActionListMoveItem,
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

    bpy.types.Object.arm_tilesheet_actionlist = CollectionProperty(type=ArmTilesheetActionListItem)
    bpy.types.Object.arm_tilesheet_actionlist_index = IntProperty(
        name="Action Index",
        default=0)
