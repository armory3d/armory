import importlib
import pkgutil

from arm.logicnode import arm_nodes

# Register node menu categories
arm_nodes.add_category('Logic', icon='OUTLINER', description="Test") #MOD_MASK | SELECT_DIFFERENCE
arm_nodes.add_category('Event', icon='INFO', description="Test")
arm_nodes.add_category('Input', icon='GREASEPENCIL', section="default") #EVENT_RETURN
arm_nodes.add_category('Native', icon='MEMORY', section="default") #SYSTEM

arm_nodes.add_category('Camera', icon='OUTLINER_OB_CAMERA', section="data")
arm_nodes.add_category('Material', icon='MATERIAL', section="data")
arm_nodes.add_category('Light', icon='LIGHT', section="data")
arm_nodes.add_category('Object', icon='OBJECT_DATA', section="data")
arm_nodes.add_category('Scene', icon='SCENE_DATA', section="data")
arm_nodes.add_category('Trait', icon='NODETREE', section="data")

arm_nodes.add_category('Animation', icon='SEQUENCE', section="motion") # FRAME_NEXT | ONIONSKIN_ON
arm_nodes.add_category('Navmesh', icon='UV_VERTEXSEL', section="motion") #TRACKING_FORWARDS
arm_nodes.add_category('Transform', icon='TRANSFORM_ORIGINS', section="motion")
arm_nodes.add_category('Physics', icon='PHYSICS', section="motion")

arm_nodes.add_category('Array', icon='LIGHTPROBE_GRID', section="values")
arm_nodes.add_category('Math', icon='FORCE_HARMONIC', section="values") #LINENUMBERS_ON | CON_TRANSFORM
arm_nodes.add_category('Random', icon='SEQ_HISTOGRAM', section="values") #FORCE_BOID | OUTLINER_OB_FORCE_FIELD
arm_nodes.add_category('String', icon='SORTALPHA', section="values") #SYNTAX_OFF | SORTSIZE | OUTLINER_OB_FONT | FILE_TEXT
arm_nodes.add_category('Variable', icon='OPTIONS', section="values") #FILE_VOLUME

arm_nodes.add_category('Canvas', icon='RENDERLAYERS', section="graphics") #CON_SIZELIKE | IMAGE_RGB_ALPHA
arm_nodes.add_category('Postprocess', icon='FREEZE', section="graphics")
arm_nodes.add_category('Renderpath', icon='STICKY_UVS_LOC', section="graphics")

arm_nodes.add_category('Sound', icon='OUTLINER_OB_SPEAKER', section="sound")

arm_nodes.add_category('Miscellaneous', icon='RESTRICT_COLOR_ON', section="misc")
arm_nodes.add_category('Layout', icon='SEQ_STRIP_DUPLICATE', section="misc") # ANCHOR_LEFT | UV_ISLANDSEL

# Import all nodes so that the modules are registered
__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    if is_pkg:
        _module = loader.find_module(module_name).load_module(module_name)
    else:
        _module = importlib.import_module(f'{__name__}.{module_name}')
    globals()[module_name] = _module
