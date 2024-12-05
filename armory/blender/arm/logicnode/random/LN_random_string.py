from arm.logicnode.arm_nodes import *


class RandomStringNode(ArmLogicTreeNode):
    """Generate a random string based on a provided characters list.

    @input Length: The length of the string to generate. If the length is
        0 or negative, an empty string is returned.
    @input Characters: A string containing the characters from which the
        random generator can choose. For each letter in the output, the
        generator randomly samples a character in the input string, so
        the more often a character occurs in the input, the higher is
        its chance of appearance in each letter of the result.
        For example, if you provide `aaab` as a character string,
        approximately 75% percent of the characters in all generated
        strings are `a`, the remaining 25% are `b`.
    """
    bl_idname = 'LNRandomStringNode'
    bl_label = 'Random String'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmIntSocket', 'Length')
        self.add_input('ArmStringSocket', 'Characters')
        self.add_output('ArmStringSocket', 'String')
