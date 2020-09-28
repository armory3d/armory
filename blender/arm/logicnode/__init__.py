import importlib
import pkgutil

from arm.logicnode import arm_nodes

# Register node menu categories
arm_nodes.add_category('Logic', icon='OUTLINER', section="basic",
                       description="Logic nodes are used to control execution flow using branching, loops, gates etc.")
arm_nodes.add_category('Event', icon='INFO', section="basic")
arm_nodes.add_category('Input', icon='GREASEPENCIL', section="basic")
arm_nodes.add_category('Native', icon='MEMORY', section="basic",
                       description="The Native category contains nodes which interact with the system (Input/Output functionality, etc.) or Haxe.")

arm_nodes.add_category('Camera', icon='OUTLINER_OB_CAMERA', section="data")
arm_nodes.add_category('Material', icon='MATERIAL', section="data")
arm_nodes.add_category('Light', icon='LIGHT', section="data")
arm_nodes.add_category('Object', icon='OBJECT_DATA', section="data")
arm_nodes.add_category('Scene', icon='SCENE_DATA', section="data")
arm_nodes.add_category('Trait', icon='NODETREE', section="data")

arm_nodes.add_category('Animation', icon='SEQUENCE', section="motion")
arm_nodes.add_category('Navmesh', icon='UV_VERTEXSEL', section="motion")
arm_nodes.add_category('Transform', icon='TRANSFORM_ORIGINS', section="motion")
arm_nodes.add_category('Physics', icon='PHYSICS', section="motion")

arm_nodes.add_category('Array', icon='LIGHTPROBE_GRID', section="values")
arm_nodes.add_category('Math', icon='FORCE_HARMONIC', section="values")
arm_nodes.add_category('Random', icon='SEQ_HISTOGRAM', section="values")
arm_nodes.add_category('String', icon='SORTALPHA', section="values")
arm_nodes.add_category('Variable', icon='OPTIONS', section="values")

arm_nodes.add_category('Canvas', icon='RENDERLAYERS', section="graphics",
                       description="Note: To get the canvas, be sure that the node(s) and the canvas (UI) is attached to the same object.")
arm_nodes.add_category('Postprocess', icon='FREEZE', section="graphics")
arm_nodes.add_category('Renderpath', icon='STICKY_UVS_LOC', section="graphics")

arm_nodes.add_category('Sound', icon='OUTLINER_OB_SPEAKER', section="sound")

arm_nodes.add_category('Miscellaneous', icon='RESTRICT_COLOR_ON', section="misc")
arm_nodes.add_category('Layout', icon='SEQ_STRIP_DUPLICATE', section="misc")

# Make sure that logic node extension packs are displayed at the end
# of the menu by default unless they declare it otherwise
arm_nodes.add_category_section('default')

# Import all nodes so that the modules are registered
__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    if is_pkg:
        _module = loader.find_module(module_name).load_module(module_name)
    else:
        _module = importlib.import_module(f'{__name__}.{module_name}')
    globals()[module_name] = _module
