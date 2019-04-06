import arm.utils

def skin_pos(vert):
    vert.add_include('compiled.inc')

    rpdat = arm.utils.get_rp()
    vert.add_include('std/skinning.glsl')
    vert.add_uniform('vec4 skinBones[skinMaxBones * 2]', link='_skinBones', included=True)
    vert.add_uniform('float posUnpack', link='_posUnpack')
    vert.write_attrib('vec4 skinA;')
    vert.write_attrib('vec4 skinB;')
    vert.write_attrib('getSkinningDualQuat(ivec4(bone * 32767), weight, skinA, skinB);')
    vert.write_attrib('spos.xyz *= posUnpack;')
    vert.write_attrib('spos.xyz += 2.0 * cross(skinA.xyz, cross(skinA.xyz, spos.xyz) + skinA.w * spos.xyz); // Rotate')
    vert.write_attrib('spos.xyz += 2.0 * (skinA.w * skinB.xyz - skinB.w * skinA.xyz + cross(skinA.xyz, skinB.xyz)); // Translate')
    vert.write_attrib('spos.xyz /= posUnpack;')

def skin_nor(vert, prep):
    rpdat = arm.utils.get_rp()
    vert.write(prep + 'wnormal = normalize(N * (vec3(nor.xy, pos.w) + 2.0 * cross(skinA.xyz, cross(skinA.xyz, vec3(nor.xy, pos.w)) + skinA.w * vec3(nor.xy, pos.w))));')
