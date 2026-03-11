from arm.logicnode.arm_nodes import *

class SetSSSRSettingsNode(ArmLogicTreeNode):
    """设置 SSSR (随机化屏幕空间反射) 参数"""
    
    bl_idname = 'LNSetSSSRSettingsNode'
    bl_label = '设置 SSSR 参数'
    bl_description = '配置 SSSR 蓝噪声采样和时间累积参数'
    arm_section = 'SSSR'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', '反射强度', default_value=1.0)
        self.add_input('ArmIntSocket', '样本数量', default_value=4)
        self.add_input('ArmFloatSocket', '最大步长', default_value=0.1)
        self.add_input('ArmIntSocket', '最大步数', default_value=100)
        self.add_input('ArmBoolSocket', '启用时间累积', default_value=True)
        self.add_input('ArmFloatSocket', '累积衰减', default_value=0.95)
        self.add_input('ArmBoolSocket', '启用蓝噪声', default_value=True)
        
        self.add_output('ArmNodeSocketAction', 'Out')
