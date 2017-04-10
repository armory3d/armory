import bpy.types
from bpy.props import *
from nodeitems_utils import NodeItem

nodes = []
category_items = {}
category_items['Logic'] = []
category_items['Event'] = []
category_items['Action'] = []
category_items['Value'] = []
category_items['Variable'] = []
category_items['Input'] = []
category_items['Animation'] = []
category_items['Physics'] = []
category_items['Navmesh'] = []
category_items['Sound'] = []
category_items['Native'] = []

object_sockets = dict()
array_nodes = dict()

class ArmLogicTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ArmLogicTreeType'

class ArmActionSocket(bpy.types.NodeSocket):
    bl_idname = 'ArmNodeSocketAction'
    bl_label = 'Action Socket'

    def draw(self, context, layout, node, text):
        layout.label(self.name)

    def draw_color(self, context, node):
        return (0.8, 0.3, 0.3, 1)

class ArmObjectSocket(bpy.types.NodeSocket):
    bl_idname = 'ArmNodeSocketObject'
    bl_label = 'Object Socket'
    default_value = StringProperty(name='Object', default='')

    def __init__(self):
        global object_sockets
        # Buckle up..
        # Match id strings to socket dict to retrieve socket in eyedropper operator
        object_sockets[str(id(self))] = self

    def draw(self, context, layout, node, text):
        if self.is_output:
            layout.label(self.name)
        else:
            row = layout.row(align = True)
            row.prop_search(self, 'default_value', bpy.context.scene, 'objects', icon='NONE', text='')
            op = row.operator('arm.node_eyedrop', text='', icon='EYEDROPPER', emboss=True)
            op.socket_index = str(id(self))

    def draw_color(self, context, node):
        return (0.15, 0.55, 0.75, 1)

class ArmNodeEyedropButton(bpy.types.Operator):
    '''Pick selected object'''
    bl_idname = 'arm.node_eyedrop'
    bl_label = 'Eyedrop'
    socket_index = StringProperty(name='Socket Index', default='')

    def execute(self, context):
        global object_sockets
        obj = bpy.context.active_object
        if obj != None:
            object_sockets[self.socket_index].default_value = obj.name
        return{'FINISHED'}

class ArmNodeAddInputButton(bpy.types.Operator):
    '''Add new input'''
    bl_idname = 'arm.node_add_input'
    bl_label = 'Add Input'
    node_index = StringProperty(name='Node Index', default='')
    socket_type = StringProperty(name='Socket Type', default='NodeSocketShader')

    def execute(self, context):
        global array_nodes
        array_nodes[self.node_index].inputs.new(self.socket_type, 'Input 1')
        return{'FINISHED'}

class ArmNodeRemoveInputButton(bpy.types.Operator):
    '''Remove last input'''
    bl_idname = 'arm.node_remove_input'
    bl_label = 'Remove Input'
    node_index = StringProperty(name='Node Index', default='')

    def execute(self, context):
        global array_nodes
        inps = array_nodes[self.node_index].inputs
        if len(inps) > 0:
            inps.remove(inps.values()[-1])
        return{'FINISHED'}

def add_node(node_class, category):
    global nodes
    nodes.append(node_class)
    category_items[category].append(NodeItem(node_class.bl_idname))

bpy.utils.register_class(ArmActionSocket)
bpy.utils.register_class(ArmObjectSocket)
bpy.utils.register_class(ArmNodeEyedropButton)
bpy.utils.register_class(ArmNodeAddInputButton)
bpy.utils.register_class(ArmNodeRemoveInputButton)
