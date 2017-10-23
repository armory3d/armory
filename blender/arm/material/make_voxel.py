import bpy
import arm.utils
import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
import arm.material.make_particle as make_particle

def make(context_id):
    rpdat = arm.utils.get_rp()
    if rpdat.rp_gi == 'Voxel GI':
        return make_gi(context_id)
    else:
        return make_ao(context_id)

def make_gi(context_id):
    con_voxel = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'always', 'cull_mode': 'none', 'color_write_red': False, 'color_write_green': False, 'color_write_blue': False, 'color_write_alpha': False, 'conservative_raster': True })
    wrd = bpy.data.worlds['Arm']

    is_shadows = not '_NoShadows' in wrd.world_defs

    vert = con_voxel.make_vert()
    frag = con_voxel.make_frag()
    geom = con_voxel.make_geom()
    tesc = None
    tese = None

    geom.ins = vert.outs
    frag.ins = geom.outs

    frag.add_include('../../Shaders/compiled.glsl')
    frag.add_include('../../Shaders/std/math.glsl')
    frag.add_include('../../Shaders/std/imageatomic.glsl')
    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')

    rpdat = arm.utils.get_rp()
    if rpdat.rp_voxelgi_hdr:
        frag.add_uniform('layout(rgba16) image3D voxels')
    else:
        # frag.add_uniform('layout(rgba8) image3D voxels')
        frag.add_uniform('layout(r32ui) uimage3D voxels')

    frag.add_uniform('vec3 lightPos', '_lampPosition')
    frag.add_uniform('vec3 lightColor', '_lampColorVoxel')
    frag.add_uniform('int lightType', '_lampType')
    frag.add_uniform('vec3 lightDir', '_lampDirection')

    frag.write('if (abs(voxposition.z) > ' + rpdat.rp_voxelgi_resolution_z + ' || abs(voxposition.x) > 1 || abs(voxposition.y) > 1) return;')
    frag.write('vec3 wposition = voxposition * voxelgiHalfExtents;')
    if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
        frag.add_uniform('vec3 eyeSnap', '_cameraPositionSnap')
        frag.write('wposition += eyeSnap;')

    frag.write('float visibility = 1.0;')
    frag.write('vec3 lp = lightPos - wposition;')
    frag.write('vec3 l;')
    frag.write('if (lightType == 0) l = lightDir;')
    frag.write('else { l = normalize(lp); visibility *= attenuate(distance(wposition, lightPos)); }')

    frag.write('float dotNL = max(dot(wnormal, l), 0.0);')
    frag.write('if (dotNL == 0.0) return;')

    if is_shadows:
        frag.add_include('../../Shaders/std/shadows.glsl')
        frag.add_uniform('sampler2D shadowMap', included=True)
        frag.add_uniform('samplerCube shadowMapCube', included=True)
        frag.add_uniform('int lightShadow', '_lampCastShadow')
        frag.add_uniform('vec2 lightPlane', '_lampPlane')
        frag.add_uniform('float shadowsBias', '_lampShadowsBias')
        frag.write('if (lightShadow == 1 && lampPos.w > 0.0) {')
        frag.write('    vec3 lpos = lampPos.xyz / lampPos.w;')
        # frag.write('    if (lpos.x < 0.0 || lpos.y < 0.0 || lpos.x > 1.0 || lpos.y > 1.0) return;')
        # Note: shadowmap bound for sun lamp is tight behind the camera - can cause darkening no close surfaces
        frag.write('    if (texture(shadowMap, lpos.xy).r < lpos.z - shadowsBias) visibility = 0.0;')
        # frag.write('    visibility = PCF(lpos.xy, lpos.z - shadowsBias);')
        frag.write('}')
        frag.write('else if (lightShadow == 2) visibility *= float(texture(shadowMapCube, -l).r + shadowsBias > lpToDepth(lp, lightPlane));')

    # frag.write('if (lightType == 2) {')
    # frag.write('    float spotEffect = dot(lightDir, l);')
    # frag.write('    if (spotEffect < spotlightData.x) {')
    # frag.write('        visibility *= smoothstep(spotlightData.y, spotlightData.x, spotEffect);')
    # frag.write('    }')
    # frag.write('}')

    # if '_PolyLight' in wrd.world_defs:
    #     frag.add_include('../../Shaders/std/ltc.glsl')
    #     frag.add_uniform('sampler2D sltcMat', link='_ltcMat')
    #     frag.add_uniform('sampler2D sltcMag', link='_ltcMag')
    #     frag.add_uniform('vec3 lampArea0', link='_lampArea0')
    #     frag.add_uniform('vec3 lampArea1', link='_lampArea1')
    #     frag.add_uniform('vec3 lampArea2', link='_lampArea2')
    #     frag.add_uniform('vec3 lampArea3', link='_lampArea3')
    #     frag.write('if (lightType == 3) {')
    #     frag.write('    float theta = acos(dotNV);')
    #     frag.write('    vec2 tuv = vec2(roughness, theta / (0.5 * PI));')
    #     frag.write('    tuv = tuv * LUT_SCALE + LUT_BIAS;')
    #     frag.write('    vec4 t = texture(sltcMat, tuv);')
    #     frag.write('    mat3 invM = mat3(vec3(1.0, 0.0, t.y), vec3(0.0, t.z, 0.0), vec3(t.w, 0.0, t.x));')
    #     frag.write('    float ltcspec = ltcEvaluate(n, vVec, dotNV, wposition, invM, lampArea0, lampArea1, lampArea2, lampArea3);')
    #     frag.write('    ltcspec *= texture(sltcMag, tuv).a;')
    #     frag.write('    float ltcdiff = ltcEvaluate(n, vVec, dotNV, wposition, mat3(1.0), lampArea0, lampArea1, lampArea2, lampArea3);')
    #     frag.write('    direct = albedo * ltcdiff + ltcspec;')
    #     frag.write('}')
    #     frag.write('else {')
    #     frag.tab += 1

    frag.write('vec3 basecol;')
    frag.write('float roughness;') #
    frag.write('float metallic;') #
    frag.write('float occlusion;') #
    parse_opacity = rpdat.arm_voxelgi_refraction
    if parse_opacity:
        frag.write('float opacity;')
    frag.write('float dotNV = 0.0;')
    cycles.parse(mat_state.nodes, con_voxel, vert, frag, geom, tesc, tese, parse_opacity=parse_opacity, parse_displacement=False, basecol_only=True)

    # Voxelized particles
    # particle = mat_state.material.arm_particle
    # if particle == 'gpu':
        # make_particle.write(vert, particle_info=cycles.particle_info)

    if not frag.contains('vec3 n ='):
        frag.write_pre = True
        frag.write('vec3 n;')
        frag.write_pre = False

    export_mpos = frag.contains('mposition') and not frag.contains('vec3 mposition')
    if export_mpos:
        vert.add_out('vec3 mpositionGeom')
        vert.write_pre = True
        vert.write('mpositionGeom = pos;')
        vert.write_pre = False

    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_uniform('mat3 N', '_normalMatrix')

    vert.add_out('vec3 voxpositionGeom')
    vert.add_out('vec3 wnormalGeom')

    vert.add_include('../../Shaders/compiled.glsl')

    if con_voxel.is_elem('col'):
        vert.add_out('vec3 vcolorGeom')
        vert.write('vcolorGeom = col;')

    if con_voxel.is_elem('tex'):
        vert.add_out('vec2 texCoordGeom')
        vert.write('texCoordGeom = tex;')

    if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
        vert.add_uniform('vec3 eyeSnap', '_cameraPositionSnap')
        vert.write('voxpositionGeom = (vec3(W * vec4(pos, 1.0)) - eyeSnap) / voxelgiHalfExtents;')
    else: 
        vert.write('voxpositionGeom = vec3(W * vec4(pos, 1.0)) / voxelgiHalfExtents;')
    vert.write('wnormalGeom = normalize(N * nor);')
    # vert.write('gl_Position = vec4(0.0, 0.0, 0.0, 1.0);')

    if is_shadows:
        vert.add_out('vec4 lampPosGeom')
        vert.add_uniform('mat4 LWVP', '_biasLampWorldViewProjectionMatrix')
        vert.write('lampPosGeom = LWVP * vec4(pos, 1.0);')

    geom.add_out('vec3 voxposition')
    geom.add_out('vec3 wnormal')
    if is_shadows:
        geom.add_out('vec4 lampPos')
    if con_voxel.is_elem('col'):
        geom.add_out('vec3 vcolor')
    if con_voxel.is_elem('tex'):
        geom.add_out('vec2 texCoord')
    if export_mpos:
        geom.add_out('vec3 mposition')

    geom.write('const vec3 p1 = voxpositionGeom[1] - voxpositionGeom[0];')
    geom.write('const vec3 p2 = voxpositionGeom[2] - voxpositionGeom[0];')
    geom.write('const vec3 p = abs(cross(p1, p2));')
    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    voxposition = voxpositionGeom[i];')
    geom.write('    wnormal = wnormalGeom[i];')
    if is_shadows:
        geom.write('    lampPos = lampPosGeom[i];')
    if con_voxel.is_elem('col'):
        geom.write('    vcolor = vcolorGeom[i];')
    if con_voxel.is_elem('tex'):
        geom.write('    texCoord = texCoordGeom[i];')
    if export_mpos:
        geom.write('    mposition = mpositionGeom[i];')
    geom.write('    if (p.z > p.x && p.z > p.y) {')
    geom.write('        gl_Position = vec4(voxposition.x, voxposition.y, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else if (p.x > p.y && p.x > p.z) {')
    geom.write('        gl_Position = vec4(voxposition.y, voxposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else {')
    geom.write('        gl_Position = vec4(voxposition.x, voxposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    EmitVertex();')
    geom.write('}')
    geom.write('EndPrimitive();')

    if cycles.emission_found:
        frag.write('vec3 color = basecol;')
    else:
        frag.write('vec3 color = basecol * visibility * lightColor * dotNL;')
    frag.write('vec3 voxel = voxposition * 0.5 + 0.5;')

    if rpdat.arm_voxelgi_emission:
        frag.write('color = min(color * 0.9, vec3(0.9)) + min(color / 200.0, 0.1);') # Higher range to allow emission

    frag.write('color = clamp(color, vec3(0.0), vec3(1.0));')

    if rpdat.rp_voxelgi_hdr:
        frag.write('imageStore(voxels, ivec3(voxelgiResolution * voxel), vec4(color, 1.0));')
    else:
        frag.write('uint val = convVec4ToRGBA8(vec4(color, 1.0) * 255);')
        frag.write('imageAtomicMax(voxels, ivec3(voxelgiResolution * voxel), val);')
        
        # frag.write('imageStore(voxels, ivec3(voxelgiResolution * voxel), vec4(color, 1.0));')
        # frag.write('imageAtomicRGBA8Avg(voxels, ivec3(voxelgiResolution * voxel), vec4(color, 1.0));')
            
        # frag.write('ivec3 coords = ivec3(voxelgiResolution * voxel);')
        # if parse_opacity:
        #     frag.write('vec4 val = vec4(color, opacity);')
        # else:
        #     frag.write('vec4 val = vec4(color, 1.0);')
        # frag.write('val *= 255.0;')
        # frag.write('uint newVal = encUnsignedNibble(convVec4ToRGBA8(val), 1);')
        # frag.write('uint prevStoredVal = 0;')
        # frag.write('uint currStoredVal;')
        # # frag.write('int counter = 0;')
        # # frag.write('while ((currStoredVal = imageAtomicCompSwap(voxels, coords, prevStoredVal, newVal)) != prevStoredVal && counter < 16) {')
        # frag.write('while ((currStoredVal = imageAtomicCompSwap(voxels, coords, prevStoredVal, newVal)) != prevStoredVal) {')
        # frag.write('    vec4 rval = convRGBA8ToVec4(currStoredVal & 0xFEFEFEFE);')
        # frag.write('    uint n = decUnsignedNibble(currStoredVal);')
        # frag.write('    rval = rval * n + val;')
        # frag.write('    rval /= ++n;')
        # frag.write('    rval = round(rval / 2) * 2;')
        # frag.write('    newVal = encUnsignedNibble(convVec4ToRGBA8(rval), n);')
        # frag.write('    prevStoredVal = currStoredVal;')
        # # frag.write('    counter++;')
        # frag.write('}')

        # frag.write('val.rgb *= 255.0f;')
        # frag.write('uint newVal = convVec4ToRGBA8(val);')
        # frag.write('uint prevStoredVal = 0;')
        # frag.write('uint curStoredVal;')
        # frag.write('while ((curStoredVal = imageAtomicCompSwap(voxels, coords, prevStoredVal, newVal)) != prevStoredVal) {')
        # frag.write('    prevStoredVal = curStoredVal;')
        # frag.write('    vec4 rval = convRGBA8ToVec4(curStoredVal);')
        # frag.write('    rval.xyz = (rval.xyz * rval.w);')
        # frag.write('    vec4 curValF = rval + val;')
        # frag.write('    curValF.xyz /= (curValF.w);')
        # frag.write('    newVal = convVec4ToRGBA8(curValF);')
        # frag.write('}')

    return con_voxel

def make_ao(context_id):
    con_voxel = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'always', 'cull_mode': 'none', 'color_write_red': False, 'color_write_green': False, 'color_write_blue': False, 'color_write_alpha': False, 'conservative_raster': True })
    wrd = bpy.data.worlds['Arm']

    vert = con_voxel.make_vert()
    frag = con_voxel.make_frag()
    geom = con_voxel.make_geom()
    tesc = None
    tese = None

    geom.ins = vert.outs
    frag.ins = geom.outs

    frag.add_include('../../Shaders/compiled.glsl')
    frag.add_include('../../Shaders/std/math.glsl')
    frag.add_include('../../Shaders/std/imageatomic.glsl')
    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')

    rpdat = arm.utils.get_rp()
    # frag.add_uniform('layout(r32ui) uimage3D voxels')
    frag.add_uniform('layout(r8) image3D voxels')
    frag.write('if (abs(voxposition.z) > ' + rpdat.rp_voxelgi_resolution_z + ' || abs(voxposition.x) > 1 || abs(voxposition.y) > 1) return;')

    vert.add_include('../../Shaders/compiled.glsl')
    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_out('vec3 voxpositionGeom')

    if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
        vert.add_uniform('vec3 eyeSnap', '_cameraPositionSnap')
        vert.write('voxpositionGeom = (vec3(W * vec4(pos, 1.0)) - eyeSnap) / voxelgiHalfExtents;')
    else: 
        vert.write('voxpositionGeom = vec3(W * vec4(pos, 1.0)) / voxelgiHalfExtents;')

    # vert.write('gl_Position = vec4(0.0, 0.0, 0.0, 1.0);')

    geom.add_out('vec3 voxposition')
    geom.write('const vec3 p1 = voxpositionGeom[1] - voxpositionGeom[0];')
    geom.write('const vec3 p2 = voxpositionGeom[2] - voxpositionGeom[0];')
    geom.write('const vec3 p = abs(cross(p1, p2));')
    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    voxposition = voxpositionGeom[i];')
    geom.write('    if (p.z > p.x && p.z > p.y) {')
    geom.write('        gl_Position = vec4(voxposition.x, voxposition.y, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else if (p.x > p.y && p.x > p.z) {')
    geom.write('        gl_Position = vec4(voxposition.y, voxposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else {')
    geom.write('        gl_Position = vec4(voxposition.x, voxposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    EmitVertex();')
    geom.write('}')
    geom.write('EndPrimitive();')

    frag.write('vec3 voxel = voxposition * 0.5 + vec3(0.5);')
    frag.write('imageStore(voxels, ivec3(voxelgiResolution * voxel), vec4(1.0));')

    return con_voxel
