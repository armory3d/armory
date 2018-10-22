import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class TimerNode(Node, ArmLogicTreeNode):
    '''Timer node'''
    bl_idname = 'LNTimerNode'
    bl_label = 'Timer'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'Start')
        self.inputs.new('ArmNodeSocketAction', 'Pause')
        self.inputs.new('ArmNodeSocketAction', 'Stop')
        self.inputs.new('NodeSocketFloat', 'Duration')
        self.inputs[-1].default_value = 1.0
        self.inputs.new('NodeSocketInt', 'Repeat')
        self.inputs[-1].default_value = 1

        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('ArmNodeSocketAction', 'Done')
        self.outputs.new('NodeSocketBool', 'Running')
        self.outputs.new('NodeSocketInt', 'Time Passed')
        self.outputs.new('NodeSocketInt', 'Time Left')
        self.outputs.new('NodeSocketFloat', 'Progress')
        self.outputs.new('NodeSocketFloat', 'Repetitions')

add_node(TimerNode, category='Action')
