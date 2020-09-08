import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

def update_node(self, context):
    #Clean all nodes

    while len(self.inputs) > 1:
        self.inputs.remove(self.inputs[-1])

    if (self.property0 == 'Uniform'):
        self.draw_nodes_uniform(context)
    elif (self.property0 == 'RGB'):
        self.draw_nodes_rgb(context)
    else:
        self.draw_nodes_colorwheel(context)

def set_data(self, context):

    abspath = bpy.path.abspath(self.filepath)
    abspath = abspath.replace("\\","\\\\")
    with open(abspath, 'r') as myfile:
        data = myfile.read().replace('\n', '').replace('"','')
        self.property1 = data

class ColorgradingSetShadowNode(ArmLogicTreeNode):
    '''Colorgrading Set Shadow node'''
    bl_idname = 'LNColorgradingSetShadowNode'
    bl_label = 'Colorgrading Set Shadow'
    bl_icon = 'NONE'

    # TODO: RRESET FILE OPTION FOR THE BELOW
    property0 : EnumProperty(
        items = [('RGB', 'RGB', 'RGB'),
                 ('Uniform', 'Uniform', 'Uniform')],
        name='Mode', default='Uniform', update=update_node)
    property1 : StringProperty(name="Loaded Data", description="Loaded data - Just ignore", default="")
    filepath : StringProperty(name="Preset File", description="Postprocess colorgrading preset file", default="", subtype="FILE_PATH", update=set_data)


    def draw_nodes_uniform(self, context):
        self.inputs.new('NodeSocketFloat', 'ShadowMax')
        self.inputs[-1].default_value = 1
        self.inputs.new('NodeSocketFloat', 'Saturation')
        self.inputs[-1].default_value = 1
        self.inputs.new('NodeSocketFloat', 'Contrast')
        self.inputs[-1].default_value = 1
        self.inputs.new('NodeSocketFloat', 'Gamma')
        self.inputs[-1].default_value = 1
        self.inputs.new('NodeSocketFloat', 'Gain')
        self.inputs[-1].default_value = 1
        self.inputs.new('NodeSocketFloat', 'Offset')
        self.inputs[-1].default_value = 1

    def draw_nodes_rgb(self, context):
        self.inputs.new('NodeSocketFloat', 'ShadowMax')
        self.inputs[-1].default_value = 1
        self.inputs.new('NodeSocketVector', 'Saturation')
        self.inputs[-1].default_value = [1,1,1]
        self.inputs.new('NodeSocketVector', 'Contrast')
        self.inputs[-1].default_value = [1,1,1]
        self.inputs.new('NodeSocketVector', 'Gamma')
        self.inputs[-1].default_value = [1,1,1]
        self.inputs.new('NodeSocketVector', 'Gain')
        self.inputs[-1].default_value = [1,1,1]
        self.inputs.new('NodeSocketVector', 'Offset')
        self.inputs[-1].default_value = [1,1,1]

    def draw_nodes_colorwheel(self, context):
        pass

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.draw_nodes_uniform(context)

    def draw_buttons(self, context, layout):
        layout.label(text="Select value mode")
        layout.prop(self, 'property0')
        if (self.property0 == 'Preset File'):
            layout.prop(self, 'filepath')
            layout.prop(self, 'property1')

add_node(ColorgradingSetShadowNode, category=MODULE_AS_CATEGORY, section='colorgrading')
