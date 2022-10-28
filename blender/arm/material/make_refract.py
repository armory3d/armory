import bpy

import arm
import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.make_mesh as make_mesh
import arm.material.make_finalize as make_finalize
import arm.material.ray_marching_glsl as ray_marching_glsl
import arm.assets as assets

if arm.is_reload(__name__):
    cycles = arm.reload_module(cycles)
    mat_state = arm.reload_module(mat_state)
    make_mesh = arm.reload_module(make_mesh)
    make_finalize = arm.reload_module(make_finalize)
    assets = arm.reload_module(assets)
else:
    arm.enable_reload(__name__)


def make(context_id, rpasses):
    wrd = bpy.data.worlds['Arm']
    
    con_refract = make_mesh.make(context_id, rpasses)

    vert = con_refract.vert
    frag = con_refract.frag
    tese = con_refract.tese

   
    frag.add_include('compiled.inc')
    frag.add_include('std/math.glsl')
    frag.add_include('std/gbuffer.glsl')

    frag.add_uniform('sampler2D tex')
    frag.add_uniform('sampler2D gbufferD')

    vert.add_uniform('mat4 P', link='_projectionMatrix')
    vert.add_uniform('vec2 cameraProj', link='_cameraPlaneProj')
    vert.add_uniform('mat3 V3', link='_viewMatrix3')
    vert.add_uniform('vec3 eye', link='_cameraPosition')
    vert.add_uniform('vec3 eyeLook', link='_cameraLook')
    
    frag.add_uniform('mat4 P', link='_projectionMatrix')
    frag.add_uniform('vec2 cameraProj', link='_cameraPlaneProj')
    frag.add_uniform('mat3 V3', link='_viewMatrix3')
    frag.add_uniform('vec3 eye', link='_cameraPosition')
    frag.add_uniform('vec3 eyeLook', link='_cameraLook')

    frag.add_in('vec3 viewRay')
    frag.add_in('vec2 texCoord')
    if not '_Deferred' in wrd.world_defs:
        frag.add_out('vec4 fragColor')

    frag.write_header('vec3 hitCoord;')

    frag.add_const('int', 'numBinarySearchSteps', '7')
    frag.add_const('int' ,'maxSteps', '128')

    frag.add_function(ray_marching_glsl.get_projected_coord)
    frag.add_function(ray_marching_glsl.get_delta_depth)
    frag.add_function(ray_marching_glsl.binary_search)
    frag.add_function(ray_marching_glsl.raycast)

    frag.write('float d = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;')
    if not '_Deferred' in wrd.world_defs:
        frag.write('if (d < 0.0) { fragColor = vec4(0.0); return; }')
    else:
        frag.write('if (d < 0.0) { fragColor[2] = vec4(0.0); return; }')
    frag.write('vec3 vray = normalize(viewRay);')
    frag.write('vec3 viewPos = getPosView(viewRay, d, cameraProj);')
    frag.write('vec3 viewNormal = n * V3;')
    frag.write('vec3 refracted = normalize(refract(viewPos, viewNormal, rior));')
    frag.write('hitCoord = viewPos;')
    frag.write('vec3 dir = refracted * (1.0 - rand(texCoord) * ss_refractionJitter * roughness) * 2.0;')
    frag.write('vec4 coords = rayCast(dir);')
    frag.write('vec3 refractCol = textureLod(tex, coords.xy, 0.0).rgb;')
    frag.write('vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);')
    frag.write('float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);')
    frag.write('float reflectivity = 1.0 - roughness;')
    frag.write('float intensity = pow(reflectivity, ss_refractionFalloffExp) * screenEdgeFactor * clamp(-refracted.z, 0.0, 1.0) * clamp((ss_refractionSearchDist - length(viewPos - hitCoord)) * (1.0 / ss_refractionSearchDist), 0.0, 1.0) * coords.w;')
   
    if not '_Deferred' in wrd.world_defs:
        frag.write('fragColor = mix(textureLod(tex, texCoord, 0.0), vec4(refractCol, intensity), intensity);')
    else:
        frag.write('fragColor[2] = mix(textureLod(tex, texCoord, 0.0), vec4(refractCol, intensity), intensity);')

    make_finalize.make(con_refract)
	# assets.vs_equal(con_transluc, assets.shader_cons['transluc_vert']) # shader_cons has no transluc yet
    # assets.fs_equal(con_transluc, assets.shader_cons['transluc_frag'])

    return con_refract
