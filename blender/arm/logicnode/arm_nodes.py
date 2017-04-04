from nodeitems_utils import NodeItem

nodes = []
category_items = {}
category_items['Event'] = []
category_items['Value'] = []
category_items['Variable'] = []
category_items['Logic'] = []
category_items['Operator'] = []
category_items['Native'] = []
category_items['Physics'] = []
category_items['Navmesh'] = []

class ArmLogicTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ArmLogicTreeType'

def add_node(node_class, category):
	global nodes
	nodes.append(node_class)
	category_items[category].append(NodeItem(node_class.bl_idname))
