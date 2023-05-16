from arm.logicnode.arm_nodes import *

class RemoveObjectNode(ArmLogicTreeNode):
    """This node will remove a scene object or a scene object and its children.
    
    @input Object: Scene object to remove.
    @input Remove Children: Remove scene object's children too.
    @input Keep Children Transforms: Scene object's children will maintain current transforms when the scene object is removed, else children transforms revert to scene origin transforms.
    """
    bl_idname = 'LNRemoveObjectNode'
    bl_label = 'Remove Object'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmBoolSocket', 'Remove Children', default_value=True)
        self.add_input('ArmBoolSocket', 'Keep Children Transforms', default_value=True)

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)