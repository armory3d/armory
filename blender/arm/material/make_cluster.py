import bpy

def write(vert, frag):
    wrd = bpy.data.worlds['Arm']
    is_shadows = '_ShadowMap' in wrd.world_defs
    
    frag.add_include('std/clusters.glsl')
    frag.add_uniform('vec2 cameraProj', link='_cameraPlaneProj')
    frag.add_uniform('vec2 cameraPlane', link='_cameraPlane')
    frag.add_uniform('vec4 lightsArray[maxLights * 2]', link='_lightsArray')
    frag.add_uniform('sampler2D clustersData', link='_clustersData')
    if is_shadows:
        frag.add_uniform('vec2 lightProj', link='_lightPlaneProj', included=True)
        frag.add_uniform('samplerCubeShadow shadowMapPoint[4]', included=True)
    vert.add_out('vec4 wvpposition')
    vert.write('wvpposition = gl_Position;')
    # wvpposition.z / wvpposition.w
    frag.write('float viewz = linearize(gl_FragCoord.z, cameraProj);')
    frag.write('int clusterI = getClusterI((wvpposition.xy / wvpposition.w) * 0.5 + 0.5, viewz, cameraPlane);')
    frag.write('int numLights = int(texelFetch(clustersData, ivec2(clusterI, 0), 0).r * 255);')

    frag.write('#ifdef HLSL')
    frag.write('viewz += texture(clustersData, vec2(0.0)).r * 1e-9;') # TODO: krafix bug, needs to generate sampler
    frag.write('#endif')

    if '_Spot' in wrd.world_defs:
        frag.add_uniform('vec4 lightsArraySpot[maxLights]', link='_lightsArraySpot')
        frag.write('int numSpots = int(texelFetch(clustersData, ivec2(clusterI, 1 + maxLightsCluster), 0).r * 255);')
        frag.write('int numPoints = numLights - numSpots;')
        if is_shadows:
            frag.add_uniform('mat4 LWVPSpot0', link='_biasLightWorldViewProjectionMatrixSpot0', included=True)
            frag.add_uniform('mat4 LWVPSpot1', link='_biasLightWorldViewProjectionMatrixSpot1', included=True)
            frag.add_uniform('mat4 LWVPSpot2', link='_biasLightWorldViewProjectionMatrixSpot2', included=True)
            frag.add_uniform('mat4 LWVPSpot3', link='_biasLightWorldViewProjectionMatrixSpot3', included=True)
            frag.add_uniform('sampler2DShadow shadowMapSpot[4]', included=True)

    frag.write('for (int i = 0; i < min(numLights, maxLightsCluster); i++) {')
    frag.write('int li = int(texelFetch(clustersData, ivec2(clusterI, i + 1), 0).r * 255);')
    
    frag.write('direct += sampleLight(')
    frag.write('    wposition,')
    frag.write('    n,')
    frag.write('    vVec,')
    frag.write('    dotNV,')
    frag.write('    lightsArray[li * 2].xyz,') # lp
    frag.write('    lightsArray[li * 2 + 1].xyz,') # lightCol
    frag.write('    albedo,')
    frag.write('    roughness,')
    frag.write('    specular,')
    frag.write('    f0')
    if is_shadows:
        frag.write('    , li, lightsArray[li * 2].w') # bias
    if '_Spot' in wrd.world_defs:
        frag.write('    , li > numPoints - 1')
        frag.write('    , lightsArray[li * 2 + 1].w') # cutoff
        frag.write('    , lightsArraySpot[li].w') # cutoff - exponent
        frag.write('    , lightsArraySpot[li].xyz') # spotDir
    if '_VoxelShadow' in wrd.world_defs and '_VoxelAOvar' in wrd.world_defs:
        frag.write('  , voxels, voxpos')
    frag.write(');')

    frag.write('}') # for numLights