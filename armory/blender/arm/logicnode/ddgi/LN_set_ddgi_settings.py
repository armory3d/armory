from arm.logicnode.arm_nodes import *

class SetDDGISettingsNode(ArmLogicTreeNode):
    """设置 DDGI (动态漫反射全局光照) 参数"""
    
    bl_idname = 'LNSetDDGISettingsNode'
    bl_label = '设置 DDGI 参数'
    bl_description = '配置 DDGI 探针网格和渲染参数'
    arm_section = 'DDGI'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', '探针间距', default_value=2.0)
        self.add_input('ArmFloatSocket', '探针半径', default_value=1.0)
        self.add_input('ArmIntSocket', '网格分辨率 X', default_value=16)
        self.add_input('ArmIntSocket', '网格分辨率 Y', default_value=16)
        self.add_input('ArmIntSocket', '网格分辨率 Z', default_value=16)
        self.add_input('ArmFloatSocket', '强度', default_value=1.0)
        self.add_input('ArmBoolSocket', '启用时间累积', default_value=True)
        
        self.add_output('ArmNodeSocketAction', 'Out')
