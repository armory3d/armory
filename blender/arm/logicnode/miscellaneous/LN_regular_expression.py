from arm.logicnode.arm_nodes import *

class RegularExpressionNode(ArmLogicTreeNode):
    """
    The first argument is a string with a regular expression pattern, the second one is a string with flags.

    @input RegExp Pattern: regular expression patterns such as
        - `.`: any character
        - `*`: repeat zero-or-more
        - `+`: repeat one-or-more
        - `?`: optional zero-or-one
        - `[A-Z0-9]`: character ranges
        - `[^\\r\\n\\t]`: character not-in-range
        - `(...)`: parenthesis to match groups of characters
        - `^`: beginning of the string (beginning of a line in multiline matching mode)
        - `$`: end of the string (end of a line in multiline matching mode)
        - `|`: "OR" statement.

    @input RegExp Flags: possible flags are the following
        - `i`: case insensitive matching
        - `g`: global replace or split, see below
        - `m`: multiline matching, ^ and $ represent the beginning and end of a line
        - `s`: the dot . will also match newlines (not supported by C# and JavaScript versions before ES2018)
        - `u`: use UTF-8 matching (Neko and C++ targets only)

    @input String: String to match, split or replace
    @input Replace: String to use when replace

    @output Match: boolean result comparing the regular expression pattern with the string
    @output Matched: array containing list of matched patterns
    @output Split: array string of string splits using the pattern
    @output Replace: new string with the pattern replaced

    """
    bl_idname = 'LNRegularExpressionNode'
    bl_label = 'Regular Expression'

    arm_version = 1

    def remove_extra_inputs(self, context):
        while len(self.outputs) > 0:
            self.outputs.remove(self.outputs[-1])
        if len(self.inputs) != 3:
            self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Match':
            self.add_output('ArmBoolSocket', 'Match')
            self.add_output('ArmNodeSocketArray', 'Matched', is_var=False)
        if self.property0 == 'Split':
            self.add_output('ArmNodeSocketArray', 'Split', is_var=False)
        if self.property0 == 'Replace':
            self.add_input('ArmStringSocket', 'Replace')
            self.add_output('ArmStringSocket', 'String')

    property0: HaxeEnumProperty(
        'property0',
        items = [('Match', 'Match', 'A regular expression is used to compare a string. Use () in the pattern to retrieve Matched groups'),
                ('Split', 'Split', 'A regular expression can also be used to split a string into several substrings'),
                ('Replace', 'Replace', 'A regular expression can also be used to replace a part of the string')],
        name='', default='Match', update=remove_extra_inputs)

    def arm_init(self, context):

        self.add_input('ArmStringSocket', 'RegExp Pattern')
        self.add_input('ArmStringSocket', 'RegExp Flags')
        self.add_input('ArmStringSocket', 'String')

        self.add_output('ArmBoolSocket', 'Match')
        self.add_output('ArmNodeSocketArray', 'Matched', is_var=False)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
