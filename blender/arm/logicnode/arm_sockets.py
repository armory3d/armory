import bpy
from bpy.props import *
from bpy.types import NodeSocket

import arm.utils


def _on_update_socket(self, context):
    self.node.on_socket_val_update(context, self)


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
    default_value_raw: PointerProperty(name='Action', type=bpy.types.Action, update=_on_update_socket)

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


class ArmBoolSocket(ArmCustomSocket):
    bl_idname = 'ArmBoolSocket'
    bl_label = 'Boolean Socket'
    arm_socket_type = 'BOOLEAN'

    default_value_raw: BoolProperty(
        name='Value',
        description='Input value used for unconnected socket',
        update=_on_update_socket
    )

    def draw(self, context, layout, node, text):
        draw_socket_layout(self, layout)

    def draw_color(self, context, node):
        return 0.8, 0.651, 0.839, 1

    def get_default_value(self):
        return self.default_value_raw


class ArmColorSocket(ArmCustomSocket):
    bl_idname = 'ArmColorSocket'
    bl_label = 'Color Socket'
    arm_socket_type = 'RGBA'

    default_value_raw: FloatVectorProperty(
        name='Value',
        size=4,
        subtype='COLOR',
        min=0.0,
        max=1.0,
        description='Input value used for unconnected socket',
        update=_on_update_socket
    )

    def draw(self, context, layout, node, text):
        draw_socket_layout(self, layout)

    def draw_color(self, context, node):
        return 0.78, 0.78, 0.161, 1

    def get_default_value(self):
        return self.default_value_raw


class ArmDynamicSocket(ArmCustomSocket):
    bl_idname = 'ArmDynamicSocket'
    bl_label = 'Dynamic Socket'
    arm_socket_type = 'NONE'

    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    def draw_color(self, context, node):
        return 0.388, 0.78, 0.388, 1


class ArmFloatSocket(ArmCustomSocket):
    bl_idname = 'ArmFloatSocket'
    bl_label = 'Float Socket'
    arm_socket_type = 'VALUE'

    default_value_raw: FloatProperty(
        name='Value',
        description='Input value used for unconnected socket',
        precision=3,
        update=_on_update_socket
    )

    def draw(self, context, layout, node, text):
        draw_socket_layout(self, layout)

    def draw_color(self, context, node):
        return 0.631, 0.631, 0.631, 1

    def get_default_value(self):
        return self.default_value_raw


class ArmIntSocket(ArmCustomSocket):
    bl_idname = 'ArmIntSocket'
    bl_label = 'Integer Socket'
    arm_socket_type = 'INT'

    default_value_raw: IntProperty(
        name='Value',
        description='Input value used for unconnected socket',
        update=_on_update_socket
    )

    def draw(self, context, layout, node, text):
        draw_socket_layout(self, layout)

    def draw_color(self, context, node):
        return 0.059, 0.522, 0.149, 1

    def get_default_value(self):
        return self.default_value_raw


class ArmObjectSocket(ArmCustomSocket):
    bl_idname = 'ArmNodeSocketObject'
    bl_label = 'Object Socket'
    arm_socket_type = 'OBJECT'

    default_value_get: PointerProperty(name='Object', type=bpy.types.Object)  # legacy version of the line after this one
    default_value_raw: PointerProperty(name='Object', type=bpy.types.Object, update=_on_update_socket)

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


class ArmStringSocket(ArmCustomSocket):
    bl_idname = 'ArmStringSocket'
    bl_label = 'String Socket'
    arm_socket_type = 'STRING'

    default_value_raw: StringProperty(
        name='Value',
        description='Input value used for unconnected socket',
        update=_on_update_socket
    )

    def draw(self, context, layout, node, text):
        draw_socket_layout_split(self, layout)

    def draw_color(self, context, node):
        return 0.439, 0.698, 1, 1

    def get_default_value(self):
        return self.default_value_raw


class ArmVectorSocket(ArmCustomSocket):
    bl_idname = 'ArmVectorSocket'
    bl_label = 'Vector Socket'
    arm_socket_type = 'VECTOR'

    default_value_raw: FloatVectorProperty(
        name='Value',
        size=3,
        description='Input value used for unconnected socket',
        update=_on_update_socket
    )

    def draw(self, context, layout, node, text):
        if not self.is_output and not self.is_linked:
            col = layout.column(align=True)
            col.prop(self, 'default_value_raw', text='')
        else:
            layout.label(text=self.name)

    def draw_color(self, context, node):
        return 0.388, 0.388, 0.78, 1

    def get_default_value(self):
        return self.default_value_raw


def draw_socket_layout(socket: bpy.types.NodeSocket, layout: bpy.types.UILayout, prop_name='default_value_raw'):
    if not socket.is_output and not socket.is_linked:
        layout.prop(socket, prop_name, text=socket.name)
    else:
        layout.label(text=socket.name)


def draw_socket_layout_split(socket: bpy.types.NodeSocket, layout: bpy.types.UILayout, prop_name='default_value_raw'):
    if not socket.is_output and not socket.is_linked:
        # Blender layouts use 0.4 splits
        layout = layout.split(factor=0.4, align=True)

    layout.label(text=socket.name)

    if not socket.is_output and not socket.is_linked:
        layout.prop(socket, prop_name, text='')


REG_CLASSES = (
    ArmActionSocket,
    ArmAnimActionSocket,
    ArmArraySocket,
    ArmBoolSocket,
    ArmColorSocket,
    ArmDynamicSocket,
    ArmFloatSocket,
    ArmIntSocket,
    ArmObjectSocket,
    ArmStringSocket,
    ArmVectorSocket,
)
register, unregister = bpy.utils.register_classes_factory(REG_CLASSES)
