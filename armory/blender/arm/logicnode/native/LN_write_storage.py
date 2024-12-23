from arm.logicnode.arm_nodes import *


class WriteStorageNode(ArmLogicTreeNode):
    """Writes a given value to the application's default storage file.
    Each value is uniquely identified by a key, which can be used to
    later read the value from the storage file.

    Each key can only refer to one value, so writing a second value with
    a key that is already used overwrites the already stored value with
    the second value.

    The location of the default storage file varies on different
    platforms, as implemented by the Kha storage API:
    - *Windows*: `%USERPROFILE%/Saved Games/<application name>/default.kha`
    - *Linux*: one of `$HOME/.<application name>/default.kha`, `$XDG_DATA_HOME/.<application name>/default.kha` or `$HOME/.local/share/default.kha`
    - *MacOS*: `~/Library/Application Support/<application name>/default.kha`
    - *iOS*: `~/Library/Application Support/<application name>/default.kha`
    - *Android*: `<internalDataPath>/<application package name>/files/default.kha`
    - *HTML 5*: saved in the local storage (web storage API) for the project's [origin](https://developer.mozilla.org/en-US/docs/Glossary/Origin).

    `<application name>` refers to the name set at `Armory Exporter > Name`,
    `<application package name>` is the generated package name on Android.

    @seeNode Read Storage
    """
    bl_idname = 'LNWriteStorageNode'
    bl_label = 'Write Storage'
    arm_section = 'file'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Key')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
