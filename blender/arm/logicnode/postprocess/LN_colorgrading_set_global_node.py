import bpy

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

class ColorgradingSetGlobalNode(ArmLogicTreeNode):
    """Colorgrading Set Global node"""
    bl_idname = 'LNColorgradingSetGlobalNode'
    bl_label = 'Colorgrading Set Global'

    # TODO: RRESET FILE OPTION FOR THE BELOW
    property0 : EnumProperty(
        items = [('RGB', 'RGB', 'RGB'),
                 ('Uniform', 'Uniform', 'Uniform')],
        name='Mode', default='Uniform', update=update_node)
    property1 : StringProperty(name="Loaded Data", description="Loaded data - Just ignore", default="")
    filepath : StringProperty(name="Preset File", description="Postprocess colorgrading preset file", default="", subtype="FILE_PATH", update=set_data)


    def draw_nodes_uniform(self, context):
        self.add_input('NodeSocketFloat', 'Whitebalance', default_value=6500.0)
        self.add_input('NodeSocketColor', 'Tint', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('NodeSocketFloat', 'Saturation', default_value=1)
        self.add_input('NodeSocketFloat', 'Contrast', default_value=1)
        self.add_input('NodeSocketFloat', 'Gamma', default_value=1)
        self.add_input('NodeSocketFloat', 'Gain', default_value=1)
        self.add_input('NodeSocketFloat', 'Offset', default_value=1)

    def draw_nodes_rgb(self, context):
        self.add_input('NodeSocketFloat', 'Whitebalance', default_value=6500.0)
        self.add_input('NodeSocketVector', 'Tint', default_value=[1,1,1])
        self.add_input('NodeSocketVector', 'Saturation', default_value=[1,1,1])
        self.add_input('NodeSocketVector', 'Contrast', default_value=[1,1,1])
        self.add_input('NodeSocketVector', 'Gamma', default_value=[1,1,1])
        self.add_input('NodeSocketVector', 'Gain', default_value=[1,1,1])
        self.add_input('NodeSocketVector', 'Offset', default_value=[1,1,1])

    def draw_nodes_colorwheel(self, context):
        pass

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.draw_nodes_uniform(context)

    def draw_buttons(self, context, layout):
        layout.label(text="Select value mode")
        layout.prop(self, 'property0')
        if (self.property0 == 'Preset File'):
            layout.prop(self, 'filepath')
            layout.prop(self, 'property1')

add_node(ColorgradingSetGlobalNode, category=MODULE_AS_CATEGORY, section='colorgrading')
