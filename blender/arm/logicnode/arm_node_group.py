# Some parts of this code is reused from project Sverchok. 
# https://https://github.com/nortikin/sverchok/blob/master/core/node_group.py
#
# SPDX-License-Identifier: GPL3
# License-Filename: LICENSE

import bpy
from bpy.props import BoolProperty, EnumProperty
from itertools import zip_longest, chain, cycle, islice
from functools import reduce
from mathutils import Vector

from typing import List, Set, Dict, Optional
import bpy.types
from bpy.props import *
import arm
import arm.logicnode.arm_nodes as arm_nodes
from arm.logicnode.arm_nodes import ArmLogicTreeNode

if arm.is_reload(__name__):
    arm_nodes = arm.reload_module(arm_nodes)
    from arm.logicnode.arm_nodes import ArmLogicTreeNode
else:
    arm.enable_reload(__name__)

array_nodes = arm.logicnode.arm_nodes.array_nodes

class ArmGroupTree(bpy.types.NodeTree):
    """Separate tree class for sub trees"""
    bl_idname = 'ArmGroupTree'
    bl_icon = 'NODETREE'
    bl_label = 'Group tree'

    # should be updated by "Go to edit group tree" operator
    group_node_name: bpy.props.StringProperty(options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return False  # only for internal usage

    def upstream_trees(self) -> List['ArmGroupTree']:
        """
        Returns all the tree sub trees (in case if there are group nodes)
        and sub trees of sub trees and so on
        The method can help predict if linking new sub tree can lead to cyclic linking
        """
        next_group_nodes = [node for node in self.nodes if node.bl_idname == 'LNCallGroupNode']
        trees = [self]
        safe_counter = 0
        while next_group_nodes:
            next_node = next_group_nodes.pop()
            if next_node.group_tree:
                trees.append(next_node.group_tree)
                next_group_nodes.extend([
                    node for node in next_node.group_tree.nodes if node.bl_idname == 'LNCallGroupNode'])
            safe_counter += 1

            if safe_counter > 1000:
                raise RecursionError(f'Looks like group tree "{self}" has links to itself from other groups')
        return trees

    def can_be_linked(self):
        """Try to avoid creating loops of group trees with each other"""
        # upstream trees of tested treed should nad share trees with downstream trees of current tree
        tested_tree_upstream_trees = {t.name for t in self.upstream_trees()}
        current_tree_downstream_trees = {p.node_tree.name for p in bpy.context.space_data.path}
        shared_trees = tested_tree_upstream_trees & current_tree_downstream_trees
        return not shared_trees
    
    def update(self):
        pass

class ArmEditGroupTree(bpy.types.Operator):
    """Go into sub tree to edit"""
    bl_idname = 'arm.edit_group_tree'
    bl_label = 'Edit group tree'
    node_index: StringProperty(name='Node Index', default='')

    def execute(self, context):
        global array_nodes
        group_node = array_nodes[self.node_index]
        sub_tree: ArmLogicTree = group_node.group_tree
        context.space_data.path.append(sub_tree, node=group_node)
        sub_tree.group_node_name = group_node.name
        return {'FINISHED'}

class ArmCopyGroupTree(bpy.types.Operator):
    """Create a copy of this group tree and use it"""
    bl_idname = 'arm.copy_group_tree'
    bl_label = 'Copy group tree'
    node_index: StringProperty(name='Node Index', default='')

    def execute(self, context):
        global array_nodes
        group_node = array_nodes[self.node_index]
        group_tree = group_node.group_tree
        [setattr(n, 'copy_override', True) for n in group_tree.nodes
        if n.bl_idname in {'LNGroupInputsNode', 'LNGroupOutputsNode'}]
        new_group_tree = group_node.group_tree.copy()
        [setattr(n, 'copy_override', False) for n in group_tree.nodes
        if n.bl_idname in {'LNGroupInputsNode', 'LNGroupOutputsNode'}]
        group_node.group_tree = new_group_tree
        return {'FINISHED'}

class ArmSearchGroupTree(bpy.types.Operator):
    """Browse group trees to be linked"""
    bl_idname = 'arm.search_group_tree'
    bl_label = 'Search group tree'
    bl_property = 'tree_name'
    node_index: StringProperty(name='Node Index', default='')

    def available_trees(self, context):
        linkable_trees = filter(lambda t: hasattr(t, 'can_be_linked') and t.can_be_linked(), bpy.data.node_groups)
        return [(t.name, ('0 ' if t.users == 0 else '') + t.name, '') for t in linkable_trees]

    tree_name: bpy.props.EnumProperty(items=available_trees)

    def execute(self, context):
        global array_nodes
        tree_to_link = bpy.data.node_groups[self.tree_name]
        group_node = array_nodes[self.node_index]
        group_node.group_tree = tree_to_link
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

class ArmAddGroupTree(bpy.types.Operator):
    """Create empty sub tree for group node"""
    bl_idname = "arm.add_group_tree"
    bl_label = "Add group tree"
    node_index: StringProperty(name='Node Index', default='')

    @classmethod
    def poll(cls, context):
        path = getattr(context.space_data, 'path', [])
        if len(path):
            if path[-1].node_tree.bl_idname in {'ArmLogicTreeType', 'ArmGroupTree'}:
                return True
        return False

    def execute(self, context):
        """Link new sub tree to group node, create input and output nodes in sub tree and go to edit one"""
        global array_nodes
        sub_tree = bpy.data.node_groups.new('Armory group', 'ArmGroupTree')  # creating sub tree
        sub_tree.use_fake_user = True
        group_node = array_nodes[self.node_index]
        group_node.group_tree = sub_tree  # link sub tree to group node
        sub_tree.nodes.new('LNGroupInputsNode').location = (-250, 0)  # create node for putting data into sub tree
        sub_tree.nodes.new('LNGroupOutputsNode').location = (250, 0)  # create node for getting data from sub tree
        return bpy.ops.arm.edit_group_tree(node_index=self.node_index)

class ArmAddGroupTreeFromSelected(bpy.types.Operator):
    """Select nodes group node and placing them into sub tree"""
    bl_idname = "arm.add_group_tree_from_selected"
    bl_label = "Add group tree from selected"

    @classmethod
    def poll(cls, context):
        path = getattr(context.space_data, 'path', [])
        if len(path):
            if path[-1].node_tree.bl_idname in {'ArmLogicTreeType', 'ArmGroupTree'}:
                return bool(cls.filter_selected_nodes(path[-1].node_tree))
        return False

    def execute(self, context):
        """
        Add group tree from selected:
        01. Deselect group Input and Output nodes
        02. Copy nodes into clipboard
        03. Create group tree and move into one
        04. Past nodes from clipboard
        05. Move nodes into tree center
        06. Add group "input" and "output" outside of bounding box of the nodes
        07. TODO: Connect "input" and "output" sockets with group nodes
        08. Add Group tree node in center of selected node in initial tree
        09. TODO: Link the node with appropriate sockets
        10. Cleaning
        """
        base_tree = context.space_data.path[-1].node_tree
        sub_tree: ArmGroupTree = bpy.data.node_groups.new('Armory group', 'ArmGroupTree')

        # deselect group nodes if selected
        [setattr(n, 'select', False) for n in base_tree.nodes
        if n.select and n.bl_idname in {'LNGroupInputsNode', 'LNGroupOutputsNode'}]

        # Frames can't be just copied because they does not have absolute location, but they can be recreated
        frame_names = {n.name for n in base_tree.nodes if n.select and n.bl_idname == 'NodeFrame'}
        [setattr(n, 'select', False) for n in base_tree.nodes if n.bl_idname == 'NodeFrame']

        
        # copy and past nodes into group tree
        bpy.ops.node.clipboard_copy()
        context.space_data.path.append(sub_tree)
        bpy.ops.node.clipboard_paste()
        context.space_data.path.pop()  # will enter later via operator

        # move nodes in tree center
        sub_tree_nodes = self.filter_selected_nodes(sub_tree)
        center = reduce(lambda v1, v2: v1 + v2, [n.location for n in sub_tree_nodes]) / len(sub_tree_nodes)
        [setattr(n, 'location', n.location - center) for n in sub_tree_nodes]

        # recreate frames
        node_name_mapping = {n.name: n.name for n in sub_tree.nodes}  # all nodes have the same name as in base tree
        self.recreate_frames(base_tree, sub_tree, frame_names, node_name_mapping)

        # add group input and output nodes
        min_x = min(n.location[0] for n in sub_tree_nodes)
        max_x = max(n.location[0] for n in sub_tree_nodes)
        input_node = sub_tree.nodes.new('LNGroupInputsNode')
        input_node.location = (min_x - 250, 0)
        output_node = sub_tree.nodes.new('LNGroupOutputsNode')
        output_node.location = (max_x + 250, 0)
        # add group tree node
        initial_nodes = self.filter_selected_nodes(base_tree)
        center = reduce(lambda v1, v2: v1 + v2,
                        [Vector(ArmLogicTreeNode.absolute_location(n)) for n in initial_nodes]) / len(initial_nodes)
        group_node = base_tree.nodes.new('LNCallGroupNode')
        group_node.select = False
        group_node.group_tree = sub_tree
        group_node.location = center
        sub_tree.group_node_name = group_node.name

        # delete selected nodes and copied frames without children
        [base_tree.nodes.remove(n) for n in self.filter_selected_nodes(base_tree)]
        with_children_frames = {n.parent.name for n in base_tree.nodes if n.parent}
        [base_tree.nodes.remove(n) for n in base_tree.nodes
        if n.name in frame_names and n.name not in with_children_frames]

        # enter the group tree
        bpy.ops.arm.edit_group_tree(node_index=group_node.get_id_str())

        return {'FINISHED'}

    @staticmethod
    def filter_selected_nodes(tree) -> list:
        """Avoiding selecting nodes which should not be copied into sub tree"""
        return [n for n in tree.nodes if n.select and n.bl_idname not in {'LNGroupInputsNode', 'LNGroupOutputsNode'}]

    @staticmethod
    def recreate_frames(from_tree: bpy.types.NodeTree,
                        to_tree: bpy.types.NodeTree,
                        frame_names: Set[str],
                        from_to_node_names: Dict[str, str]):
        """
        Copy frames from one tree to another
        from_to_node_names - mapping of node names between two trees
        """
        new_frame_names = {n: to_tree.nodes.new('NodeFrame').name for n in frame_names}
        frame_attributes = ['label', 'use_custom_color', 'color', 'label_size', 'text']
        for frame_name in frame_names:
            old_frame = from_tree.nodes[frame_name]
            new_frame = to_tree.nodes[new_frame_names[frame_name]]
            for attr in frame_attributes:
                setattr(new_frame, attr, getattr(old_frame, attr))
        for from_node in from_tree.nodes:
            if from_node.name not in from_to_node_names:
                continue
            if from_node.parent and from_node.parent.name in new_frame_names:
                if from_node.bl_idname == 'NodeFrame':
                    to_node = to_tree.nodes[new_frame_names[from_node.name]]
                else:
                    to_node = to_tree.nodes[from_to_node_names[from_node.name]]
                to_node.parent = to_tree.nodes[new_frame_names[from_node.parent.name]]

class ArmUngroupGroupTree(bpy.types.Operator):
    """Put sub nodes into current layout and delete current group node"""
    bl_idname = 'arm.ungroup_group_tree'
    bl_label = "Ungroup group tree"

    @classmethod
    def poll(cls, context):
        if context.space_data.type == 'NODE_EDITOR':
            if context.active_node and hasattr(context.active_node, 'group_tree'):
                if context.active_node.group_tree is not None:
                    return True
        return False

    def execute(self, context):
        """Similar to AddGroupTreeFromSelected operator but in backward direction (from sub tree to tree)"""

        # go to sub tree, select all except input and output groups and mark nodes to be copied
        group_node = context.active_node
        sub_tree = group_node.group_tree
        bpy.ops.arm.edit_group_tree(node_index=group_node.get_id_str())
        [setattr(n, 'select', False) for n in sub_tree.nodes]
        group_nodes_filter = filter(lambda n: n.bl_idname not in {'LNGroupInputsNode', 'LNGroupOutputsNode'}, sub_tree.nodes)
        for node in group_nodes_filter:
            node.select = True
            node['sub_node_name'] = node.name  # this will be copied within the nodes

        # the attribute should be empty in destination tree
        tree = context.space_data.path[-2].node_tree
        for node in tree.nodes:
            if 'sub_node_name' in node:
                del node['sub_node_name']

        # Frames can't be just copied because they does not have absolute location, but they can be recreated
        frame_names = {n.name for n in sub_tree.nodes if n.select and n.bl_idname == 'NodeFrame'}
        [setattr(n, 'select', False) for n in sub_tree.nodes if n.bl_idname == 'NodeFrame']

        if any(n for n in sub_tree.nodes if n.select):  # if no selection copy operator will raise error
            # copy and past nodes into group tree
            bpy.ops.node.clipboard_copy()
            context.space_data.path.pop()
            bpy.ops.node.clipboard_paste()  # this will deselect all and select only pasted nodes

            # move nodes in group node center
            tree_select_nodes = [n for n in tree.nodes if n.select]
            center = reduce(lambda v1, v2: v1 + v2,
                            [Vector(ArmLogicTreeNode.absolute_location(n)) for n in tree_select_nodes]) / len(tree_select_nodes)
            [setattr(n, 'location', n.location - (center - group_node.location)) for n in tree_select_nodes]

            # recreate frames
            node_name_mapping = {n['sub_node_name']: n.name for n in tree.nodes if 'sub_node_name' in n}
            ArmAddGroupTreeFromSelected.recreate_frames(sub_tree, tree, frame_names, node_name_mapping)
        else:
            context.space_data.path.pop()  # should exit from sub tree anywhere

        # delete group node
        tree.nodes.remove(group_node)
        for node in tree.nodes:
            if 'sub_node_name' in node:
                del node['sub_node_name']

        tree.update()

        return {'FINISHED'}

class ArmAddCallGroupNode(bpy.types.Operator):
    """Create A Call Group Node"""
    bl_idname = 'arm.add_call_group_node'
    bl_label = "Add call group node"

    node_ref = None

    @classmethod
    def poll(cls, context):
        if context.space_data.type == 'NODE_EDITOR':
            return context.space_data.edit_tree and context.space_data.tree_type == 'ArmLogicTreeType'
        return False

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.execute(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.node_ref.location = context.space_data.cursor_location
        elif event.type == 'LEFTMOUSE':  # Confirm
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def execute(self, context):
        tree = context.space_data.path[-1].node_tree
        self.node_ref = tree.nodes.new('LNCallGroupNode')
        self.node_ref.location = context.space_data.cursor_location
        return {'FINISHED'}

class ARM_PT_LogicGroupPanel(bpy.types.Panel):
    bl_label = 'Armory Logic Group'
    bl_idname = 'ARM_PT_LogicGroupPanel'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType' and context.space_data.edit_tree

    def draw(self, context):
        layout = self.layout
        layout.operator('arm.add_call_group_node', icon='ADD')
        layout.operator('arm.add_group_tree_from_selected', icon='NODETREE')
        layout.operator('arm.ungroup_group_tree', icon='NODETREE')

REG_CLASSES = (
    ArmGroupTree,
    ArmEditGroupTree,
    ArmCopyGroupTree,
    ArmSearchGroupTree,
    ArmAddGroupTree,
    ArmAddGroupTreeFromSelected,
    ArmUngroupGroupTree,
    ArmAddCallGroupNode,
    ARM_PT_LogicGroupPanel
)
register, unregister = bpy.utils.register_classes_factory(REG_CLASSES)