import bpy
from bpy.types import NodeTree
from bpy.props import *
import nodeitems_utils
from nodeitems_utils import NodeCategory
from arm.logicnode import *
import webbrowser

registered_nodes = []

class ArmLogicTree(NodeTree):
    '''Logic nodes'''
    bl_idname = 'ArmLogicTreeType'
    bl_label = 'Logic Node Editor'
    bl_icon = 'DECORATE'

class LogicNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType'

def register_nodes():
    global registered_nodes

    # Re-register all nodes for now..
    if len(registered_nodes) > 0:
        unregister_nodes()

    for n in arm_nodes.nodes:
        registered_nodes.append(n)
        bpy.utils.register_class(n)

    node_categories = []

    for category in sorted(arm_nodes.category_items):
        sorted_items=sorted(arm_nodes.category_items[category], key=lambda item: item.nodetype)
        node_categories.append(
            LogicNodeCategory('Logic' + category + 'Nodes', category, items=sorted_items)
        )

    nodeitems_utils.register_node_categories('ArmLogicNodes', node_categories)

def unregister_nodes():
    global registered_nodes
    for n in registered_nodes:
        bpy.utils.unregister_class(n)
    registered_nodes = []
    nodeitems_utils.unregister_node_categories('ArmLogicNodes')

class ARM_PT_LogicNodePanel(bpy.types.Panel):
    bl_label = 'Armory Logic Node'
    bl_idname = 'ARM_PT_LogicNodePanel'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Node'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        if context.active_node != None and context.active_node.bl_idname.startswith('LN'):
            layout.prop(context.active_node, 'arm_logic_id')
            layout.prop(context.active_node, 'arm_watch')
            layout.operator('arm.open_node_source')

class ArmOpenNodeSource(bpy.types.Operator):
    '''Expose Haxe source'''
    bl_idname = 'arm.open_node_source'
    bl_label = 'Open Node Source'
 
    def execute(self, context):
        if context.active_node != None and context.active_node.bl_idname.startswith('LN'):
            name = context.active_node.bl_idname[2:]
            webbrowser.open('https://github.com/armory3d/armory/tree/master/Sources/armory/logicnode/' + name + '.hx')
        return{'FINISHED'}

class ArmNodeSearch(bpy.types.Operator):
    '''Search nodes'''
    bl_idname = "arm.node_search"
    bl_label = "Node Search"
    bl_options = {"REGISTER"}
    bl_property = "item"

    def get_items(self, context):
        items = []
        for n in registered_nodes:
            items.append((n.bl_idname, n.bl_label, ''))
        return items

    item: EnumProperty(items=get_items)

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}

    def execute(self, context):
        bpy.ops.node.add_node(type=self.item, use_transform=True)
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

def draw_menu(self, context):
    if context.space_data.tree_type != "ArmLogicTreeType":
        return
    layout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator("arm.node_search", text="Search", icon="VIEWZOOM")
    layout.separator()

def register():
    bpy.utils.register_class(ArmLogicTree)
    bpy.utils.register_class(ARM_PT_LogicNodePanel)
    bpy.utils.register_class(ArmOpenNodeSource)
    register_nodes()
    bpy.utils.register_class(ArmNodeSearch)
    bpy.types.NODE_MT_add.prepend(draw_menu)

def unregister():
    bpy.types.NODE_MT_add.remove(draw_menu)
    bpy.utils.unregister_class(ArmNodeSearch)
    unregister_nodes()
    bpy.utils.unregister_class(ArmLogicTree)
    bpy.utils.unregister_class(ARM_PT_LogicNodePanel)
    bpy.utils.unregister_class(ArmOpenNodeSource)
