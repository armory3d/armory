from math import pi, cos, sin, sqrt
from typing import Type

import bpy
from bpy.props import *
from bpy.types import NodeSocket
import mathutils

import arm.node_utils
import arm.utils

if arm.is_reload(__name__):
    arm.node_utils = arm.reload_module(arm.node_utils)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)

# See Blender sources: /source/blender/editors/space_node/drawnode.cc
# Permalink for 3.2.2: https://github.com/blender/blender/blob/bcfdb14560e77891d674c2701a5071a7c07baba3/source/blender/editors/space_node/drawnode.cc#L1152-L1167
socket_colors = {
    'ArmNodeSocketAction': (0.8, 0.3, 0.3, 1),
    'ArmNodeSocketAnimAction': (0.8, 0.8, 0.8, 1),
    'ArmRotationSocket': (0.68, 0.22, 0.62, 1),
    'ArmNodeSocketArray': (0.8, 0.4, 0.0, 1),
    'ArmBoolSocket': (0.80, 0.65, 0.84, 1.0),
    'ArmColorSocket': (0.78, 0.78, 0.16, 1.0),
    'ArmDynamicSocket': (0.39, 0.78, 0.39, 1.0),
    'ArmFloatSocket': (0.63, 0.63, 0.63, 1.0),
    'ArmIntSocket': (0.059, 0.522, 0.149, 1),
    'ArmNodeSocketObject': (0.15, 0.55, 0.75, 1),
    'ArmStringSocket': (0.44, 0.70, 1.00, 1.0),
    'ArmVectorSocket': (0.39, 0.39, 0.78, 1.0),
    'ArmAnySocket': (0.9, 0.9, 0.9, 1),
    'ArmNodeSocketAnimTree': (0.3, 0.1, 0.0, 1.0),
    'ArmFactorSocket': (0.631, 0.631, 0.631, 1.0),
    'ArmBlendSpaceSocket': (0.631, 0.631, 0.631, 1.0)
}


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

    def on_node_update(self):
        """Called when the update() method of the corresponding node is called."""
        pass

    def copy_defaults(self, socket):
        """Called when this socket default values are to be copied to the given socket"""
        pass


class ArmActionSocket(ArmCustomSocket):
    bl_idname = 'ArmNodeSocketAction'
    bl_label = 'Action Socket'
    arm_socket_type = 'NONE'

    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    def draw_color(self, context, node):
        return socket_colors[self.bl_idname]


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
            row = layout.row(align=True)
            layout.prop_search(self, 'default_value_raw', bpy.data, 'actions', icon='NONE', text=self.name)

    def draw_color(self, context, node):
        return socket_colors[self.bl_idname]

    def copy_defaults(self, socket):
        if socket.bl_idname == self.bl_idname:
            socket.default_value_raw = self.default_value_raw

class ArmRotationSocket(ArmCustomSocket):
    bl_idname = 'ArmRotationSocket'
    bl_label = 'Rotation Socket'
    arm_socket_type = 'ROTATION'  # the internal representation is a quaternion, AKA a '4D vector' (using mathutils.Vector((x,y,z,w)))

    def get_default_value(self):
        if self.default_value_raw is None:
            return mathutils.Vector((0.0,0.0,0.0,1.0))
        else:
            return self.default_value_raw

    def on_unit_update(self, context):
        if self.default_value_unit == 'Rad':
            fac = pi/180  # deg->rad conversion
        else:
            fac = 180/pi  # rad->deg conversion
        if self.default_value_mode == 'AxisAngle':
            self.default_value_s3 *= fac
        elif self.default_value_mode == 'EulerAngles':
            self.default_value_s0 *= fac
            self.default_value_s1 *= fac
            self.default_value_s2 *= fac
        self.do_update_raw(context)

    def on_mode_update(self, context):
        if self.default_value_mode == 'Quaternion':
            summ = abs(self.default_value_s0)
            summ+= abs(self.default_value_s1)
            summ+= abs(self.default_value_s2)
            summ+= abs(self.default_value_s3)
            if summ<0.01:
                self.default_value_s3 = 1.0
        elif self.default_value_mode == 'AxisAngle':
            summ = abs(self.default_value_s0)
            summ+= abs(self.default_value_s1)
            summ+= abs(self.default_value_s2)
            if summ<1E-5:
                self.default_value_s3 = 0.0
        self.do_update_raw(context)

    @staticmethod
    def convert_to_quaternion(part1,part2,param1,param2,param3):
        """converts a representation of rotation into a quaternion.
        ``part1`` is a vector, ``part2`` is a scalar or None,
        ``param1`` is in ('Quaternion', 'EulerAngles', 'AxisAngle'),
        ``param2`` is in ('Rad','Deg') for both EulerAngles and AxisAngle,
        ``param3`` is a len-3 string like "XYZ", for EulerAngles """
        if param1=='Quaternion':
            qx, qy, qz = part1[0], part1[1], part1[2]
            qw = part2
            # need to normalize the quaternion for a rotation (having it be 0 is not an option)
            ql = sqrt(qx**2+qy**2+qz**2+qw**2)
            if abs(ql)<1E-5:
                qx, qy, qz, qw = 0.0,0.0,0.0,1.0
            else:
                qx /= ql
                qy /= ql
                qz /= ql
                qw /= ql
            return mathutils.Vector((qx,qy,qz,qw))

        elif param1 == 'AxisAngle':
            if param2 == 'Deg':
                angle = part2 * pi/180
            else:
                angle = part2
            cang, sang = cos(angle/2), sin(angle/2)
            x,y,z = part1[0], part1[1], part1[2]
            veclen = sqrt(x**2+y**2+z**2)
            if veclen<1E-5:
                return mathutils.Vector((0.0,0.0,0.0,1.0))
            else:
                return mathutils.Vector((
                    x/veclen * sang,
                    y/veclen * sang,
                    z/veclen * sang,
                    cang
                ))
        else:  # param1 == 'EulerAngles'
            x,y,z = part1[0], part1[1], part1[2]
            if param2 == 'Deg':
                x *= pi/180
                y *= pi/180
                z *= pi/180
            cx, sx = cos(x/2), sin(x/2)
            cy, sy = cos(y/2), sin(y/2)
            cz, sz = cos(z/2), sin(z/2)

            qw, qx, qy, qz  = 1.0,0.0,0.0,0.0
            for direction in param3[::-1]:
                qwi, qxi,qyi,qzi = {'X': (cx,sx,0,0), 'Y': (cy,0,sy,0), 'Z': (cz,0,0,sz)}[direction]

                qw = qw*qwi -qx*qxi -qy*qyi -qz*qzi
                qx = qx*qwi +qw*qxi +qy*qzi -qz*qyi
                qy = qy*qwi +qw*qyi +qz*qxi -qx*qzi
                qz = qz*qwi +qw*qzi +qx*qyi -qy*qxi
            return mathutils.Vector((qx,qy,qz,qw))


    def do_update_raw(self, context):
        part1 = mathutils.Vector((
            self.default_value_s0,
            self.default_value_s1,
            self.default_value_s2, 1
        ))
        part2 = self.default_value_s3

        self.default_value_raw = self.convert_to_quaternion(
            part1,
            self.default_value_s3,
            self.default_value_mode,
            self.default_value_unit,
            self.default_value_order
        )


    def draw(self, context, layout, node, text):
        if (self.is_output or self.is_linked):
            layout.label(text=self.name)
        else:
            coll1 = layout.column(align=True)
            coll1.label(text=self.name)
            bx=coll1.box()
            coll = bx.column(align=True)
            coll.prop(self, 'default_value_mode')
            if self.default_value_mode in ('EulerAngles', 'AxisAngle'):
                coll.prop(self, 'default_value_unit')

            if self.default_value_mode == 'EulerAngles':
                coll.prop(self, 'default_value_order')
                coll.prop(self, 'default_value_s0', text='X')
                coll.prop(self, 'default_value_s1', text='Y')
                coll.prop(self, 'default_value_s2', text='Z')
            elif self.default_value_mode == 'Quaternion':
                coll.prop(self, 'default_value_s0', text='X')
                coll.prop(self, 'default_value_s1', text='Y')
                coll.prop(self, 'default_value_s2', text='Z')
                coll.prop(self, 'default_value_s3', text='W')
            elif self.default_value_mode == 'AxisAngle':
                coll.prop(self, 'default_value_s0', text='X')
                coll.prop(self, 'default_value_s1', text='Y')
                coll.prop(self, 'default_value_s2', text='Z')
                coll.separator()
                coll.prop(self, 'default_value_s3', text='Angle')

    def draw_color(self, context, node):
        return socket_colors[self.bl_idname]

    default_value_mode: EnumProperty(
        items=[('EulerAngles', 'Euler Angles', 'Euler Angles'),
               ('AxisAngle', 'Axis/Angle', 'Axis/Angle'),
               ('Quaternion', 'Quaternion', 'Quaternion')],
        name='', default='EulerAngles',
        update=on_mode_update)

    default_value_unit: EnumProperty(
        items=[('Deg', 'Degrees', 'Degrees'),
               ('Rad', 'Radians', 'Radians')],
        name='', default='Rad',
        update=on_unit_update)
    default_value_order: EnumProperty(
        items=[('XYZ','XYZ','XYZ'),
               ('XZY','XZY (legacy Armory euler order)','XZY (legacy Armory euler order)'),
               ('YXZ','YXZ','YXZ'),
               ('YZX','YZX','YZX'),
               ('ZXY','ZXY','ZXY'),
               ('ZYX','ZYX','ZYX')],
        name='', default='XYZ'
    )

    default_value_s0: FloatProperty(update=do_update_raw)
    default_value_s1: FloatProperty(update=do_update_raw)
    default_value_s2: FloatProperty(update=do_update_raw)
    default_value_s3: FloatProperty(update=do_update_raw)

    default_value_raw: FloatVectorProperty(
        name='Value',
        description='Raw quaternion obtained for the default value of a ArmRotationSocket socket',
        size=4, default=(0,0,0,1),
        update = _on_update_socket
    )

    def copy_defaults(self, socket):
        if socket.bl_idname == self.bl_idname:
            socket.default_value_mode = self.default_value_mode
            socket.default_value_unit = self.default_value_unit
            socket.default_value_order = self.default_value_order
            socket.default_value_s0 = self.default_value_s0
            socket.default_value_s1 = self.default_value_s1
            socket.default_value_s2 = self.default_value_s2
            socket.default_value_s3 = self.default_value_s3
            socket.default_value_raw = self.default_value_raw


class ArmArraySocket(ArmCustomSocket):
    bl_idname = 'ArmNodeSocketArray'
    bl_label = 'Array Socket'
    arm_socket_type = 'NONE'

    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    def draw_color(self, context, node):
        return socket_colors[self.bl_idname]


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
        return socket_colors[self.bl_idname]

    def get_default_value(self):
        return self.default_value_raw

    def copy_defaults(self, socket):
        if socket.bl_idname == self.bl_idname:
            socket.default_value_raw = self.default_value_raw


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
        default=[0.0, 0.0, 0.0, 1.0],
        description='Input value used for unconnected socket',
        update=_on_update_socket
    )

    def draw(self, context, layout, node, text):
        draw_socket_layout_split(self, layout)

    def draw_color(self, context, node):
        return socket_colors[self.bl_idname]

    def get_default_value(self):
        return self.default_value_raw

    def copy_defaults(self, socket):
        if socket.bl_idname == self.bl_idname:
            socket.default_value_raw = self.default_value_raw


class ArmDynamicSocket(ArmCustomSocket):
    bl_idname = 'ArmDynamicSocket'
    bl_label = 'Dynamic Socket'
    arm_socket_type = 'NONE'

    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    def draw_color(self, context, node):
        return socket_colors[self.bl_idname]


class ArmAnySocket(ArmCustomSocket):
    bl_idname = 'ArmAnySocket'
    bl_label = 'Any Socket'
    arm_socket_type = 'NONE'

    # Callback function when socket label is changed
    def on_disp_label_update(self, context):
        node = self.node
        if node.bl_idname == 'LNGroupInputsNode' or node.bl_idname == 'LNGroupOutputsNode':
            if not node.invalid_link:
                node.socket_name_update(self)
                self.on_node_update()
                self.name = self.display_label

    display_label: StringProperty(
        name='display_label',
        description='Property to store socket display name',
        update=on_disp_label_update)

    display_color: FloatVectorProperty(
        name='Color',
        size=4,
        subtype='COLOR',
        min=0.0,
        max=1.0,
        default=socket_colors['ArmAnySocket']
    )

    def draw(self, context, layout, node, text):
        layout.label(text=self.display_label)

    def draw_color(self, context, node):
        return self.display_color

    def on_node_update(self):
        # Cache name and color of connected socket
        if self.is_output:
            c_node, c_socket = arm.node_utils.output_get_connected_node(self)
        else:
            c_node, c_socket = arm.node_utils.input_get_connected_node(self)

        if c_node is None:
            self.display_color = socket_colors[self.__class__.bl_idname]
        else:
            if self.display_label == '':
                self.display_label = c_socket.name
            self.display_color = c_socket.draw_color(bpy.context, c_node)


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
        return socket_colors[self.bl_idname]

    def get_default_value(self):
        return self.default_value_raw

    def copy_defaults(self, socket):
        if socket.bl_idname == self.bl_idname:
            socket.default_value_raw = self.default_value_raw

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
        return socket_colors[self.bl_idname]

    def get_default_value(self):
        return self.default_value_raw

    def copy_defaults(self, socket):
        if socket.bl_idname == self.bl_idname:
            socket.default_value_raw = self.default_value_raw

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
        return socket_colors[self.bl_idname]

    def copy_defaults(self, socket):
        if socket.bl_idname == self.bl_idname:
            socket.default_value_raw = self.default_value_raw

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
        return socket_colors[self.bl_idname]

    def get_default_value(self):
        return self.default_value_raw

    def copy_defaults(self, socket):
        if socket.bl_idname == self.bl_idname:
            socket.default_value_raw = self.default_value_raw

class ArmVectorSocket(ArmCustomSocket):
    bl_idname = 'ArmVectorSocket'
    bl_label = 'Vector Socket'
    arm_socket_type = 'VECTOR'

    default_value_raw: FloatVectorProperty(
        name='Value',
        size=3,
        precision=3,
        description='Input value used for unconnected socket',
        update=_on_update_socket
    )

    def draw(self, context, layout, node, text):
        if not self.is_output and not self.is_linked:
            col = layout.column(align=True)
            col.label(text=self.name + ":")
            col.prop(self, 'default_value_raw', text='')
        else:
            layout.label(text=self.name)

    def draw_color(self, context, node):
        return socket_colors[self.bl_idname]

    def get_default_value(self):
        return self.default_value_raw

    def copy_defaults(self, socket):
        if socket.bl_idname == self.bl_idname:
            socket.default_value_raw = self.default_value_raw

class ArmAnimTreeSocket(ArmCustomSocket):
    bl_idname = 'ArmNodeSocketAnimTree'
    bl_label = 'Animation Tree Socket'
    arm_socket_type = 'NONE'

    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    def draw_color(self, context, node):
        return socket_colors[self.bl_idname]

class ArmFactorSocket(ArmCustomSocket):
    bl_idname = 'ArmFactorSocket'
    bl_label = 'Factor Socket'
    arm_socket_type = 'FACTOR'

    default_value_raw: FloatProperty(
        name='Factor',
        description='Input value used for unconnected socket in the range [0 , 1]',
        precision=3,
        min = 0.0,
        max = 1.0,
        update=_on_update_socket
    )

    def draw(self, context, layout, node, text):
        draw_socket_layout(self, layout)

    def draw_color(self, context, node):
        return socket_colors[self.bl_idname]

    def get_default_value(self):
        return self.default_value_raw

class ArmBlendSpaceSocket(ArmCustomSocket):
    bl_idname = 'ArmBlendSpaceSocket'
    bl_label = 'Blend Space Socket'
    arm_socket_type = 'FACTOR'

    default_value_raw: FloatProperty(
        name='Factor',
        description='Input value used for unconnected socket in the range [0 , 1]',
        precision=3,
        min = 0.0,
        max = 1.0,
        update=_on_update_socket
    )

    def draw(self, context, layout, node, text):
        draw_socket_layout(self, layout)

    def draw_color(self, context, node):
        return socket_colors[self.bl_idname]

    def get_default_value(self):
        return self.default_value_raw

    def set_default_value(self, value):
        self.default_value_raw = value

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


if bpy.app.version < (4, 1, 0):
    def _make_socket_interface(interface_name: str, bl_idname: str) -> Type[bpy.types.NodeSocketInterface]:
        """Create a socket interface class that is used by Blender for node
        groups. We currently don't use real node groups, but without these
        classes Blender will (incorrectly) draw the socket borders in light grey.
        """
        def draw(self, context, layout):
            pass

        def draw_color(self, context):
            # This would be used if we were using "real" node groups
            return 0, 0, 0, 1

        cls = type(
            interface_name,
            (bpy.types.NodeSocketInterface, ), {
                'bl_socket_idname': bl_idname,
                'draw': draw,
                'draw_color': draw_color,
            }
        )
        return cls
else:
    def _make_socket_interface(interface_name: str, bl_idname: str) -> Type[bpy.types.NodeTreeInterfaceSocket]:
        """Create a socket interface class that is used by Blender for node
        groups. We currently don't use real node groups, but without these
        classes Blender will (incorrectly) draw the socket borders in light grey.
        """
        def draw(self, context, layout):
            pass

        def draw_color(self, context):
            # This would be used if we were using "real" node groups
            return 0, 0, 0, 1

        cls = type(
            interface_name,
            (bpy.types.NodeTreeInterfaceSocket, ), {
                'bl_socket_idname': bl_idname,
                'draw': draw,
                'draw_color': draw_color,
            }
        )
        return cls   


ArmActionSocketInterface = _make_socket_interface('ArmActionSocketInterface', 'ArmNodeSocketAction')
ArmAnimSocketInterface = _make_socket_interface('ArmAnimSocketInterface', 'ArmNodeSocketAnimAction')
ArmRotationSocketInterface = _make_socket_interface('ArmRotationSocketInterface', 'ArmRotationSocket')
ArmArraySocketInterface = _make_socket_interface('ArmArraySocketInterface', 'ArmNodeSocketArray')
ArmBoolSocketInterface = _make_socket_interface('ArmBoolSocketInterface', 'ArmBoolSocket')
ArmColorSocketInterface = _make_socket_interface('ArmColorSocketInterface', 'ArmColorSocket')
ArmDynamicSocketInterface = _make_socket_interface('ArmDynamicSocketInterface', 'ArmDynamicSocket')
ArmFloatSocketInterface = _make_socket_interface('ArmFloatSocketInterface', 'ArmFloatSocket')
ArmIntSocketInterface = _make_socket_interface('ArmIntSocketInterface', 'ArmIntSocket')
ArmObjectSocketInterface = _make_socket_interface('ArmObjectSocketInterface', 'ArmNodeSocketObject')
ArmStringSocketInterface = _make_socket_interface('ArmStringSocketInterface', 'ArmStringSocket')
ArmVectorSocketInterface = _make_socket_interface('ArmVectorSocketInterface', 'ArmVectorSocket')
ArmAnySocketInterface = _make_socket_interface('ArmAnySocketInterface', 'ArmAnySocket')
ArmAnimTreeSocketInterface = _make_socket_interface('ArmAnimTreeSocketInterface', 'ArmNodeSocketAnimTree')
ArmFactorSocketInterface = _make_socket_interface('ArmFactorSocketInterface', 'ArmFactorSocket')
ArmBlendSpaceSocketInterface = _make_socket_interface('ArmBlendSpaceSocketInterface', 'ArmBlendSpaceSocket')

__REG_CLASSES = (
    ArmActionSocketInterface,
    ArmAnimSocketInterface,
    ArmRotationSocketInterface,
    ArmArraySocketInterface,
    ArmBoolSocketInterface,
    ArmColorSocketInterface,
    ArmDynamicSocketInterface,
    ArmFloatSocketInterface,
    ArmIntSocketInterface,
    ArmObjectSocketInterface,
    ArmStringSocketInterface,
    ArmVectorSocketInterface,
    ArmAnySocketInterface,
    ArmAnimTreeSocketInterface,
    ArmFactorSocketInterface,
    ArmBlendSpaceSocketInterface,

    ArmActionSocket,
    ArmAnimActionSocket,
    ArmRotationSocket,
    ArmArraySocket,
    ArmBoolSocket,
    ArmColorSocket,
    ArmDynamicSocket,
    ArmFloatSocket,
    ArmIntSocket,
    ArmObjectSocket,
    ArmStringSocket,
    ArmVectorSocket,
    ArmAnySocket,
    ArmAnimTreeSocket,
    ArmFactorSocket,
    ArmBlendSpaceSocket,
)
register, unregister = bpy.utils.register_classes_factory(__REG_CLASSES)
