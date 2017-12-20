import bpy

def skin_pos(vert):

    vert.add_include('compiled.glsl')

    if bpy.data.worlds['Arm'].arm_skin == 'GPU (Matrix)':
        vert.add_include('std/skinning_mat.glsl')
        vert.add_uniform('vec4 skinBones[skinMaxBones * 3]', link='_skinBones', included=True)
        vert.write('mat4 skinningMat = getSkinningMat(ivec4(bone), weight);')
        vert.write('spos *= skinningMat;')
    
    else: # Dual Quat
        vert.add_include('std/skinning.glsl')
        vert.add_uniform('vec4 skinBones[skinMaxBones * 2]', link='_skinBones', included=True)
        vert.write('vec4 skinA;')
        vert.write('vec4 skinB;')
        vert.write('getSkinningDualQuat(ivec4(bone), weight, skinA, skinB);')
        vert.write('spos.xyz += 2.0 * cross(skinA.xyz, cross(skinA.xyz, spos.xyz) + skinA.w * spos.xyz); // Rotate')
        vert.write('spos.xyz += 2.0 * (skinA.w * skinB.xyz - skinB.w * skinA.xyz + cross(skinA.xyz, skinB.xyz)); // Translate')

def skin_nor(vert, prep):
    if bpy.data.worlds['Arm'].arm_skin == 'GPU (Matrix)':
        vert.write('mat3 skinningMatVec = getSkinningMatVec(skinningMat);')
        vert.write(prep + 'wnormal = normalize(N * (nor * skinningMatVec));')

    else: # Dual Quat
        vert.write(prep + 'wnormal = normalize(N * (nor + 2.0 * cross(skinA.xyz, cross(skinA.xyz, nor) + skinA.w * nor)));')
