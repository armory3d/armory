import bpy
import textwrap
from bpy.props import *

import arm.props_ui

if arm.is_reload(__name__):
    arm.props_ui = arm.reload_module(arm.props_ui)
else:
    arm.enable_reload(__name__)

class ArmRetargetActions(bpy.types.Operator):
    bl_idname = 'arm.retarget_action'
    bl_label = 'Retarget action data'
    bl_description = 'Retargets action data from one bone to another for root motion'

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj.type != 'ARMATURE':
            return False
        if obj.mode != 'OBJECT':
            return False
        wrd = bpy.data.worlds['Arm']
        if wrd.arm_retarget_from == wrd.arm_retarget_to:
            return False
        if context.space_data.type == 'DOPESHEET_EDITOR':
            ds_mode = context.space_data.mode
            if ds_mode in {'DOPESHEET', 'ACTION'}:
                return bool(context.active_action)
        if context.space_data.type == 'NLA_EDITOR':
            if context.active_nla_strip:
                if context.active_nla_strip.action:
                    return True
        return False

    def execute(self, context):
        if context.space_data.type == 'DOPESHEET_EDITOR':
            ds_mode = context.space_data.mode
            if ds_mode in {'DOPESHEET', 'ACTION'}:
                self.action = context.active_action
        if context.space_data.type == 'NLA_EDITOR':
            self.action = context.active_nla_strip.action
        wrd = bpy.data.worlds['Arm']
        obj = context.object
        # Create helper object
        helper1 = bpy.data.objects.new(name="arm_helper_1", object_data=None)
        helper1.rotation_mode = 'QUATERNION'
        helper2 = bpy.data.objects.new(name="arm_helper_2", object_data=None)
        helper2.rotation_mode = 'QUATERNION'
        # Get bones
        pose = obj.pose
        from_bone = pose.bones.get(wrd.arm_retarget_from)
        to_bone = pose.bones.get(wrd.arm_retarget_to)
        if from_bone is None or to_bone is None:
            self.report({'ERROR'}, "Actions not retargeted. Armature or bones do not exist.")
            return{'CANCELLED'}
        # Copy selected transform bake to helper1
        helper1_scl = helper1.constraints.new('COPY_SCALE')
        helper1_scl.target = obj
        helper1_scl.subtarget = wrd.arm_retarget_from
        helper1_rot = helper1.constraints.new('COPY_ROTATION')
        helper1_rot.target = obj
        helper1_rot.subtarget = wrd.arm_retarget_from
        helper1_rot.use_x = wrd.arm_action_retarget_rot_x
        helper1_rot.use_y = wrd.arm_action_retarget_rot_y
        helper1_rot.use_z = wrd.arm_action_retarget_rot_z
        helper1_loc = helper1.constraints.new('COPY_LOCATION')
        helper1_loc.target = obj
        helper1_loc.subtarget = wrd.arm_retarget_from
        helper1_loc.use_x = wrd.arm_action_retarget_pos_x
        helper1_loc.use_y = wrd.arm_action_retarget_pos_y
        helper1_loc.use_z = wrd.arm_action_retarget_pos_z
        # Remove selected transform and bake to helper2
        helper2_scl = helper2.constraints.new('COPY_SCALE')
        helper2_scl.target = obj
        helper2_scl.subtarget = wrd.arm_retarget_from
        helper2_rot = helper2.constraints.new('COPY_ROTATION')
        helper2_rot.target = obj
        helper2_rot.subtarget = wrd.arm_retarget_from
        helper2_rot.use_x = not wrd.arm_action_retarget_rot_x
        helper2_rot.use_y = not wrd.arm_action_retarget_rot_y
        helper2_rot.use_z = not wrd.arm_action_retarget_rot_z
        helper2_loc = helper2.constraints.new('COPY_LOCATION')
        helper2_loc.target = obj
        helper2_loc.subtarget = wrd.arm_retarget_from
        helper2_loc.use_x = not wrd.arm_action_retarget_pos_x
        helper2_loc.use_y = not wrd.arm_action_retarget_pos_y
        helper2_loc.use_z = not wrd.arm_action_retarget_pos_z
        # Select helper only
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.collection.objects.link(helper1)
        bpy.context.scene.collection.objects.link(helper2)
        helper1.select_set(True)
        helper2.select_set(True)
        bpy.context.view_layer.objects.active = helper1
        obj.animation_data.action = self.action
        framerange = self.action.frame_range
         # Set helper locations
        bpy.context.scene.frame_set(1)
        world_loc = obj.matrix_world @ from_bone.head
        helper1.location = world_loc
        helper2.location = world_loc
        # Bake to helper
        bpy.ops.nla.bake(frame_start=int(framerange[0]), frame_end=int(framerange[1]), step=1, only_selected=True, visual_keying=True,
                         clear_constraints=True, clean_curves=True, clear_parents=False, use_current_action=False, bake_types={'OBJECT'})
        # Copy transform to new root bone
        copy_transform1 = to_bone.constraints.new('COPY_TRANSFORMS')
        copy_transform1.target = helper1
        # Copy transform from old root bone
        copy_transform2 = from_bone.constraints.new('COPY_TRANSFORMS')
        copy_transform2.target = helper2
        # Select from and to bones only
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        for bone in obj.data.bones:
            bone.select = False
        to_bone.bone.select = True
        from_bone.bone.select = True
        obj.data.bones.active = to_bone.bone
        framerange = self.action.frame_range
        obj.animation_data.action = self.action
        overwrite = wrd.arm_retarget_overwrite
        if not overwrite:
            new_action = self.action.copy()
            new_action.name = self.action.name + '_retarget'
            obj.animation_data.action = new_action
        # Bake to from and to bones
        bpy.ops.nla.bake(frame_start=int(framerange[0]), frame_end=int(framerange[1]), step=1, only_selected=True, visual_keying=True,
                         clear_constraints=True, clean_curves=True, clear_parents=False, use_current_action=True, bake_types={'POSE'})
        # Clean up
        bpy.data.actions.remove(helper1.animation_data.action)
        bpy.data.actions.remove(helper2.animation_data.action)
        bpy.data.objects.remove(helper1)
        bpy.data.objects.remove(helper2)
        self.report({'INFO'}, "Action retargeted successfully")
        return{'FINISHED'}

class ArmDrawRetargetPanel:

    @classmethod
    def check_bone(cls, armature, bone):
        if bone is not None:
            if armature is not None:
                return bone in armature.bones
        return False

    @classmethod 
    def draw(cls, context, action, layout):
        layout.label(text='Action: ' + action.name)
        wrd = bpy.data.worlds['Arm']
        # Armature Object
        layout.prop(wrd, 'arm_retarget_armature')
        con = False
        # From, To bones
        if wrd.arm_retarget_armature:
            if wrd.arm_retarget_armature.type == 'ARMATURE':
                con = True
                sub = layout.row(align=True)
                sub.label(text="From Bone:")
                sub.prop_search(wrd, 'arm_retarget_from', 
                                   wrd.arm_retarget_armature.data, "bones", text="")
                con = cls.check_bone(wrd.arm_retarget_armature.data, wrd.arm_retarget_from)
                sub = layout.row(align=True)
                sub.label(text="To Bone:")
                sub.prop_search(wrd,'arm_retarget_to',
                                   wrd.arm_retarget_armature.data, "bones", text="")
                con = cls.check_bone(wrd.arm_retarget_armature.data, wrd.arm_retarget_to)
        # Check if bones exist
        condition = con and bool(wrd.arm_retarget_from) and bool(wrd.arm_retarget_to)
        section = layout.column()
        section.enabled = condition
        # Position
        sub = section.row(align=True)
        sub.label(text="Position:")
        sub.prop(wrd, 'arm_action_retarget_pos_x', text='X', toggle=True)
        sub.prop(wrd, 'arm_action_retarget_pos_y', text='Y', toggle=True)
        sub.prop(wrd, 'arm_action_retarget_pos_z', text='Z', toggle=True)
        # Rotation
        sub = section.row(align=True)
        sub.label(text="Rotation:")
        sub.prop(wrd, 'arm_action_retarget_rot_x', text='X', toggle=True)
        sub.prop(wrd, 'arm_action_retarget_rot_y', text='Y', toggle=True)
        sub.prop(wrd, 'arm_action_retarget_rot_z', text='Z', toggle=True)
        # Retarget Operator
        sub = section.row()
        sub.prop(wrd, 'arm_retarget_overwrite')
        box = section.box()
        text='Retargeting will apply all constraints for the selected objects and then baked.'
        'The constraints are removed after retarget.'
        textwrap_width = int(bpy.context.region.width//2)
        col = arm.props_ui.draw_multiline_with_icon(box, textwrap_width, 'ERROR', text)
        sub = section.row(align=True)
        sub.operator('arm.retarget_action', text='Retarget', icon='FILE_REFRESH')

class ARM_PT_DSRootMotionRetargetPanel(bpy.types.Panel):
    bl_label = 'Armory Root Motion Retarget'
    bl_idname = 'ARM_PT_DSRootMotionRetargetPanel'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_context = 'data'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        ds_mode = context.space_data.mode
        if ds_mode in {'DOPESHEET', 'ACTION'}:
            return bool(context.active_action)

    def draw(self, context):
        ArmDrawRetargetPanel.draw(context, context.active_action, self.layout)

class ARM_PT_NLARootMotionRetargetPanel(bpy.types.Panel):
    bl_label = 'Armory Root Motion Retarget'
    bl_idname = 'ARM_PT_NLARootMotionRetargetPanel'
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_context = 'data'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        return bool(context.active_nla_strip)

    def draw(self, context):
        ArmDrawRetargetPanel.draw(context, context.active_nla_strip.action, self.layout)

class ARM_PT_DopeSheetRootMotionPanel(bpy.types.Panel):
    bl_label = 'Armory Root Motion'
    bl_idname = 'ARM_PT_DopeSheetRootMotionPanel'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_context = 'data'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        ds_mode = context.space_data.mode
        if ds_mode in {'DOPESHEET', 'ACTION'}:
            return bool(context.active_action)

    def draw(self, context):
        action = context.active_action
        layout = self.layout
        layout.label(text='Action: ' + action.name)
        layout.prop(action, 'arm_root_motion_pos')
        layout.prop(action, 'arm_root_motion_rot')

class ARM_PT_NLARootMotionPanel(bpy.types.Panel):
    bl_label = 'Armory Root Motion'
    bl_idname = 'ARM_PT_NLARootMotionPanel'
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_context = 'data'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        return bool(context.active_nla_strip)

    def draw(self, context):
        action = context.active_nla_strip.action
        layout = self.layout
        layout.label(text='Action: ' + action.name)
        layout.prop(action, 'arm_root_motion_pos')
        layout.prop(action, 'arm_root_motion_rot')

__REG_CLASSES = (
    ArmRetargetActions,
    ARM_PT_DSRootMotionRetargetPanel,
    ARM_PT_NLARootMotionRetargetPanel,
    ARM_PT_DopeSheetRootMotionPanel,
    ARM_PT_NLARootMotionPanel,
)
__reg_classes, __unreg_classes = bpy.utils.register_classes_factory(__REG_CLASSES)

def register():
    __reg_classes()

def unregister():
    __unreg_classes()
