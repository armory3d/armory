import bpy
from bpy.props import PointerProperty
from bpy.types import NodeSocket

import arm.utils


class ArmActionSocket(NodeSocket):
    bl_idname = 'ArmNodeSocketAction'
    bl_label = 'Action Socket'

    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    def draw_color(self, context, node):
        return 0.8, 0.3, 0.3, 1


class ArmAnimActionSocket(NodeSocket):
    bl_idname = 'ArmNodeSocketAnimAction'
    bl_label = 'Action Socket'
    default_value_get: PointerProperty(name='Action', type=bpy.types.Action)

    def get_default_value(self):
        if self.default_value_get is None:
            return ''
        if self.default_value_get.name not in bpy.data.actions:
            return self.default_value_get.name
        name = arm.utils.asset_name(bpy.data.actions[self.default_value_get.name])
        return arm.utils.safestr(name)

    def draw(self, context, layout, node, text):
        if self.is_output:
            layout.label(text=self.name)
        elif self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop_search(self, 'default_value_get', bpy.data, 'actions', icon='NONE', text='')

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.8, 1


class ArmArraySocket(NodeSocket):
    bl_idname = 'ArmNodeSocketArray'
    bl_label = 'Array Socket'

    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    def draw_color(self, context, node):
        return 0.8, 0.4, 0.0, 1


class ArmCustomSocket(NodeSocket):
    """
    A custom socket that can be used to define more socket types for
    logic node packs. Do not use this type directly (it is not
    registered)!
    """
    bl_idname = 'ArmCustomSocket'
    bl_label = 'Custom Socket'

    def get_default_value(self):
        """Override this for values of unconnected input sockets."""
        return None


class ArmObjectSocket(NodeSocket):
    bl_idname = 'ArmNodeSocketObject'
    bl_label = 'Object Socket'
    default_value_get: PointerProperty(name='Object', type=bpy.types.Object)

    def get_default_value(self):
        if self.default_value_get is None:
            return ''
        if self.default_value_get.name not in bpy.data.objects:
            return self.default_value_get.name
        return arm.utils.asset_name(bpy.data.objects[self.default_value_get.name])

    def draw(self, context, layout, node, text):
        if self.is_output:
            layout.label(text=self.name)
        elif self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row(align=True)
            row.prop_search(self, 'default_value_get', context.scene, 'objects', icon='NONE', text=self.name)

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
