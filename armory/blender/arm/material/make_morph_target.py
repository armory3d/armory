import arm.utils

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)

def morph_pos(vert):
    rpdat = arm.utils.get_rp()
    vert.add_include('compiled.inc')
    vert.add_include('std/morph_target.glsl')
    vert.add_uniform('sampler2D morphDataPos', link='_morphDataPos', included=True)
    vert.add_uniform('sampler2D morphDataNor', link='_morphDataNor', included=True)
    vert.add_uniform('vec4 morphWeights[8]', link='_morphWeights', included=True)
    vert.add_uniform('vec2 morphScaleOffset', link='_morphScaleOffset', included=True)
    vert.add_uniform('vec2 morphDataDim', link='_morphDataDim', included=True)
    vert.add_uniform('float texUnpack', link='_texUnpack')
    vert.add_uniform('float posUnpack', link='_posUnpack')
    vert.write_attrib('vec2 texCoordMorph = morph * texUnpack;')
    vert.write_attrib('spos.xyz *= posUnpack;')
    vert.write_attrib('getMorphedVertex(texCoordMorph, spos.xyz);')
    vert.write_attrib('spos.xyz /= posUnpack;')

def morph_nor(vert, is_bone, prep):
    vert.write_attrib('vec3 morphNor = vec3(0, 0, 0);')
    vert.write_attrib('getMorphedNormal(texCoordMorph, vec3(nor.xy, pos.w), morphNor);')
    if not is_bone:
        vert.write_attrib(prep + 'wnormal = normalize(N * morphNor);')
