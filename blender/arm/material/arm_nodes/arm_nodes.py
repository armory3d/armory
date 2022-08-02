from typing import Type

from bpy.types import Node
import nodeitems_utils

nodes = []
category_items = {}


def add_node(node_class: Type[Node], category: str):
    global nodes
    nodes.append(node_class)
    if category_items.get(category) is None:
        category_items[category] = []
    category_items[category].append(nodeitems_utils.NodeItem(node_class.bl_idname))
