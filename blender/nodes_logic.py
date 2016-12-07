import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *

class CGTree(NodeTree):
    '''Logic nodes'''
    bl_idname = 'ArmLogicTreeType'
    bl_label = 'Logic Node Tree'
    bl_icon = 'GAME'

class ArmLogicTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ArmLogicTreeType'

class TransformNode(Node, ArmLogicTreeNode):
    '''Transform node'''
    bl_idname = 'TransformNodeType'
    bl_label = 'Transform'
    bl_icon = 'SOUND'

    def init(self, context):
        self.inputs.new('NodeSocketVector', "Location")
        self.inputs.new('NodeSocketVector', "Rotation")
        self.inputs.new('NodeSocketVector', "Scale")
        self.inputs[-1].default_value = [1.0, 1.0, 1.0]

        self.outputs.new('NodeSocketString', "Transform")

class TimeNode(Node, ArmLogicTreeNode):
    '''Time node'''
    bl_idname = 'TimeNodeType'
    bl_label = 'Time'
    bl_icon = 'TIME'
    
    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Start")
        self.inputs.new('NodeSocketFloat', "Stop")
        self.inputs[-1].default_value = -1
        self.inputs.new('NodeSocketBool', "Enabled")
        self.inputs[-1].default_value = True
        self.inputs.new('NodeSocketBool', "Loop")
        self.inputs.new('NodeSocketBool', "Reflect")
        
        self.outputs.new('NodeSocketFloat', "Time")
        
class VectorNode(Node, ArmLogicTreeNode):
    '''Vector node'''
    bl_idname = 'VectorNodeType'
    # Label for nice name display
    bl_label = 'Vector'
    # Icon identifier
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketFloat', "X")
        self.inputs.new('NodeSocketFloat', "Y")
        self.inputs.new('NodeSocketFloat', "Z")
        
        self.outputs.new('NodeSocketVector', "Vector")

class ScaleValueNode(Node, ArmLogicTreeNode):
    '''Scale value node'''
    bl_idname = 'ScaleValueNodeType'
    bl_label = 'ScaleValue'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Factor")
        self.inputs[-1].default_value = 1.0
        self.inputs.new('NodeSocketFloat', "Value")
        
        self.outputs.new('NodeSocketFloat', "Value")

class SineNode(Node, ArmLogicTreeNode):
    '''Sine node'''
    bl_idname = 'SineNodeType'
    bl_label = 'Sine'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Value")
        
        self.outputs.new('NodeSocketFloat', "Value")

class ThisNode(Node, ArmLogicTreeNode):
    '''This node'''
    bl_idname = 'ThisNodeType'
    bl_label = 'This'
    bl_icon = 'GAME'
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "Target")

class PickerNode(Node, ArmLogicTreeNode):
    '''Picker node'''
    bl_idname = 'PickerNodeType'
    bl_label = 'Picker'
    bl_icon = 'GAME'
    property0 = StringProperty(name = "Object", default="")

    def init(self, context):
        self.outputs.new('NodeSocketShader', "Target")

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "property0", context.scene, "objects", text = "")

class SetTransformNode(Node, ArmLogicTreeNode):
    '''Set transform node'''
    bl_idname = 'SetTransformNodeType'
    bl_label = 'Set Transform'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "Trigger")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Transform")

class GoToNode(Node, ArmLogicTreeNode):
    '''Navigate to location'''
    bl_idname = 'GoToNodeType'
    bl_label = 'Go To'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "Trigger")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Transform")

class GetTransformNode(Node, ArmLogicTreeNode):
    '''Get transform node'''
    bl_idname = 'GetTransformNodeType'
    bl_label = 'Get Transform'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "Target")
        self.outputs.new('NodeSocketShader', "Transform")

class SetVisibleNode(Node, ArmLogicTreeNode):
    '''Set visible node'''
    bl_idname = 'SetVisibleNodeType'
    bl_label = 'Set Visible'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Bool")

class InputDownNode(Node, ArmLogicTreeNode):
    '''Input down node'''
    bl_idname = 'InputDownNodeType'
    bl_label = 'Input Down'
    bl_icon = 'GAME'

    def init(self, context):
        self.outputs.new('NodeSocketBool', "Bool")

class InputStartedNode(Node, ArmLogicTreeNode):
    '''Input started node'''
    bl_idname = 'InputStartedNodeType'
    bl_label = 'Input Started'
    bl_icon = 'GAME'

    def init(self, context):
        self.outputs.new('NodeSocketBool', "Bool")

class GreaterThanNode(Node, ArmLogicTreeNode):
    '''Greater than node'''
    bl_idname = 'GreaterThanNodeType'
    bl_label = 'Greater Than'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Value 1")
        self.inputs.new('NodeSocketFloat', "Value 2")
        self.outputs.new('NodeSocketBool', "Bool")

### Node Categories ###
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class ObjectNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType'

class ValueNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType'

class MathNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType'

class LogicNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType'

node_categories = [
    ObjectNodeCategory("LOGICTARGETNODES", "Target", items=[
        NodeItem("ThisNodeType"),
        NodeItem("PickerNodeType"),
    ]),
    ValueNodeCategory("LOGICVALUENODES", "Value", items=[
        NodeItem("TransformNodeType"),
        NodeItem("VectorNodeType"),
    ]),
    MathNodeCategory("LOGICMATHNODES", "Math", items=[
        NodeItem("ScaleValueNodeType"),
        NodeItem("SineNodeType"),
    ]),
    LogicNodeCategory("LOGICLOGICNODES", "Logic", items=[
        NodeItem("GreaterThanNodeType"),
    ]),
    LogicNodeCategory("LOGICOPERATORNODES", "Operator", items=[
        NodeItem("SetTransformNodeType"),
        NodeItem("GetTransformNodeType"),
        NodeItem("GoToNodeType"),
        NodeItem("SetVisibleNodeType"),
    ]),
    LogicNodeCategory("LOGICINPUTNODES", "Input", items=[
        NodeItem("TimeNodeType"),
        NodeItem("InputDownNodeType"),
        NodeItem("InputStartedNodeType"),
    ]),
]

def register():
    bpy.utils.register_module(__name__)
    try:
        nodeitems_utils.register_node_categories("ARM_LOGIC_NODES", node_categories)
    except:
        pass

def unregister():
    nodeitems_utils.unregister_node_categories("ARM_LOGIC_NODES")
    bpy.utils.unregister_module(__name__)
