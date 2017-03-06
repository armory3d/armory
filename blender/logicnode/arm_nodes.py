from nodeitems_utils import NodeItem

nodes = []
category_items = {}
category_items['Event'] = []
category_items['Value'] = []
category_items['Logic'] = []
category_items['Operator'] = []

class ArmLogicTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ArmLogicTreeType'

def add_node(node_class, category):
	global nodes
	nodes.append(node_class)
	category_items[category].append(NodeItem(node_class.bl_idname))
