from math import pi, cos, sin, sqrt
import bpy
from bpy.props import PointerProperty, EnumProperty, FloatProperty, FloatVectorProperty
from bpy.types import NodeSocket
import mathutils

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

    
class ArmRotationSocket(ArmCustomSocket):
    bl_idname = 'ArmNodeSocketRotation'
    bl_label = 'Rotation Socket'
    arm_socket_type = 'ROTATION'  # the internal representation is a quaternion, AKA a '4D vector' (using mathutils.Vector((x,y,z,w)))
    
    def get_default_value(self):
        if self.default_value_raw is None:
            return Vector((0.0,0.0,0.0,1.0))
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
        if self.default_value_mode == 'Quat':
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
        ``param1`` is in ('Quat', 'EulerAngles', 'AxisAngle'),
        ``param2`` is in ('Rad','Deg') for both EulerAngles and AxisAngle,
        ``param3`` is a len-3 string like "XYZ", for EulerAngles """
        if param1 == 'Quat':
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
            self.defualt_value_unit,
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
            elif self.default_value_mode == 'Quat':
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
        return 0.68, 0.22, 0.62, 1

    default_value_mode: EnumProperty(
        items=[('EulerAngles', 'Euler Angles', 'Euler Angles'),
               ('AxisAngle', 'Axis/Angle', 'Axis/Angle'),
               ('Quat', 'Quaternion', 'Quaternion')],
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

    default_value_raw: FloatVectorProperty(size=4, default=(0,0,0,1))


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
    bpy.utils.register_class(ArmRotationSocket)
    bpy.utils.register_class(ArmArraySocket)
    bpy.utils.register_class(ArmObjectSocket)


def unregister():
    bpy.utils.unregister_class(ArmObjectSocket)
    bpy.utils.unregister_class(ArmArraySocket)
    bpy.utils.unregister_class(ArmAnimActionSocket)
    bpy.utils.unregister_class(ArmRotationSocket)
    bpy.utils.unregister_class(ArmActionSocket)
