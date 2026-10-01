"""
Parallax Occlusion Mapping (POM) node for Armory3D.

This node provides POM with self-shadowing support for realistic
depth effects on surfaces using height maps.

Usage:
    1. Connect a height/displacement map to the Height input
    2. Connect the UV output to your texture nodes
    3. Optionally use Shadow output to modulate lighting

Author: Armory3D Contributors
License: zlib
Issue: #2609
"""

import bpy
from bpy.types import Node
from bpy.props import FloatProperty, IntProperty, BoolProperty


class ArmParallaxOcclusionNode(Node):
    """Parallax Occlusion Mapping node with self-shadowing support."""
    
    bl_idname = 'ArmParallaxOcclusionNodeType'
    bl_label = 'Parallax Occlusion Mapping'
    bl_icon = 'MATERIAL_DATA'
    
    # Node properties
    height_scale: FloatProperty(
        name='Height Scale',
        description='Depth scale of the parallax effect',
        default=0.05,
        min=0.0,
        max=1.0,
        soft_min=0.01,
        soft_max=0.2
    )
    
    min_layers: IntProperty(
        name='Min Layers',
        description='Minimum number of raymarch steps (used at grazing angles)',
        default=8,
        min=1,
        max=64
    )
    
    max_layers: IntProperty(
        name='Max Layers',
        description='Maximum number of raymarch steps (used at steep angles)',
        default=32,
        min=1,
        max=128
    )
    
    enable_shadows: BoolProperty(
        name='Self Shadowing',
        description='Enable self-shadowing for more realistic depth',
        default=True
    )
    
    def init(self, context):
        """Initialize node inputs and outputs."""
        # Inputs
        self.inputs.new('NodeSocketFloat', 'Height')
        self.inputs.new('NodeSocketVector', 'UV')
        
        scale_input = self.inputs.new('NodeSocketFloat', 'Scale')
        scale_input.default_value = 0.05
        
        min_input = self.inputs.new('NodeSocketFloat', 'Min Layers')
        min_input.default_value = 8.0
        
        max_input = self.inputs.new('NodeSocketFloat', 'Max Layers')
        max_input.default_value = 32.0
        
        # Outputs
        self.outputs.new('NodeSocketVector', 'UV')
        self.outputs.new('NodeSocketFloat', 'Shadow')
    
    def draw_buttons(self, context, layout):
        """Draw node UI buttons."""
        layout.prop(self, 'enable_shadows')
    
    def draw_buttons_ext(self, context, layout):
        """Draw extended node UI in sidebar."""
        layout.prop(self, 'height_scale')
        layout.prop(self, 'min_layers')
        layout.prop(self, 'max_layers')
        layout.prop(self, 'enable_shadows')


def register():
    """Register the node class with Blender."""
    bpy.utils.register_class(ArmParallaxOcclusionNode)


def unregister():
    """Unregister the node class from Blender."""
    bpy.utils.unregister_class(ArmParallaxOcclusionNode)
