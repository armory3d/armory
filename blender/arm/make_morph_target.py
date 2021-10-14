import arm.utils

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


    

def write(vert):
    vert.add_include('compiled.inc')
    vert.add_include('std/morph_target.glsl')

    vert.add_in('vec2 tex1')
    vert.write_attrib('texCoord1 = tex1 * texUnpack;')

    vert.add_uniform('float posUnpack', link='_posUnpack')
    vert.add_uniform('sampler2D morphData', link='_morphData')
    vert.add_uniform('vec4 morphPosition', link='_morphPosition', included=True)