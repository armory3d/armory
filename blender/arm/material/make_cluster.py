import bpy
import arm.utils

def write(vert, frag):
    wrd = bpy.data.worlds['Arm']
    is_shadows = '_ShadowMap' in wrd.world_defs
    is_shadows_atlas = '_ShadowMapAtlas' in wrd.world_defs
    is_single_atlas = is_shadows_atlas and '_SingleAtlas' in wrd.world_defs

    frag.add_include_front('std/clusters.glsl')
    frag.add_uniform('vec2 cameraProj', link='_cameraPlaneProj')
    frag.add_uniform('vec2 cameraPlane', link='_cameraPlane')
    frag.add_uniform('vec4 lightsArray[maxLights * 3]', link='_lightsArray')
    frag.add_uniform('sampler2D clustersData', link='_clustersData')
    if is_shadows:
        frag.add_uniform('bool receiveShadow')
        frag.add_uniform('vec2 lightProj', link='_lightPlaneProj', included=True)
        if is_shadows_atlas:
            if not is_single_atlas:
                frag.add_uniform('sampler2DShadow shadowMapAtlasPoint', included=True)
            else:
                frag.add_uniform('sampler2DShadow shadowMapAtlas', top=True)
            frag.add_uniform('vec4 pointLightDataArray[maxLightsCluster]', link='_pointLightsAtlasArray', included=True)
        else:
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
        frag.add_uniform('vec4 lightsArraySpot[maxLights * 2]', link='_lightsArraySpot')
        frag.write('int numSpots = int(texelFetch(clustersData, ivec2(clusterI, 1 + maxLightsCluster), 0).r * 255);')
        frag.write('int numPoints = numLights - numSpots;')
        if is_shadows:
            if is_shadows_atlas:
                if not is_single_atlas:
                    frag.add_uniform('sampler2DShadow shadowMapAtlasSpot', included=True)
                else:
                    frag.add_uniform('sampler2DShadow shadowMapAtlas', top=True)
            else:
                frag.add_uniform('sampler2DShadow shadowMapSpot[4]', included=True)
            # FIXME: type is actually mat4, but otherwise it will not be set as floats when writing the shaders' json files
            frag.add_uniform('vec4 LWVPSpotArray[maxLightsCluster]', link='_biasLightWorldViewProjectionMatrixSpotArray', included=True)

    frag.write('for (int i = 0; i < min(numLights, maxLightsCluster); i++) {')
    frag.write('int li = int(texelFetch(clustersData, ivec2(clusterI, i + 1), 0).r * 255);')

    if '_MicroShadowing' in wrd.world_defs:
        frag.add_include('std/gbuffer.glsl')
        frag.add_uniform('sampler2D gbuffer1')
        frag.add_uniform('sampler2D gbuffer0')
        frag.add_uniform('sampler2D gbufferD')
        frag.add_uniform('vec3 eyeLook', link='_cameraLook')
        frag.write('vec4 g0 = textureLod(gbuffer0, texCoord, 0.0); // Normal.xy, metallic/roughness, matid')
        frag.write('vec3 n2;');
        frag.write('n2.z = 1.0 - abs(g0.x) - abs(g0.y);')
        frag.write('n2.xy = n2.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);')
        frag.write('n2 = normalize(n2);')
        frag.write('vec4 g1 = textureLod(gbuffer1, texCoord, 0.0);')
        frag.write('vec2 occspec = unpackFloat2(g1.a);')
        frag.write('float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;')
        frag.write('vec3 p = getPos(eye, eyeLook, normalize(viewRay), depth, cameraProj);')
        frag.write('vec3 v = normalize(eye - p);')
        frag.write('float dotNV2 = max(dot(n2, v), 0.0);')
        frag.write('occspec.x = mix(1.0, occspec.x, dotNV2); // AO Fresnel')

    frag.write('direct += sampleLight(')
    frag.write('    wposition,')
    if '_MicroShadowing' in wrd.world_defs:
        frag.write('    n2,')
        frag.write('    vVec,')
        frag.write('    dotNV2,')
    else:
    	frag.write('    n,')
    	frag.write('    vVec,')
    	frag.write('    dotNV')

    frag.write('    lightsArray[li * 3].xyz,') # lp
    frag.write('    lightsArray[li * 3 + 1].xyz,') # lightCol
    frag.write('    albedo,')
    frag.write('    roughness,')
    frag.write('    specular,')
    frag.write('    f0')
    if is_shadows:
        frag.write('\t, li, lightsArray[li * 3 + 2].x, lightsArray[li * 3 + 2].z != 0.0') # bias
    if '_Spot' in wrd.world_defs:
        frag.write('\t, lightsArray[li * 3 + 2].y != 0.0')
        frag.write('\t, lightsArray[li * 3 + 2].y') # spot size (cutoff)
        frag.write('\t, lightsArraySpot[li].w') # spot blend (exponent)
        frag.write('\t, lightsArraySpot[li].xyz') # spotDir
        frag.write('\t, vec2(lightsArray[li * 3].w, lightsArray[li * 3 + 1].w)') # scale
        frag.write('\t, lightsArraySpot[li * 2 + 1].xyz') # right
    if '_VoxelShadow' in wrd.world_defs and '_VoxelAOvar' in wrd.world_defs:
        frag.write('  , voxels, voxpos')
    if '_MicroShadowing' in wrd.world_defs:
        frag.write(' , occspec.x')
    if '_SSRS' in wrd.world_defs:
        frag.add_uniform('sampler2D gbufferD')
        frag.add_uniform('mat4 invVP')
       	frag.write(' , gbufferD, invVP, eye')
    frag.write(');')

    frag.write('}') # for numLights
