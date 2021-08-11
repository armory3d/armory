import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory

import arm
import arm.material.arm_nodes.arm_nodes as arm_nodes
# Import all nodes so that they register. Do not remove this import
# even if it looks unused
from arm.material.arm_nodes import *

if arm.is_reload(__name__):
    arm_nodes = arm.reload_module(arm_nodes)
    arm.material.arm_nodes = arm.reload_module(arm.material.arm_nodes)
    from arm.material.arm_nodes import *
else:
    arm.enable_reload(__name__)

registered_nodes = []


class MaterialNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'


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
        sorted_items = sorted(arm_nodes.category_items[category], key=lambda item: item.nodetype)
        node_categories.append(
            MaterialNodeCategory('ArmMaterial' + category + 'Nodes', category, items=sorted_items)
        )

    nodeitems_utils.register_node_categories('ArmMaterialNodes', node_categories)


def unregister_nodes():
    global registered_nodes
    for n in registered_nodes:
        bpy.utils.unregister_class(n)
    registered_nodes = []
    nodeitems_utils.unregister_node_categories('ArmMaterialNodes')


def register():
    register_nodes()


def unregister():
    unregister_nodes()
