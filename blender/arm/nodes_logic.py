from typing import Any, Callable
import webbrowser

import bl_operators
import bpy
import blf
from bpy.props import BoolProperty, CollectionProperty, StringProperty

import arm.logicnode.arm_nodes as arm_nodes
import arm.logicnode.replacement
import arm.logicnode.tree_variables
import arm.logicnode.arm_node_group
import arm.logicnode
import arm.props_traits
import arm.ui_icons as ui_icons
import arm.utils

if arm.is_reload(__name__):
    arm_nodes = arm.reload_module(arm_nodes)
    arm.logicnode.replacement = arm.reload_module(arm.logicnode.replacement)
    arm.logicnode.tree_variables = arm.reload_module(arm.logicnode.tree_variables)
    arm.logicnode = arm.reload_module(arm.logicnode)
    arm.props_traits = arm.reload_module(arm.props_traits)
    ui_icons = arm.reload_module(ui_icons)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)

INTERNAL_GROUPS_MENU_ID = 'ARM_INTERNAL_GROUPS'
internal_groups_menu_class: bpy.types.Menu

registered_nodes = []
registered_categories = []


class ArmLogicTree(bpy.types.NodeTree):
    """Logic nodes"""
    bl_idname = 'ArmLogicTreeType'
    bl_label = 'Logic Node Editor'
    bl_icon = 'NODETREE'

    def update(self):
        pass


class ARM_MT_NodeAddOverride(bpy.types.Menu):
    """
    Overrides the `Add node` menu. If called from the logic node
    editor, the custom menu is drawn, otherwise the default one is drawn.

    TODO: Find a better solution to custom menus, this will conflict
     with other add-ons overriding this menu.
    """
    bl_idname = "NODE_MT_add"
    bl_label = "Add"
    bl_translation_context = bpy.app.translations.contexts.operator_default

    overridden_menu: bpy.types.Menu = None
    overridden_draw: Callable = None

    def draw(self, context):
        if context.space_data.tree_type == 'ArmLogicTreeType':
            layout = self.layout

            # Invoke the search
            layout.operator_context = "INVOKE_DEFAULT"
            layout.operator('arm.node_search', icon="VIEWZOOM")

            for category_section in arm_nodes.category_items.values():
                layout.separator()

                for category in category_section:
                    safe_category_name = arm.utils.safesrc(category.name.lower())
                    layout.menu(f'ARM_MT_{safe_category_name}_menu', text=category.name, icon=category.icon)

            if arm.logicnode.arm_node_group.ArmGroupTree.has_linkable_group_trees():
                layout.separator()
                layout.menu(f'ARM_MT_{INTERNAL_GROUPS_MENU_ID}_menu', text=internal_groups_menu_class.bl_label, icon='OUTLINER_OB_GROUP_INSTANCE')

        else:
            ARM_MT_NodeAddOverride.overridden_draw(self, context)


class ARM_OT_AddNodeOverride(bpy.types.Operator):
    bl_idname = "arm.add_node_override"
    bl_label = "Add Node"
    bl_property = "type"
    bl_options = {'INTERNAL'}

    type: StringProperty(name="NodeItem type")
    use_transform: BoolProperty(name="Use Transform")
    settings: CollectionProperty(
        name="Settings",
        description="Settings to be applied on the newly created node",
        type=bl_operators.node.NodeSetting,
        options={'SKIP_SAVE'},
    )

    def invoke(self, context, event):
        # Passing collection properties as operator parameters only
        # works via raw sequences of dicts:
        # https://blender.stackexchange.com/a/298977/58208
        # https://github.com/blender/blender/blob/cf1e1ed46b7ec80edb0f43cb514d3601a1696ec1/source/blender/python/intern/bpy_rna.c#L2033-L2043
        setting_dicts = []
        for setting in self.settings.values():
            setting_dicts.append({
                "name": setting.name,
                "value": setting.value
            })

        bpy.ops.node.add_node('INVOKE_DEFAULT', type=self.type, use_transform=self.use_transform, settings=setting_dicts)
        return {'FINISHED'}

    @classmethod
    def description(cls, context, properties):
        """Show the node's bl_description attribute as a tooltip or, if
        it doesn't exist, its docstring."""
        nodetype = arm.utils.type_name_to_type(properties.type)

        if hasattr(nodetype, 'bl_description'):
            return nodetype.bl_description.split('.')[0]

        if nodetype.__doc__ is None:
            return ""

        return nodetype.__doc__.split('.')[0].strip()

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType' and context.space_data.edit_tree


def get_category_draw_func(category: arm_nodes.ArmNodeCategory):
    def draw_category_menu(self, context):
        layout = self.layout

        for index, node_section in enumerate(category.node_sections.values()):
            if index != 0:
                layout.separator()

            for node_item in node_section:
                op = layout.operator("arm.add_node_override", text=node_item.label)
                op.type = node_item.nodetype
                op.use_transform = True

    return draw_category_menu


def register_nodes():
    global registered_nodes, internal_groups_menu_class

    # Re-register all nodes for now..
    if len(registered_nodes) > 0 or len(registered_categories) > 0:
        unregister_nodes()

    arm.logicnode.init_nodes(subpackages_only=True)

    for node_type in arm_nodes.nodes:
        # Don't register internal nodes, they are already registered
        if not issubclass(node_type, bpy.types.NodeInternal):
            registered_nodes.append(node_type)
            bpy.utils.register_class(node_type)

    # Also add Blender's layout nodes
    arm_nodes.add_node(bpy.types.NodeReroute, 'Layout')
    arm_nodes.add_node(bpy.types.NodeFrame, 'Layout')

    # Generate and register category menus
    for category_section in arm_nodes.category_items.values():
        for category in category_section:
            category.sort_nodes()
            safe_category_name = arm.utils.safesrc(category.name.lower())
            assert(safe_category_name != INTERNAL_GROUPS_MENU_ID)  # see below
            menu_class = type(f'ARM_MT_{safe_category_name}Menu', (bpy.types.Menu, ), {
                'bl_space_type': 'NODE_EDITOR',
                'bl_idname': f'ARM_MT_{safe_category_name}_menu',
                'bl_label': category.name,
                'bl_description': category.description,
                'draw': get_category_draw_func(category)
            })
            registered_categories.append(menu_class)

            bpy.utils.register_class(menu_class)

    # Generate and register group menu
    def draw_nodegroups_menu(self, context):
        layout = self.layout

        tree: arm.logicnode.arm_node_group.ArmGroupTree
        for tree in arm.logicnode.arm_node_group.ArmGroupTree.get_linkable_group_trees():
            op = layout.operator('arm.add_node_override', text=tree.name)
            op.type = 'LNCallGroupNode'
            op.use_transform = True
            item = op.settings.add()
            item.name = "group_tree"
            item.value = f'bpy.data.node_groups["{tree.name}"]'

    # Don't name categories like the content of the INTERNAL_GROUPS_MENU_ID variable!
    menu_class = type(f'ARM_MT_{INTERNAL_GROUPS_MENU_ID}Menu', (bpy.types.Menu,), {
        'bl_space_type': 'NODE_EDITOR',
        'bl_idname': f'ARM_MT_{INTERNAL_GROUPS_MENU_ID}_menu',
        'bl_label': 'Node Groups',
        'bl_description': 'List of node groups that can be added to the current tree',
        'draw': draw_nodegroups_menu
    })
    internal_groups_menu_class = menu_class
    bpy.utils.register_class(menu_class)


def unregister_nodes():
    global registered_nodes, registered_categories, internal_groups_menu_class

    for n in registered_nodes:
        if issubclass(n, arm_nodes.ArmLogicTreeNode):
            n.on_unregister()
        bpy.utils.unregister_class(n)
    registered_nodes = []

    for c in registered_categories:
        bpy.utils.unregister_class(c)
    registered_categories = []

    if internal_groups_menu_class is not None:
        bpy.utils.unregister_class(internal_groups_menu_class)
        internal_groups_menu_class = None


class ARM_PT_LogicNodePanel(bpy.types.Panel):
    bl_label = 'Armory Logic Node'
    bl_idname = 'ARM_PT_LogicNodePanel'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType' and context.space_data.edit_tree

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        if context.active_node is not None and context.active_node.bl_idname.startswith('LN'):
            layout.prop(context.active_node, 'arm_watch')

            layout.separator()
            layout.operator('arm.open_node_documentation', icon='HELP')
            column = layout.column(align=True)
            column.operator('arm.open_node_python_source', icon='FILE_SCRIPT')
            column.operator('arm.open_node_haxe_source', icon_value=ui_icons.get_id("haxe"))


class ArmOpenNodeHaxeSource(bpy.types.Operator):
    """Expose Haxe source"""
    bl_idname = 'arm.open_node_haxe_source'
    bl_label = 'Open Node Haxe Source'

    def execute(self, context):
        if context.selected_nodes is not None:
            if len(context.selected_nodes) == 1:
                if context.selected_nodes[0].bl_idname.startswith('LN'):
                    name = context.selected_nodes[0].bl_idname[2:]
                    version = arm.utils.get_last_commit()
                    if version == '':
                        version = 'main'
                    webbrowser.open(f'https://github.com/armory3d/armory/tree/{version}/Sources/armory/logicnode/{name}.hx')
        return{'FINISHED'}


class ArmOpenNodePythonSource(bpy.types.Operator):
    """Expose Python source"""
    bl_idname = 'arm.open_node_python_source'
    bl_label = 'Open Node Python Source'

    def execute(self, context):
        if context.selected_nodes is not None:
            if len(context.selected_nodes) == 1:
                node = context.selected_nodes[0]
                if node.bl_idname.startswith('LN') and node.arm_version is not None:
                    version = arm.utils.get_last_commit()
                    if version == '':
                        version = 'main'
                    rel_path = node.__module__.replace('.', '/')
                    webbrowser.open(f'https://github.com/armory3d/armory/tree/{version}/blender/{rel_path}.py')
        return{'FINISHED'}


class ArmOpenNodeWikiEntry(bpy.types.Operator):
    """Open the logic node's documentation in the Armory wiki"""
    bl_idname = 'arm.open_node_documentation'
    bl_label = 'Open Node Documentation'

    def execute(self, context):
        if context.selected_nodes is not None:
            if len(context.selected_nodes) == 1:
                node = context.selected_nodes[0]
                if node.bl_idname.startswith('LN') and node.arm_version is not None:
                    anchor = node.bl_label.lower().replace(" ", "-")

                    category = arm_nodes.eval_node_category(node)
                    category_section = arm_nodes.get_category(category).category_section

                    webbrowser.open(f'https://github.com/armory3d/armory/wiki/reference_{category_section}#{anchor}')

        return {'FINISHED'}


class ARM_PT_NodeDevelopment(bpy.types.Panel):
    """Sidebar panel to ease development of logic nodes."""
    bl_label = 'Node Development'
    bl_idname = 'ARM_PT_NodeDevelopment'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType' and context.space_data.edit_tree

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        node = context.active_node
        if node is not None and node.bl_idname.startswith('LN'):
            box = layout.box()
            box.label(text='Selected Node')
            col = box.column(align=True)

            self._draw_row(col, 'bl_idname', node.bl_idname)
            self._draw_row(col, 'Category', arm_nodes.eval_node_category(node))
            self._draw_row(col, 'Section', node.arm_section)
            self._draw_row(col, 'Specific Version', node.arm_version)
            self._draw_row(col, 'Class Version', node.__class__.arm_version)
            self._draw_row(col, 'Is Deprecated', node.arm_is_obsolete)

            is_var_node = isinstance(node, arm_nodes.ArmLogicVariableNodeMixin)
            self._draw_row(col, 'Is Variable Node', is_var_node)
            self._draw_row(col, 'Logic ID', node.arm_logic_id)
            if is_var_node:
                self._draw_row(col, 'Is Master Node', node.is_master_node)

            layout.separator()
            layout.operator('arm.node_replace_all')

    @staticmethod
    def _draw_row(col: bpy.types.UILayout, text: str, val: Any):
        split = col.split(factor=0.4)
        split.label(text=text)
        split.label(text=str(val))


class ARM_OT_ReplaceNodesOperator(bpy.types.Operator):
    bl_idname = "arm.node_replace_all"
    bl_label = "Replace Deprecated Nodes"
    bl_description = "Replace all deprecated nodes in the active node tree"
    bl_options = {'REGISTER'}

    def execute(self, context):
        arm.logicnode.replacement.replace_all()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.space_data is not None and context.space_data.type == 'NODE_EDITOR'

class ARM_UL_InterfaceSockets(bpy.types.UIList):
    """UI List of input and output sockets"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        socket = item
        color = socket.draw_color(context, context.active_node)

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)

            row.template_node_socket(color=color)
            row.prop(socket, "display_label", text="", emboss=False, icon_value=icon)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.template_node_socket(color=color)

class DrawNodeBreadCrumbs():
    """A class to draw node tree breadcrumbs or context path"""
    draw_handler = None

    @classmethod
    def convert_array_to_string(cls, arr):
        return ' > '.join(arr)

    @classmethod
    def draw(cls, context):
        if  context.space_data.edit_tree and context.space_data.node_tree.bl_idname == "ArmLogicTreeType":
            height = context.area.height
            path_data = [path.node_tree.name for path in context.space_data.path]
            str = cls.convert_array_to_string(path_data)
            blf.position(0, 20, height-60, 0)
            if bpy.app.version < (4, 1, 0):
                blf.size(0, 15, 72)
            else:
                blf.size(15, 72)
            blf.draw(0, str)

    @classmethod
    def register_draw(cls):
        if cls.draw_handler is not None:
            cls.unregister_draw()
        cls.draw_handler = bpy.types.SpaceNodeEditor.draw_handler_add(cls.draw, tuple([bpy.context]), 'WINDOW', 'POST_PIXEL')

    @classmethod
    def unregister_draw(cls):
        if cls.draw_handler is not None:
            bpy.types.SpaceNodeEditor.draw_handler_remove(cls.draw_handler, 'WINDOW')
            cls.draw_handler = None


__REG_CLASSES = (
    ArmLogicTree,
    ArmOpenNodeHaxeSource,
    ArmOpenNodePythonSource,
    ArmOpenNodeWikiEntry,
    ARM_OT_ReplaceNodesOperator,
    ARM_MT_NodeAddOverride,
    ARM_OT_AddNodeOverride,
    ARM_UL_InterfaceSockets,
    ARM_PT_LogicNodePanel,
    ARM_PT_NodeDevelopment
)
__reg_classes, __unreg_classes = bpy.utils.register_classes_factory(__REG_CLASSES)


def register():
    arm.logicnode.arm_nodes.register()
    arm.logicnode.arm_sockets.register()
    arm.logicnode.arm_node_group.register()
    arm.logicnode.tree_variables.register()

    ARM_MT_NodeAddOverride.overridden_menu = bpy.types.NODE_MT_add
    ARM_MT_NodeAddOverride.overridden_draw = bpy.types.NODE_MT_add.draw

    __reg_classes()

    arm.logicnode.init_categories()
    DrawNodeBreadCrumbs.register_draw()
    register_nodes()


def unregister():
    unregister_nodes()
    DrawNodeBreadCrumbs.unregister_draw()
    # Ensure that globals are reset if the addon is enabled again in the same Blender session
    arm_nodes.reset_globals()

    __unreg_classes()
    bpy.utils.register_class(ARM_MT_NodeAddOverride.overridden_menu)

    arm.logicnode.tree_variables.unregister()
    arm.logicnode.arm_node_group.unregister()
    arm.logicnode.arm_sockets.unregister()
    arm.logicnode.arm_nodes.unregister()
