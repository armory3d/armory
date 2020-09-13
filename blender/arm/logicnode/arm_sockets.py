import bpy
from bpy.props import PointerProperty
from bpy.types import NodeSocket

import arm.utils


class ArmCustomSocket(NodeSocket):
    """
    A custom socket that can be used to define more socket types for
    logic node packs. Do not use this type directly (it is not
    registered)!
    """

    bl_idname = 'ArmCustomSocket'
    bl_label = 'Custom Socket'
    # note: trying to use the `type` property will fail. All custom nodes will have "VALUE" as a type, because it is the default.
    arm_socket_type = 'NONE'
    # please also declare a property named "default_value_raw" of arm_socket_type isn't "NONE"

    def get_default_value(self):
        """Override this for values of unconnected input sockets."""
        return None


class ArmActionSocket(ArmCustomSocket):
    bl_idname = 'ArmNodeSocketAction'
    bl_label = 'Action Socket'
    arm_socket_type = 'NONE'

    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    def draw_color(self, context, node):
        return 0.8, 0.3, 0.3, 1


class ArmAnimActionSocket(ArmCustomSocket):
    bl_idname = 'ArmNodeSocketAnimAction'
    bl_label = 'Action Socket'
    arm_socket_type = 'STRING'

    default_value_get: PointerProperty(name='Action', type=bpy.types.Action)  # legacy version of the line after this one
    default_value_raw: PointerProperty(name='Action', type=bpy.types.Action)

    def __init__(self):
        super().__init__()
        if self.default_value_get is not None:
            self.default_value_raw = self.default_value_get
            self.default_value_get = None

    def get_default_value(self):
        if self.default_value_raw is None:
            return ''
        if self.default_value_raw.name not in bpy.data.actions:
            return self.default_value_raw.name
        name = arm.utils.asset_name(bpy.data.actions[self.default_value_raw.name])
        return arm.utils.safestr(name)

    def draw(self, context, layout, node, text):
        if self.is_output:
            layout.label(text=self.name)
        elif self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop_search(self, 'default_value_raw', bpy.data, 'actions', icon='NONE', text='')

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.8, 1


class ArmArraySocket(ArmCustomSocket):
    bl_idname = 'ArmNodeSocketArray'
    bl_label = 'Array Socket'
    arm_socket_type = 'NONE'

    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    def draw_color(self, context, node):
        return 0.8, 0.4, 0.0, 1


class ArmObjectSocket(ArmCustomSocket):
    bl_idname = 'ArmNodeSocketObject'
    bl_label = 'Object Socket'
    arm_socket_type = 'OBJECT'

    default_value_get: PointerProperty(name='Object', type=bpy.types.Object)  # legacy version of the line after this one
    default_value_raw: PointerProperty(name='Object', type=bpy.types.Object)

    def __init__(self):
        super().__init__()
        if self.default_value_get is not None:
            self.default_value_raw = self.default_value_get
            self.default_value_get = None

    def get_default_value(self):
        if self.default_value_raw is None:
            return ''
        if self.default_value_raw.name not in bpy.data.objects:
            return self.default_value_raw.name
        return arm.utils.asset_name(bpy.data.objects[self.default_value_raw.name])

    def draw(self, context, layout, node, text):
        if self.is_output:
            layout.label(text=self.name)
        elif self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row(align=True)
            row.prop_search(self, 'default_value_raw', context.scene, 'objects', icon='NONE', text=self.name)

    def draw_color(self, context, node):
        return 0.15, 0.55, 0.75, 1


def register():
    bpy.utils.register_class(ArmActionSocket)
    bpy.utils.register_class(ArmAnimActionSocket)
    bpy.utils.register_class(ArmArraySocket)
    bpy.utils.register_class(ArmObjectSocket)


def unregister():
    bpy.utils.unregister_class(ArmObjectSocket)
    bpy.utils.unregister_class(ArmArraySocket)
    bpy.utils.unregister_class(ArmAnimActionSocket)
    bpy.utils.unregister_class(ArmActionSocket)
