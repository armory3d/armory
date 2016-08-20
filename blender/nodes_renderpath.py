import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import sys
import json
import platform
import subprocess
import nodes_compositor
from utils import to_hex
import assets
import utils

class CGPipelineTree(NodeTree):
    '''Render Path nodes'''
    bl_idname = 'CGPipelineTreeType'
    bl_label = 'Render Path Node Tree'
    bl_icon = 'SCENE'

class CGPipelineTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CGPipelineTreeType'

# Prebuilt
class QuadPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'QuadPassNodeType'
    bl_label = 'Quad Pass'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketString', "Shader Context")
        self.inputs.new('NodeSocketShader', "Bind 1")
        self.inputs.new('NodeSocketString', "Constant")
        self.inputs.new('NodeSocketShader', "Bind 2")
        self.inputs.new('NodeSocketString', "Constant")
        self.inputs.new('NodeSocketShader', "Bind 3")
        self.inputs.new('NodeSocketString', "Constant")

        self.outputs.new('NodeSocketShader', "Stage")

class SSAOPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'SSAOPassNodeType'
    bl_label = 'SSAO'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "A")
        self.inputs.new('NodeSocketShader', "GBufferD")
        self.inputs.new('NodeSocketShader', "GBuffer0")

        self.outputs.new('NodeSocketShader', "Stage")

class SSAOReprojectPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'SSAOReprojectPassNodeType'
    bl_label = 'SSAO Reproject'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Last")
        self.inputs.new('NodeSocketShader', "Depth")
        self.inputs.new('NodeSocketShader', "Normals")
        self.inputs.new('NodeSocketShader', "Velocity")

        self.outputs.new('NodeSocketShader', "Stage")

class ApplySSAOPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'ApplySSAOPassNodeType'
    bl_label = 'Apply SSAO'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "A")
        self.inputs.new('NodeSocketShader', "B")
        self.inputs.new('NodeSocketShader', "GBufferD")
        self.inputs.new('NodeSocketShader', "GBuffer0")

        self.outputs.new('NodeSocketShader', "Stage")

class SSRPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'SSRPassNodeType'
    bl_label = 'SSR'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "A")
        self.inputs.new('NodeSocketShader', "B")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "GBufferD")
        self.inputs.new('NodeSocketShader', "GBuffer0")

        self.outputs.new('NodeSocketShader', "Stage")

class BloomPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'BloomPassNodeType'
    bl_label = 'Bloom'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "A")
        self.inputs.new('NodeSocketShader', "B")
        self.inputs.new('NodeSocketShader', "Color")

        self.outputs.new('NodeSocketShader', "Stage")

class MotionBlurPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'MotionBlurPassNodeType'
    bl_label = 'Motion Blur'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "GBufferD")
        self.inputs.new('NodeSocketShader', "GBuffer0")

        self.outputs.new('NodeSocketShader', "Stage")

class MotionBlurVelocityPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'MotionBlurVelocityPassNodeType'
    bl_label = 'Motion Blur Velocity'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "GBuffer0")
        self.inputs.new('NodeSocketShader', "Velocity")

        self.outputs.new('NodeSocketShader', "Stage")

class CopyPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'CopyPassNodeType'
    bl_label = 'Copy'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")

        self.outputs.new('NodeSocketShader', "Stage")

class BlendPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'BlendPassNodeType'
    bl_label = 'Blend'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")

        self.outputs.new('NodeSocketShader', "Stage")

class CombinePassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'CombinePassNodeType'
    bl_label = 'Combine'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "A")
        self.inputs.new('NodeSocketShader', "B")

        self.outputs.new('NodeSocketShader', "Stage")

class BlurBasicPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'BlurBasicPassNodeType'
    bl_label = 'Blur Basic'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "In/Out")
        self.inputs.new('NodeSocketShader', "Temp")

        self.outputs.new('NodeSocketShader', "Stage")

class DebugNormalsPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DebugNormalsPassNodeType'
    bl_label = 'Debug Normals'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")

        self.outputs.new('NodeSocketShader', "Stage")

class FXAAPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'FXAAPassNodeType'
    bl_label = 'FXAA'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")

        self.outputs.new('NodeSocketShader', "Stage")

class SMAAPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'SMAAPassNodeType'
    bl_label = 'SMAA'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Edges Target")
        self.inputs.new('NodeSocketShader', "Blend Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "Velocity")

        self.outputs.new('NodeSocketShader', "Stage")

class TAAPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'TAAPassNodeType'
    bl_label = 'TAA'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "Last Color")
        self.inputs.new('NodeSocketShader', "Velocity")

        self.outputs.new('NodeSocketShader', "Stage")

class SSSPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'SSSPassNodeType'
    bl_label = 'SSS'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target In")
        self.inputs.new('NodeSocketShader', "Target Out")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "GBufferD")
        self.inputs.new('NodeSocketShader', "GBuffer0")

        self.outputs.new('NodeSocketShader', "Stage")

class WaterPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'WaterPassNodeType'
    bl_label = 'Water'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "GBufferD")

        self.outputs.new('NodeSocketShader', "Stage")

class DeferredLightPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DeferredLightPassNodeType'
    bl_label = 'Deferred Light'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "GBuffer")
        self.inputs.new('NodeSocketShader', "Shadow Map")

        self.outputs.new('NodeSocketShader', "Stage")

class DeferredIndirectPassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DeferredIndirectPassNodeType'
    bl_label = 'Deferred Indirect'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "GBuffer")
        self.inputs.new('NodeSocketShader', "SSAO")

        self.outputs.new('NodeSocketShader', "Stage")

class TranslucentResolvePassNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'TranslucentResolvePassNodeType'
    bl_label = 'Translucent Resolve'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Translucent GBuffer")

        self.outputs.new('NodeSocketShader', "Stage")

# Pipeline
class DrawGeometryNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DrawGeometryNodeType'
    bl_label = 'Draw Geometry'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Context")
        self.inputs.new('NodeSocketString', "Order")
        self.inputs[2].default_value = 'front_to_back'

        self.outputs.new('NodeSocketShader', "Stage")
        
class DrawDecalsNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DrawDecalsNodeType'
    bl_label = 'Draw Decals'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Context")

        self.outputs.new('NodeSocketShader', "Stage")
        
class ClearTargetNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'ClearTargetNodeType'
    bl_label = 'Clear Target'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketBool', "Color")
        self.inputs.new('NodeSocketColor', "Value")
        self.inputs.new('NodeSocketBool', "Depth")
        self.inputs.new('NodeSocketFloat', "Value")
        self.inputs[4].default_value = 1.0
        self.inputs.new('NodeSocketBool', "Stencil")
        self.inputs.new('NodeSocketInt', "Value")

        self.outputs.new('NodeSocketShader', "Stage")

class BeginNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'BeginNodeType'
    bl_label = 'Begin'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "ID")
        self.inputs.new('NodeSocketString', "Geometry")
        self.inputs.new('NodeSocketString', "Shadows")
        self.inputs.new('NodeSocketString', "Translucent")
        self.inputs.new('NodeSocketString', "Overlay")
        self.inputs.new('NodeSocketBool', "HDR Space")
        self.inputs[5].default_value = True
        self.outputs.new('NodeSocketShader', "Stage")
    
class SetTargetNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'SetTargetNodeType'
    bl_label = 'Set Target'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")

        self.outputs.new('NodeSocketShader', "Stage")
        
class TargetNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'TargetNodeType'
    bl_label = 'Target'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "ID")
        self.inputs.new('NodeSocketInt', "Width")
        self.inputs.new('NodeSocketInt', "Height")
        self.inputs.new('NodeSocketShader', "Depth Buffer")
        self.inputs.new('NodeSocketString', "Format")
        self.inputs.new('NodeSocketBool', "Ping Pong")

        self.outputs.new('NodeSocketShader', "Target")

class TargetArrayNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'TargetArrayNodeType'
    bl_label = 'Target Array'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketInt', "Instances")

        self.outputs.new('NodeSocketShader', "Targets")

class DepthBufferNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DepthBufferNodeType'
    bl_label = 'Depth Buffer'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "ID")
        self.inputs.new('NodeSocketBool', "Stencil")
        
        self.outputs.new('NodeSocketShader', "Target")

class GBufferNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'GBufferNodeType'
    bl_label = 'GBuffer'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Target 0")
        self.inputs.new('NodeSocketShader', "Target 1")
        self.inputs.new('NodeSocketShader', "Target 2")
        self.inputs.new('NodeSocketShader', "Target 3")
        self.inputs.new('NodeSocketShader', "Target 4")

        self.outputs.new('NodeSocketShader', "Targets")
    
class FramebufferNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'FramebufferNodeType'
    bl_label = 'Framebuffer'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "Target")

class BindTargetNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'BindTargetNodeType'
    bl_label = 'Bind Target'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketString', "Constant")

        self.outputs.new('NodeSocketShader', "Stage")

class DrawMaterialQuadNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DrawMaterialQuadNodeType'
    bl_label = 'Draw Material Quad'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Material Context")

        self.outputs.new('NodeSocketShader', "Stage")
        
class DrawQuadNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DrawQuadNodeType'
    bl_label = 'Draw Quad'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Shader Context")

        self.outputs.new('NodeSocketShader', "Stage")

class CallFunctionNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'CallFunctionNodeType'
    bl_label = 'Call Function'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Function")

        self.outputs.new('NodeSocketShader', "Stage")
    
class BranchFunctionNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'BranchFunctionNodeType'
    bl_label = 'Branch Function'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketString', "Function")

        self.outputs.new('NodeSocketShader', "True")
        self.outputs.new('NodeSocketShader', "False")
        
class MergeStagesNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'MergeStagesNodeType'
    bl_label = 'Merge Stages'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Stage")

        self.outputs.new('NodeSocketShader', "Stage")

class LoopStagesNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'LoopStagesNodeType'
    bl_label = 'Loop Stages'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketInt', "From")
        self.inputs.new('NodeSocketInt', "To")

        self.outputs.new('NodeSocketShader', "Complete")
        self.outputs.new('NodeSocketShader', "Loop")
        
class LoopLightsNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'LoopLightsNodeType'
    bl_label = 'Loop Lights'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")

        self.outputs.new('NodeSocketShader', "Complete")
        self.outputs.new('NodeSocketShader', "Loop")

class DrawStereoNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DrawStereoNodeType'
    bl_label = 'Draw Stereo'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")

        self.outputs.new('NodeSocketShader', "Complete")
        self.outputs.new('NodeSocketShader', "Per Eye")

class DrawWorldNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DrawWorldNodeType'
    bl_label = 'Draw World'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        # self.inputs.new('NodeSocketShader', "Depth")

        self.outputs.new('NodeSocketShader', "Stage")

class DrawCompositorNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DrawCompositorNodeType'
    bl_label = 'Draw Compositor'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "Depth")
        self.inputs.new('NodeSocketShader', "Normals")

        self.outputs.new('NodeSocketShader', "Stage")

class DrawCompositorWithFXAANode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'DrawCompositorWithFXAANodeType'
    bl_label = 'Draw Compositor + FXAA'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Stage")
        self.inputs.new('NodeSocketShader', "Target")
        self.inputs.new('NodeSocketShader', "Color")
        self.inputs.new('NodeSocketShader', "Depth")
        self.inputs.new('NodeSocketShader', "Normals")

        self.outputs.new('NodeSocketShader', "Stage")

# Constant nodes
class ScreenNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'ScreenNodeType'
    bl_label = 'Screen'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.outputs.new('NodeSocketInt', "Width")
        self.outputs.new('NodeSocketInt', "Height")
        self.inputs.new('NodeSocketFloat', "Scale")
        self.inputs[0].default_value = 1.0

class BackgroundColorNode(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'BackgroundColorNodeType'
    bl_label = 'Background Color'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.outputs.new('NodeSocketInt', "Color")
   
class LightCount(Node, CGPipelineTreeNode):
    '''A custom node'''
    bl_idname = 'LightCountNodeType'
    bl_label = 'Light Count'
    bl_icon = 'SOUND'
    
    def init(self, context):
        self.outputs.new('NodeSocketInt', "Count")

### Node Categories ###
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class MyCommandNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CGPipelineTreeType'

class MyTargetNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CGPipelineTreeType'

class MyPassNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CGPipelineTreeType'
        
class MyConstantNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CGPipelineTreeType'

class MyLogicNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CGPipelineTreeType'

node_categories = [
    MyCommandNodeCategory("COMMANDNODES", "Command", items=[
        NodeItem("BeginNodeType"),
        NodeItem("DrawGeometryNodeType"),
        NodeItem("DrawDecalsNodeType"),
        NodeItem("ClearTargetNodeType"),
        NodeItem("SetTargetNodeType"),
        NodeItem("BindTargetNodeType"),
        NodeItem("DrawMaterialQuadNodeType"),
        NodeItem("DrawQuadNodeType"),
        NodeItem("DrawWorldNodeType"),
        NodeItem("DrawCompositorNodeType"),
        NodeItem("DrawCompositorWithFXAANodeType"),
    ]),
    MyTargetNodeCategory("TARGETNODES", "Target", items=[
        NodeItem("TargetNodeType"),
        NodeItem("TargetArrayNodeType"),
        NodeItem("DepthBufferNodeType"),
        NodeItem("GBufferNodeType"),
        NodeItem("FramebufferNodeType"),
    ]),
    MyPassNodeCategory("PREBUILTNODES", "Prebuilt", items=[
        NodeItem("QuadPassNodeType"),
        NodeItem("SSAOPassNodeType"),
        NodeItem("SSAOReprojectPassNodeType"),
        NodeItem("ApplySSAOPassNodeType"),
        NodeItem("SSRPassNodeType"),
        NodeItem("BloomPassNodeType"),
        NodeItem("MotionBlurPassNodeType"),
        NodeItem("MotionBlurVelocityPassNodeType"),
        NodeItem("CopyPassNodeType"),
        NodeItem("BlendPassNodeType"),
        NodeItem("CombinePassNodeType"),
        NodeItem("BlurBasicPassNodeType"),
        NodeItem("DebugNormalsPassNodeType"),
        NodeItem("FXAAPassNodeType"),
        NodeItem("SMAAPassNodeType"),
        NodeItem("TAAPassNodeType"),
        NodeItem("SSSPassNodeType"),
        NodeItem("WaterPassNodeType"),
        NodeItem("DeferredLightPassNodeType"),
        NodeItem("DeferredIndirectPassNodeType"),
        NodeItem("TranslucentResolvePassNodeType"),
    ]),
    MyConstantNodeCategory("CONSTANTNODES", "Constant", items=[
        NodeItem("ScreenNodeType"),
        NodeItem("BackgroundColorNodeType"),
        NodeItem("LightCountNodeType"),
    ]),
    MyLogicNodeCategory("LOGICNODES", "Logic", items=[
        NodeItem("CallFunctionNodeType"),
        NodeItem("BranchFunctionNodeType"),
        NodeItem("MergeStagesNodeType"),
        NodeItem("LoopStagesNodeType"),
        NodeItem("LoopLightsNodeType"),
        NodeItem("DrawStereoNodeType"),
    ]),
]

# Handling node data
def reload_blend_data():
    if bpy.data.node_groups.get('forward_path') == None:
        load_library()
        pass

def load_library():
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons['armory'].preferences
    sdk_path = addon_prefs.sdk_path
    data_path = sdk_path + '/armory/blender/data/data.blend'

    with bpy.data.libraries.load(data_path, link=False) as (data_from, data_to):
        data_to.node_groups = ['forward_path', 'forward_path_low', 'deferred_path', 'deferred_path_low', 'deferred_path_high', 'hybrid_path', 'vr_path', 'pathtrace_path', 'Armory PBR']
    
    # TODO: cannot use for loop
    # TODO: import pbr group separately, no need for fake user
    bpy.data.node_groups['forward_path'].use_fake_user = True
    bpy.data.node_groups['forward_path_low'].use_fake_user = True
    bpy.data.node_groups['deferred_path'].use_fake_user = True
    bpy.data.node_groups['deferred_path_low'].use_fake_user = True
    bpy.data.node_groups['deferred_path_high'].use_fake_user = True
    bpy.data.node_groups['hybrid_path'].use_fake_user = True
    bpy.data.node_groups['vr_path'].use_fake_user = True
    bpy.data.node_groups['pathtrace_path'].use_fake_user = True
    bpy.data.node_groups['Armory PBR'].use_fake_user = True

def register():
    bpy.utils.register_module(__name__)
    try:
        nodeitems_utils.register_node_categories("CG_PIPELINE_NODES", node_categories)
        reload_blend_data()
    except:
        pass

def unregister():
    nodeitems_utils.unregister_node_categories("CG_PIPELINE_NODES")
    bpy.utils.unregister_module(__name__)

def buildNodeTrees(shader_references, asset_references, assets_path):
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    fp = os.path.sep.join(s)
    os.chdir(fp)

    # Make sure Assets dir exists
    if not os.path.exists('compiled/Assets/pipelines'):
        os.makedirs('compiled/Assets/pipelines')
    
    buildNodeTrees.assets_path = assets_path
    buildNodeTrees.linked_assets = []
    # Always include
    buildNodeTrees.linked_assets.append(buildNodeTrees.assets_path + 'brdf.png')

    # Export selected pipeline
    node_group = bpy.data.node_groups[bpy.data.cameras[0].pipeline_path]
    buildNodeTree(node_group, shader_references, asset_references)

    return buildNodeTrees.linked_assets

def buildNodeTree(node_group, shader_references, asset_references):
    output = {}
    res = {}
    output['pipeline_resources'] = [res]
    
    path = 'compiled/Assets/pipelines/'
    node_group_name = node_group.name.replace('.', '_')
    
    rn = get_root_node(node_group)
    if rn == None:
        return

    res['id'] = node_group_name

    # Store main context names
    res['geometry_context'] = bpy.data.cameras[0].geometry_context
    res['shadows_context'] = bpy.data.cameras[0].shadows_context
    
    res['render_targets'], res['depth_buffers'] = preprocess_pipeline(rn, node_group)
    res['stages'] = []
    
    buildNode(res['stages'], rn, node_group, shader_references, asset_references)

    asset_path = path + node_group_name + '.arm'
    utils.write_arm(asset_path, output)
    assets.add(asset_path)

def make_set_target(stage, node_group, node, currentNode=None, target_index=1, viewport_scale=1.0):
    if currentNode == None:
        currentNode = node
    
    stage['command'] = 'set_target'

    # First param is viewport scale
    if len(stage['params']) == 0:
        stage['params'].append(viewport_scale)

    currentNode = findNodeByLink(node_group, currentNode, currentNode.inputs[target_index])
    
    if currentNode.bl_idname == 'TargetNodeType':
        targetId = currentNode.inputs[0].default_value
        stage['params'].append(targetId)
        # Store current target size
        buildNode.last_set_target_w = currentNode.inputs[1].default_value
        buildNode.last_set_target_h = currentNode.inputs[2].default_value
    
    elif currentNode.bl_idname == 'GBufferNodeType':
        # Set all linked targets
        for i in range(0, 5):
            if currentNode.inputs[i].is_linked:
                make_set_target(stage, node_group, node, currentNode, target_index=i)
    
    elif currentNode.bl_idname == 'NodeReroute':
        make_set_target(stage, node_group, node, currentNode, target_index=0)
    
    else: # Framebuffer
        targetId = ''
        stage['params'].append(targetId)

def make_clear_target(stage, color_val=None, depth_val=None, stencil_val=None):
    stage['command'] = 'clear_target'
    if color_val != None:
        stage['params'].append('color')
        stage['params'].append(str(to_hex(color_val)))
    if depth_val != None:
        stage['params'].append('depth')
        stage['params'].append(str(depth_val))
    if stencil_val != None:
        stage['params'].append('stencil')
        stage['params'].append(str(stencil_val))

def make_draw_geometry(stage, node_group, node):
    stage['command'] = 'draw_geometry'
    # Context
    context = node.inputs[1].default_value
    # Store shadowmap size
    if context == bpy.data.cameras[0].shadows_context:
        bpy.data.worlds[0].shadowmap_size = buildNode.last_set_target_w
    stage['params'].append(context)
    # Order
    order = node.inputs[2].default_value
    stage['params'].append(order)
    
def make_draw_decals(stage, node_group, node, shader_references, asset_references):
    stage['command'] = 'draw_decals'
    context = node.inputs[1].default_value
    stage['params'].append(context) # Context
    bpy.data.cameras[0].last_decal_context = context

def make_bind_target(stage, node_group, node, constant_name, currentNode=None, target_index=1):
    if currentNode == None:
        currentNode = node
        
    stage['command'] = 'bind_target'
    
    link = findLink(node_group, currentNode, currentNode.inputs[target_index])
    currentNode = link.from_node
    
    if currentNode.bl_idname == 'NodeReroute':
        make_bind_target(stage, node_group, node, constant_name, currentNode=currentNode, target_index=0)
    
    elif currentNode.bl_idname == 'GBufferNodeType':
        for i in range(0, 5):
            if currentNode.inputs[i].is_linked:
                targetNode = findNodeByLink(node_group, currentNode, currentNode.inputs[i])
                targetId = targetNode.inputs[0].default_value
                # if i == 0 and targetNode.inputs[3].default_value == True: # Depth
                if targetNode.inputs[3].is_linked: # Depth
                    db_node = findNodeByLink(node_group, targetNode, targetNode.inputs[3])
                    db_id = db_node.inputs[0].default_value
                    stage['params'].append('_' + db_id)
                    stage['params'].append(constant_name + 'D')
                stage['params'].append(targetId) # Color buffer
                stage['params'].append(constant_name + str(i))
    
    elif currentNode.bl_idname == 'TargetNodeType':     
        targetId = currentNode.inputs[0].default_value
        stage['params'].append(targetId)
        stage['params'].append(constant_name)
        
    elif currentNode.bl_idname == 'DepthBufferNodeType':
        targetId = '_' + currentNode.inputs[0].default_value
        stage['params'].append(targetId)
        stage['params'].append(constant_name)

def make_draw_material_quad(stage, node_group, node, shader_references, asset_references, context_index=1):
    stage['command'] = 'draw_material_quad'
    material_context = node.inputs[context_index].default_value
    stage['params'].append(material_context)
    # Include resource and shaders
    shader_context = node.inputs[context_index].default_value
    scon = shader_context.split('/')
    dir_name = scon[2]
    # No world defs for material passes
    res_name = scon[2]
    asset_references.append('compiled/ShaderResources/' + dir_name + '/' + res_name + '.arm')
    shader_references.append('compiled/Shaders/' + dir_name + '/' + res_name)

def make_draw_quad(stage, node_group, node, shader_references, asset_references, context_index=1, shader_context=None):
    stage['command'] = 'draw_shader_quad'
    # Append world defs to get proper context
    world_defs = bpy.data.worlds[0].world_defs
    if shader_context == None:
        shader_context = node.inputs[context_index].default_value
    scon = shader_context.split('/')
    stage['params'].append(scon[0] + world_defs + '/' + scon[1] + world_defs + '/' + scon[2])
    # Include resource and shaders
    dir_name = scon[0]
    # Append world defs
    res_name = scon[1] + world_defs
    asset_references.append('compiled/ShaderResources/' + dir_name + '/' + res_name + '.arm')
    shader_references.append('compiled/Shaders/' + dir_name + '/' + res_name)

def make_draw_world(stage, node_group, node, shader_references, asset_references, dome=True):
    if dome:
        stage['command'] = 'draw_skydome'
    else:
        stage['command'] = 'draw_material_quad'
    wname = bpy.data.worlds[0].name
    stage['params'].append(wname + '_material/' + wname + '_material/env_map') # Only one world for now
    # Link assets
    if '_EnvClouds' in bpy.data.worlds[0].world_defs:
        buildNodeTrees.linked_assets.append(buildNodeTrees.assets_path + 'noise256.png')

def make_draw_compositor(stage, node_group, node, shader_references, asset_references, with_fxaa=False):
    scon = 'compositor_pass'
    wrd = bpy.data.worlds[0]
    world_defs = wrd.world_defs
    compositor_defs = nodes_compositor.parse_defs(bpy.data.scenes[0].node_tree) # Thrown in scene 0 for now
    # Additional compositor flags
    compo_depth = False # Read depth
    compo_pos = False # Construct position from depth
    if with_fxaa: # FXAA directly in compositor, useful for forward path
        compositor_defs += '_CompoFXAA'
    if wrd.generate_letterbox:
        compositor_defs += '_CompoLetterbox'
    if wrd.generate_grain:
        compositor_defs += '_CompoGrain'
    if bpy.data.scenes[0].cycles.film_exposure != 1.0:
        compositor_defs += '_CompoExposure'
    if wrd.generate_fog:
        compositor_defs += '_CompoFog'
        compo_pos = True
    if bpy.data.cameras[0].cycles.aperture_size > 0.0:
        compositor_defs += '_CompoDOF'
        compo_depth = True
    if compo_pos:
        compositor_defs += '_CompoPos'
        compo_depth = True
    if compo_depth:
        compositor_defs += '_CompoDepth'

    defs = world_defs + compositor_defs
    res_name = scon + defs
    
    stage['command'] = 'draw_shader_quad'
    stage['params'].append(res_name + '/' + res_name + '/' + scon)
    # Include resource and shaders
    asset_references.append('compiled/ShaderResources/' + scon + '/' + res_name + '.arm')
    shader_references.append('compiled/Shaders/' + scon + '/' + res_name)
    # Link assets
    buildNodeTrees.linked_assets.append(buildNodeTrees.assets_path + 'noise256.png')

def make_call_function(stage, node_group, node):
    stage['command'] = 'call_function'
    stage['params'].append(node.inputs[1].default_value)

def make_branch_function(stage, node_group, node):
    make_call_function(stage, node_group, node)
    
def process_call_function(stage, stages, node, node_group, shader_references, asset_references):
    # Step till merge node
    stage['returns_true'] = []
    if node.outputs[0].is_linked:
        stageNode = findNodeByLinkFrom(node_group, node, node.outputs[0])
        buildNode(stage['returns_true'], stageNode, node_group, shader_references, asset_references)
    
    stage['returns_false'] = []
    if node.outputs[1].is_linked:
        stageNode = findNodeByLinkFrom(node_group, node, node.outputs[1])
        margeNode = buildNode(stage['returns_false'], stageNode, node_group, shader_references, asset_references)
    
    # Continue using top level stages after merge node
    afterMergeNode = findNodeByLinkFrom(node_group, margeNode, margeNode.outputs[0])
    buildNode(stages, afterMergeNode, node_group, shader_references, asset_references)

def make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[3, 5, 7], bind_target_constants=None, shader_context=None, viewport_scale=1.0, with_clear=False):
    # Set target
    if target_index != None and node.inputs[target_index].is_linked:
        stage = {}
        stage['params'] = []
        make_set_target(stage, node_group, node, target_index=target_index, viewport_scale=viewport_scale)
        stages.append(stage)
    # Optinal clear
    if with_clear:
        stage = {}
        stage['params'] = []
        make_clear_target(stage, color_val=[0.0, 0.0, 0.0, 1.0])
        stages.append(stage)
    # Bind targets
    stage = {}
    stage['params'] = []
    buildNode.last_bind_target = stage
    bind_target_used = False
    for i in range(0, len(bind_target_indices)):
        index = bind_target_indices[i]
        if node.inputs[index].is_linked:
            bind_target_used = True
            if bind_target_constants == None:
                constant_name = node.inputs[index + 1].default_value
            else:
                constant_name = bind_target_constants[i]
            make_bind_target(stage, node_group, node, constant_name, target_index=index)   
    if bind_target_used:
        stages.append(stage)
        stage = {}
        stage['params'] = []
    # Draw quad
    make_draw_quad(stage, node_group, node, shader_references, asset_references, context_index=2, shader_context=shader_context)
    stages.append(stage)

def make_ssao_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[3, 4], bind_target_constants=['gbufferD', 'gbuffer0'], shader_context='ssao_pass/ssao_pass/ssao_pass', viewport_scale=bpy.data.worlds[0].generate_ssao_texture_scale)
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=2, bind_target_indices=[1, 4], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_x', viewport_scale=bpy.data.worlds[0].generate_ssao_texture_scale)
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2, 4], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_y')
    buildNodeTrees.linked_assets.append(buildNodeTrees.assets_path + 'noise8.png')

def make_ssao_reproject_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[3, 4, 2, 5], bind_target_constants=['gbufferD', 'gbuffer0', 'slast', 'sveloc'], shader_context='ssao_reproject_pass/ssao_reproject_pass/ssao_reproject_pass')
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=2, bind_target_indices=[1, 4], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_x')
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2, 4], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_y')
    buildNodeTrees.linked_assets.append(buildNodeTrees.assets_path + 'noise8.png')

def make_apply_ssao_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=2, bind_target_indices=[4, 5], bind_target_constants=['gbufferD', 'gbuffer0'], shader_context='ssao_pass/ssao_pass/ssao_pass')
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=3, bind_target_indices=[2, 5], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_x')
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[3, 5], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_edge_pass/blur_edge_pass/blur_edge_pass_y_blend')
    buildNodeTrees.linked_assets.append(buildNodeTrees.assets_path + 'noise8.png')

def make_ssr_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=2, bind_target_indices=[4, 5, 6], bind_target_constants=['tex', 'gbufferD', 'gbuffer0'], shader_context='ssr_pass/ssr_pass/ssr_pass', viewport_scale=bpy.data.worlds[0].generate_ssr_texture_scale)
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=3, bind_target_indices=[2, 6], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_adaptive_pass/blur_adaptive_pass/blur_adaptive_pass_x', viewport_scale=bpy.data.worlds[0].generate_ssr_texture_scale, with_clear=True) # Have to clear to prevent artefacts, potentially because of viewport scale
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[3, 6], bind_target_constants=['tex', 'gbuffer0'], shader_context='blur_adaptive_pass/blur_adaptive_pass/blur_adaptive_pass_y3_blend')

def make_bloom_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=2, bind_target_indices=[4], bind_target_constants=['tex'], shader_context='bloom_pass/bloom_pass/bloom_pass')
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=3, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='blur_gaus_pass/blur_gaus_pass/blur_gaus_pass_x')
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[3], bind_target_constants=['tex'], shader_context='blur_gaus_pass/blur_gaus_pass/blur_gaus_pass_y_blend')

def make_motion_blur_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2, 3, 4], bind_target_constants=['tex', 'gbufferD', 'gbuffer0'], shader_context='motion_blur_pass/motion_blur_pass/motion_blur_pass')

def make_motion_blur_velocity_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2, 3, 4], bind_target_constants=['tex', 'gbuffer0', 'sveloc'], shader_context='motion_blur_veloc_pass/motion_blur_veloc_pass/motion_blur_veloc_pass')

def make_copy_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='copy_pass/copy_pass/copy_pass')

def make_blend_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='blend_pass/blend_pass/blend_pass')

def make_combine_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2, 3], bind_target_constants=['tex', 'tex2'], shader_context='combine_pass/combine_pass/combine_pass')

def make_blur_basic_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=2, bind_target_indices=[1], bind_target_constants=['tex'], shader_context='blur_pass/blur_pass/blur_pass_x')
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='blur_pass/blur_pass/blur_pass_y')

def make_debug_normals_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='debug_normals_pass/debug_normals_pass/debug_normals_pass')

def make_fxaa_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2], bind_target_constants=['tex'], shader_context='fxaa_pass/fxaa_pass/fxaa_pass')

def make_smaa_pass(stages, node_group, node, shader_references, asset_references):
    stage = {}
    stage['params'] = []
    make_set_target(stage, node_group, node, target_index=2)
    stages.append(stage)
    
    stage = {}
    stage['params'] = []
    make_clear_target(stage, color_val=[0.0, 0.0, 0.0, 0.0])
    stages.append(stage)
    
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=None, bind_target_indices=[4], bind_target_constants=['colorTex'], shader_context='smaa_edge_detect/smaa_edge_detect/smaa_edge_detect')
    
    stage = {}
    stage['params'] = []
    make_set_target(stage, node_group, node, target_index=3)
    stages.append(stage)

    stage = {}
    stage['params'] = []
    make_clear_target(stage, color_val=[0.0, 0.0, 0.0, 0.0])
    stages.append(stage)
    
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=None, bind_target_indices=[2], bind_target_constants=['edgesTex'], shader_context='smaa_blend_weight/smaa_blend_weight/smaa_blend_weight')
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[4, 3, 5], bind_target_constants=['colorTex', 'blendTex', 'sveloc'], shader_context='smaa_neighborhood_blend/smaa_neighborhood_blend/smaa_neighborhood_blend')
    buildNodeTrees.linked_assets.append(buildNodeTrees.assets_path + 'smaa_area.png')
    buildNodeTrees.linked_assets.append(buildNodeTrees.assets_path + 'smaa_search.png')

def make_taa_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2, 3, 4], bind_target_constants=['tex', 'tex2', 'sveloc'], shader_context='taa_pass/taa_pass/taa_pass')

def make_sss_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[3, 4, 5], bind_target_constants=['tex', 'gbufferD', 'gbuffer0'], shader_context='sss_pass/sss_pass/sss_pass_x')
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=2, bind_target_indices=[3, 4, 5], bind_target_constants=['tex', 'gbufferD', 'gbuffer0'], shader_context='sss_pass/sss_pass/sss_pass_y')

def make_water_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2, 3], bind_target_constants=['tex', 'gbufferD'], shader_context='water_pass/water_pass/water_pass')

def make_deferred_light_pass(stages, node_group, node, shader_references, asset_references):
    # make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2, 3], bind_target_constants=['gbuffer', 'shadowMap'], shader_context='deferred_light/deferred_light/deferred_light')
    # Draw light volume - TODO: properly generate stage
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2, 3], bind_target_constants=['gbuffer', 'shadowMap'], shader_context='deferred_light/deferred_light/deferred_light')
    stages[-1]['command'] = 'draw_light_volume'

def make_deferred_indirect_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2, 3], bind_target_constants=['gbuffer', 'ssaotex'], shader_context='deferred_indirect/deferred_indirect/deferred_indirect')

def make_translucent_resolve_pass(stages, node_group, node, shader_references, asset_references):
    make_quad_pass(stages, node_group, node, shader_references, asset_references, target_index=1, bind_target_indices=[2], bind_target_constants=['gbuffer'], shader_context='translucent_resolve/translucent_resolve/translucent_resolve')

# Returns merge node
def buildNode(stages, node, node_group, shader_references, asset_references):
    stage = {}
    stage['params'] = []
    
    append_stage = True
    
    if node.bl_idname == 'MergeStagesNodeType':
        return node
    
    elif node.bl_idname == 'SetTargetNodeType':
        buildNode.last_bind_target = None
        make_set_target(stage, node_group, node)

    elif node.bl_idname == 'ClearTargetNodeType':
        color_val = None
        depth_val = None
        stencil_val = None
        if node.inputs[1].default_value == True:
            if node.inputs[2].is_linked: # Assume background color node is linked
                color_val = bpy.data.cameras[0].world_envtex_color
            else:
                color_val = node.inputs[2].default_value
        if node.inputs[3].default_value == True:
            depth_val = node.inputs[4].default_value
        if node.inputs[5].default_value == True:
            stencil_val = node.inputs[6].default_value
        make_clear_target(stage, color_val=color_val, depth_val=depth_val, stencil_val=stencil_val)
            
    elif node.bl_idname == 'DrawGeometryNodeType':
        make_draw_geometry(stage, node_group, node)
        
    elif node.bl_idname == 'DrawDecalsNodeType':
        make_draw_decals(stage, node_group, node, shader_references, asset_references)
        
    elif node.bl_idname == 'BindTargetNodeType':
        if buildNode.last_bind_target is not None:
            stage = buildNode.last_bind_target
            append_stage = False
        buildNode.last_bind_target = stage
        constant_name = node.inputs[2].default_value
        make_bind_target(stage, node_group, node, constant_name)
        
    elif node.bl_idname == 'DrawMaterialQuadNodeType':
        make_draw_material_quad(stage, node_group, node, shader_references, asset_references)
        
    elif node.bl_idname == 'DrawQuadNodeType':
        make_draw_quad(stage, node_group, node, shader_references, asset_references)
    
    elif node.bl_idname == 'DrawWorldNodeType':
        # Bind depth for quad
        # if node.inputs[1].is_linked:
        #     stage = {}
        #     stage['params'] = []
        #     buildNode.last_bind_target = stage
        #     if node.inputs[1].is_linked:
        #         make_bind_target(stage, node_group, node, target_index=1, constant_name='gbufferD')
        #     stages.append(stage)
        stage = {}
        stage['params'] = []
        # Draw quad
        # make_draw_world(stage, node_group, node, shader_references, asset_references, dome=False)
        # Draw dome
        make_draw_world(stage, node_group, node, shader_references, asset_references, dome=True)
    
    elif node.bl_idname == 'DrawCompositorNodeType' or node.bl_idname == 'DrawCompositorWithFXAANodeType':
        # Set target
        if node.inputs[1].is_linked:
            make_set_target(stage, node_group, node)
            stages.append(stage)
        # Bind targets
        if node.inputs[2].is_linked or node.inputs[3].is_linked:
            stage = {}
            stage['params'] = []
            buildNode.last_bind_target = stage
            if node.inputs[2].is_linked:
                make_bind_target(stage, node_group, node, target_index=2, constant_name='tex')
            if node.inputs[3].is_linked:
                make_bind_target(stage, node_group, node, target_index=3, constant_name='gbufferD')
            if node.inputs[4].is_linked:
                make_bind_target(stage, node_group, node, target_index=4, constant_name='gbuffer0')
            stages.append(stage)
        # Draw quad
        stage = {}
        stage['params'] = []
        with_fxaa = node.bl_idname == 'DrawCompositorWithFXAANodeType'
        make_draw_compositor(stage, node_group, node, shader_references, asset_references, with_fxaa=with_fxaa)
    
    elif node.bl_idname == 'BranchFunctionNodeType':
        make_branch_function(stage, node_group, node)
        stages.append(stage)
        process_call_function(stage, stages, node, node_group, shader_references, asset_references)
        return
        
    elif node.bl_idname == 'LoopStagesNodeType':
        # Just repeats the commands
        append_stage = False
        if node.outputs[1].is_linked:
            count = node.inputs[2].default_value
            for i in range(0, count):
                loopNode = findNodeByLinkFrom(node_group, node, node.outputs[1])
                buildNode(stages, loopNode, node_group, shader_references, asset_references)
    
    elif node.bl_idname == 'LoopLightsNodeType':
        append_stage = False
        stage['command'] = 'loop_lights'
        stages.append(stage)
        stage['returns_true'] = []
        if node.outputs[1].is_linked:
            loopNode = findNodeByLinkFrom(node_group, node, node.outputs[1])
            buildNode(stage['returns_true'], loopNode, node_group, shader_references, asset_references)
    
    elif node.bl_idname == 'DrawStereoNodeType':
        append_stage = False
        stage['command'] = 'draw_stereo'
        stages.append(stage)
        stage['returns_true'] = []
        if node.outputs[1].is_linked:
            loopNode = findNodeByLinkFrom(node_group, node, node.outputs[1])
            buildNode(stage['returns_true'], loopNode, node_group, shader_references, asset_references)

    elif node.bl_idname == 'CallFunctionNodeType':
        make_call_function(stage, node_group, node)
    
    elif node.bl_idname == 'QuadPassNodeType':
        make_quad_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False

    elif node.bl_idname == 'SSAOPassNodeType':
        make_ssao_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'SSAOReprojectPassNodeType':
        make_ssao_reproject_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'ApplySSAOPassNodeType':
        make_apply_ssao_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'SSRPassNodeType':
        make_ssr_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'BloomPassNodeType':
        make_bloom_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'MotionBlurPassNodeType':
        make_motion_blur_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'MotionBlurVelocityPassNodeType':
        make_motion_blur_velocity_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'CopyPassNodeType':
        make_copy_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'BlendPassNodeType':
        make_blend_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'CombinePassNodeType':
        make_combine_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'BlurBasicPassNodeType':
        make_blur_basic_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'DebugNormalsPassNodeType':
        make_debug_normals_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'FXAAPassNodeType':
        make_fxaa_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'SMAAPassNodeType':
        make_smaa_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'TAAPassNodeType':
        make_taa_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'SSSPassNodeType':
        make_sss_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'WaterPassNodeType':
        make_water_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'DeferredLightPassNodeType':
        make_deferred_light_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'DeferredIndirectPassNodeType':
        make_deferred_indirect_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False
    elif node.bl_idname == 'TranslucentResolvePassNodeType':
        make_translucent_resolve_pass(stages, node_group, node, shader_references, asset_references)
        append_stage = False

    if append_stage:
        stages.append(stage)
    
    # Build next stage
    if node.outputs[0].is_linked:
        stageNode = findNodeByLinkFrom(node_group, node, node.outputs[0])
        buildNode(stages, stageNode, node_group, shader_references, asset_references)
# Used to merge bind target nodes into one stage
buildNode.last_bind_target = None
# Used to determine shadowmap size
buildNode.last_set_target_w = 0
buildNode.last_set_target_h = 0


def findNodeByLink(node_group, to_node, inp):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == inp:
            return link.from_node

def findLink(node_group, to_node, inp):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == inp:
            return link
            
def findNodeByLinkFrom(node_group, from_node, outp):
    for link in node_group.links:
        if link.from_node == from_node and link.from_socket == outp:
            return link.to_node
   
def get_root_node(node_group):
    # Find first node linked to begin node
    rn = None
    for n in node_group.nodes:
        if n.bl_idname == 'BeginNodeType':
            # Store contexts
            bpy.data.cameras[0].pipeline_id = n.inputs[0].default_value
            geometry_contexts = n.inputs[1].default_value.split(',')
            bpy.data.cameras[0].geometry_context = geometry_contexts[0]
            if len(geometry_contexts) > 1:
                bpy.data.cameras[0].geometry_context_empty = geometry_contexts[1]
            bpy.data.cameras[0].shadows_context = n.inputs[2].default_value
            bpy.data.cameras[0].translucent_context = n.inputs[3].default_value
            bpy.data.cameras[0].overlay_context = n.inputs[4].default_value
            if n.inputs[5].default_value == False: # No HDR space lighting, append def
                bpy.data.worlds[0].world_defs += '_LDR'
            rn = findNodeByLinkFrom(node_group, n, n.outputs[0])
            break
    return rn

def preprocess_pipeline(root_node, node_group):
    render_targets = []
    depth_buffers = []
    preprocess_pipeline.velocity_def_added = False
    bpy.data.cameras[0].pipeline_passes = ''
    traverse_pipeline(root_node, node_group, render_targets, depth_buffers)
    return render_targets, depth_buffers
    
def traverse_pipeline(node, node_group, render_targets, depth_buffers):
    # Gather linked draw geometry contexts
    if node.bl_idname == 'DrawGeometryNodeType':
        if bpy.data.cameras[0].pipeline_passes != '':
            bpy.data.cameras[0].pipeline_passes += '_' # Separator
        bpy.data.cameras[0].pipeline_passes += node.inputs[1].default_value

    # Gather defs from linked nodes
    if node.bl_idname == 'TAAPassNodeType' or node.bl_idname == 'MotionBlurVelocityPassNodeType' or node.bl_idname == 'SSAOReprojectPassNodeType':
        if preprocess_pipeline.velocity_def_added == False:
            assets.add_khafile_def('WITH_VELOC')
            bpy.data.worlds[0].world_defs += '_Veloc'
            preprocess_pipeline.velocity_def_added = True
        if node.bl_idname == 'TAAPassNodeType':
            assets.add_khafile_def('WITH_TAA')
            # bpy.data.worlds[0].world_defs += '_TAA'
    elif node.bl_idname == 'SMAAPassNodeType':
        bpy.data.worlds[0].world_defs += '_SMAA'

    elif node.bl_idname == 'SSAOPassNodeType' or node.bl_idname == 'ApplySSAOPassNodeType' or node.bl_idname == 'SSAOReprojectPassNodeType':
        if bpy.data.worlds[0].generate_ssao: # SSAO enabled
            bpy.data.worlds[0].world_defs += '_SSAO'

    elif node.bl_idname == 'DrawStereoNodeType':
        assets.add_khafile_def('WITH_VR')
        bpy.data.worlds[0].world_defs += '_VR'

    # Collect render targets
    if node.bl_idname == 'SetTargetNodeType' or node.bl_idname == 'QuadPassNodeType' or node.bl_idname == 'DrawCompositorNodeType' or node.bl_idname == 'DrawCompositorWithFXAANodeType':
        if node.inputs[1].is_linked:
            tnode = findNodeByLink(node_group, node, node.inputs[1])
            parse_render_target(tnode, node_group, render_targets, depth_buffers)
    
    # Traverse loops
    elif node.bl_idname == 'LoopStagesNodeType' or node.bl_idname == 'LoopLightsNodeType' or node.bl_idname == 'DrawStereoNodeType':
        if node.outputs[1].is_linked:
            loop_node = findNodeByLinkFrom(node_group, node, node.outputs[1])
            traverse_pipeline(loop_node, node_group, render_targets, depth_buffers)
    
    # Prebuilt
    elif node.bl_idname == 'MotionBlurPassNodeType' or node.bl_idname == 'MotionBlurVelocityPassNodeType' or node.bl_idname == 'CopyPassNodeType' or node.bl_idname == 'BlendPassNodeType' or node.bl_idname == 'CombinePassNodeType' or node.bl_idname == 'DebugNormalsPassNodeType' or node.bl_idname == 'FXAAPassNodeType' or node.bl_idname == 'TAAPassNodeType' or node.bl_idname == 'WaterPassNodeType' or node.bl_idname == 'DeferredLightPassNodeType' or node.bl_idname == 'DeferredIndirectPassNodeType' or node.bl_idname == 'TranslucentResolvePassNodeType':
        if node.inputs[1].is_linked:
            tnode = findNodeByLink(node_group, node, node.inputs[1])
            parse_render_target(tnode, node_group, render_targets, depth_buffers)
    elif node.bl_idname == 'SSRPassNodeType' or node.bl_idname == 'ApplySSAOPassNodeType' or node.bl_idname == 'BloomPassNodeType' or node.bl_idname == 'SMAAPassNodeType':
        for i in range(1, 4):
            if node.inputs[i].is_linked:
                tnode = findNodeByLink(node_group, node, node.inputs[i])
                parse_render_target(tnode, node_group, render_targets, depth_buffers)
    elif node.bl_idname == 'SSAOPassNodeType' or node.bl_idname == 'SSAOReprojectPassNodeType' or node.bl_idname == 'SSSPassNodeType' or node.bl_idname == 'BlurBasicPassNodeType':
        for i in range(1, 3):
            if node.inputs[i].is_linked:
                tnode = findNodeByLink(node_group, node, node.inputs[i])
                parse_render_target(tnode, node_group, render_targets, depth_buffers)

    # Next stage
    if node.outputs[0].is_linked:
        stagenode = findNodeByLinkFrom(node_group, node, node.outputs[0])
        traverse_pipeline(stagenode, node_group, render_targets, depth_buffers)
        
def parse_render_target(node, node_group, render_targets, depth_buffers):
    if node.bl_idname == 'NodeReroute':
        tnode = findNodeByLink(node_group, node, node.inputs[0])
        parse_render_target(tnode, node_group, render_targets, depth_buffers)
        
    elif node.bl_idname == 'TargetNodeType':
        # Target already exists
        id = node.inputs[0].default_value
        for t in render_targets:
            if t['id'] == id:
                return
        
        depth_buffer_id = None
        if node.inputs[3].is_linked:
            # Find depth buffer
            depth_node = findNodeByLink(node_group, node, node.inputs[3])
            depth_buffer_id = depth_node.inputs[0].default_value
            # Append depth buffer
            found = False
            for db in depth_buffers:
                if db['id'] == depth_buffer_id:
                    found = True
                    break 
            if found == False:
                db = {}
                db['id'] = depth_buffer_id
                db['stencil_buffer'] = depth_node.inputs[1].default_value
                depth_buffers.append(db)    
        # Get scale
        scale = 1.0
        if node.inputs[1].is_linked:
            size_node = findNodeByLink(node_group, node, node.inputs[1])
            while size_node.bl_idname == 'NodeReroute': # Step through reroutes
                size_node = findNodeByLink(node_group, size_node, size_node.inputs[0])
            scale = size_node.inputs[0].default_value
            
        # Append target
        target = make_render_target(node, scale, depth_buffer_id=depth_buffer_id)
        render_targets.append(target)
        
    elif node.bl_idname == 'GBufferNodeType':
        for i in range(0, 5):
            if node.inputs[i].is_linked:
                n = findNodeByLink(node_group, node, node.inputs[i])
                parse_render_target(n, node_group, render_targets, depth_buffers)

def make_render_target(n, scale, depth_buffer_id=None):
    target = {}
    target['id'] = n.inputs[0].default_value
    target['width'] = n.inputs[1].default_value
    target['height'] = n.inputs[2].default_value
    target['format'] = n.inputs[4].default_value
    target['ping_pong'] = n.inputs[5].default_value
    if scale != 1.0:
        target['scale'] = scale    
    if depth_buffer_id != None:
        target['depth_buffer'] = depth_buffer_id
    return target
