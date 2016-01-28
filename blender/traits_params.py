import shutil
import bpy
import os
import json
from bpy.types import Menu, Panel, UIList
from bpy.props import *

class ListParamsTraitItem(bpy.types.PropertyGroup):
	# Group of properties representing an item in the list
	name = bpy.props.StringProperty(
		   name="Name",
		   description="A name for this item",
		   default="Untitled")
		   
	# enabled_prop = bpy.props.BoolProperty(
	#        name="",
	#        description="A name for this item",
	#        default=True)



class MY_UL_ParamsTraitList(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		# We could write some code to decide which icon to use here...
		custom_icon = 'OBJECT_DATAMODE'

		# Make sure your code supports all 3 layout types
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			#layout.prop(item, "enabled_prop")
			#layout.label(item.name, icon = custom_icon)
			layout.prop(item, "name", text="", emboss=False, icon=custom_icon)

		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			layout.label("", icon = custom_icon)

def initObjectProperties():
	bpy.types.Object.my_paramstraitlist = bpy.props.CollectionProperty(type = ListParamsTraitItem)
	bpy.types.Object.paramstraitlist_index = bpy.props.IntProperty(name = "Index for my_list", default = 0)

class LIST_OT_ParamsTraitNewItem(bpy.types.Operator):
	# Add a new item to the list
	bl_idname = "my_paramstraitlist.new_item"
	bl_label = "Add a new item"

	def execute(self, context):
		bpy.context.object.my_paramstraitlist.add()
		bpy.context.object.paramstraitlist_index += 1
		return{'FINISHED'}


class LIST_OT_ParamsTraitDeleteItem(bpy.types.Operator):
	# Delete the selected item from the list
	bl_idname = "my_paramstraitlist.delete_item"
	bl_label = "Deletes an item"

	@classmethod
	def poll(self, context):
		""" Enable if there's something in the list """
		return len(bpy.context.object.my_paramstraitlist) > 0

	def execute(self, context):
		list = bpy.context.object.my_paramstraitlist
		index = bpy.context.object.paramstraitlist_index

		list.remove(index)

		if index > 0:
			index = index - 1

		bpy.context.object.paramstraitlist_index = index
		return{'FINISHED'}


class LIST_OT_ParamsTraitMoveItem(bpy.types.Operator):
	# Move an item in the list
	bl_idname = "my_paramstraitlist.move_item"
	bl_label = "Move an item in the list"
	direction = bpy.props.EnumProperty(
				items=(
					('UP', 'Up', ""),
					('DOWN', 'Down', ""),))

	@classmethod
	def poll(self, context):
		""" Enable if there's something in the list. """
		return len(bpy.context.object.my_paramstraitlist) > 0


	def move_index(self):
		# Move index of an item render queue while clamping it
		index = bpy.context.object.paramstraitlist_index
		list_length = len(bpy.context.object.my_paramstraitlist) - 1
		new_index = 0

		if self.direction == 'UP':
			new_index = index - 1
		elif self.direction == 'DOWN':
			new_index = index + 1

		new_index = max(0, min(new_index, list_length))
		index = new_index


	def execute(self, context):
		list = bpy.context.object.my_paramstraitlist
		index = bpy.context.object.paramstraitlist_index

		if self.direction == 'DOWN':
			neighbor = index + 1
			#queue.move(index,neighbor)
			self.move_index()

		elif self.direction == 'UP':
			neighbor = index - 1
			#queue.move(neighbor, index)
			self.move_index()
		else:
			return{'CANCELLED'}
		return{'FINISHED'}

def register():
	bpy.utils.register_module(__name__)
	initObjectProperties()

def unregister():
	bpy.utils.unregister_module(__name__)
