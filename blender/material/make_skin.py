
def skin_pos(vert):
    vert.add_include('../../Shaders/compiled.glsl')
    vert.add_include('../../Shaders/std/skinning.glsl')
    vert.add_uniform('float skinBones[skinMaxBones * 8]', link='_skinBones', included=True)
    vert.write('vec4 skinA;')
    vert.write('vec4 skinB;')
    vert.write('getSkinningDualQuat(ivec4(bone), weight, skinA, skinB);')
    vert.write('spos.xyz += 2.0 * cross(skinA.xyz, cross(skinA.xyz, spos.xyz) + skinA.w * spos.xyz); // Rotate')
    vert.write('spos.xyz += 2.0 * (skinA.w * skinB.xyz - skinB.w * skinA.xyz + cross(skinA.xyz, skinB.xyz)); // Translate')
