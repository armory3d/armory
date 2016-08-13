// DSSDO
// http://kayru.org/articles/dssdo/
#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform sampler2D snoise;
uniform mat4 invVP;
uniform vec3 eye;

const float PI = 3.1415926535;
const vec2 screenSize = vec2(800.0, 600.0);
const vec2 aspectRatio = vec2(min(1.0, screenSize.y / screenSize.x), min(1.0, screenSize.x / screenSize.y));

const int num_samples = 32;
const float g_occlusion_radius = 0.279710;
const float g_occlusion_max_distance = 0.639419;
const float fudge_factor_l0 = 2.0;
const float fudge_factor_l1 = 10.0;
const float sh2_weight_l0 = fudge_factor_l0 * 0.28209; //0.5*sqrt(1.0/pi);
const vec3 sh2_weight_l1 = vec3(fudge_factor_l1 * 0.48860); //0.5*sqrt(3.0/pi);
const vec4 sh2_weight = vec4(sh2_weight_l1, sh2_weight_l0) / num_samples;

in vec2 texCoord;
out vec4 outColor;

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}
vec3 getPos(float depth, vec2 coord) {	
    // vec4 pos = vec4(coord * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
    vec4 pos = vec4(coord * 2.0 - 1.0, depth, 1.0);
    pos = invVP * pos;
    pos.xyz /= pos.w;
    return pos.xyz - eye;
}

vec4 doDO(vec3 point, vec3 noise, float radius, vec3 center_pos, float max_distance_inv, vec3 center_normal) {
	vec2 textureOffset = reflect( point.xy, noise.xy ).xy * radius;
	vec2 sample_tex = texCoord + textureOffset;
	
	// float depth = 1.0 - texture(gbuffer0, sample_tex).a;
	float depth = texture(gbufferD, sample_tex).r * 2.0 - 1.0;
	vec3 sample_pos = getPos(depth, sample_tex);

	vec3 center_to_sample = sample_pos - center_pos;
	float dist = length(center_to_sample);
	vec3 center_to_sample_normalized = center_to_sample / dist;
	float attenuation = 1.0 - clamp(dist * max_distance_inv, 0.0, 1.0);
	float dp = dot(center_normal, center_to_sample_normalized);

	const float attenuation_angle_threshold = 0.1;
	attenuation = attenuation*attenuation * step(attenuation_angle_threshold, dp);

	return attenuation * sh2_weight * vec4(center_to_sample_normalized, 1.0);
}

void main() {
	// float depth = 1.0 - texture(gbuffer0, texCoord).a;
	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	// if (depth == 0.0) {
	if (depth == 1.0) {
		outColor = vec4(1.0);
		return;
	}
	
	vec3 points[num_samples];	
 	points[0] = vec3(-0.134, 0.044, -0.825);
	points[1] = vec3(0.045, -0.431, -0.529);
	points[2] = vec3(-0.537, 0.195, -0.371);
	points[3] = vec3(0.525, -0.397, 0.713);
	points[4] = vec3(0.895, 0.302, 0.139);
	points[5] = vec3(-0.613, -0.408, -0.141);
	points[6] = vec3(0.307, 0.822, 0.169);
	points[7] = vec3(-0.819, 0.037, -0.388);
	points[8] = vec3(0.376, 0.009, 0.193);
	points[9] = vec3(-0.006, -0.103, -0.035);
	points[10] = vec3(0.098, 0.393, 0.019);
	points[11] = vec3(0.542, -0.218, -0.593);
	points[12] = vec3(0.526, -0.183, 0.424);
	points[13] = vec3(-0.529, -0.178, 0.684);
	points[14] = vec3(0.066, -0.657, -0.570);
	points[15] = vec3(-0.214, 0.288, 0.188);
	points[16] = vec3(-0.689, -0.222, -0.192);
	points[17] = vec3(-0.008, -0.212, -0.721);
	points[18] = vec3(0.053, -0.863, 0.054);
	points[19] = vec3(0.639, -0.558, 0.289);
	points[20] = vec3(-0.255, 0.958, 0.099);
	points[21] = vec3(-0.488, 0.473, -0.381);
	points[22] = vec3(-0.592, -0.332, 0.137);
	points[23] = vec3(0.080, 0.756, -0.494);
	points[24] = vec3(-0.638, 0.319, 0.686);
	points[25] = vec3(-0.663, 0.230, -0.634);
	points[26] = vec3(0.235, -0.547, 0.664);
	points[27] = vec3(0.164, -0.710, 0.086);
	points[28] = vec3(-0.009, 0.493, -0.038);
	points[29] = vec3(-0.322, 0.147, -0.105);
	points[30] = vec3(-0.554, -0.725, 0.289);
	points[31] = vec3(0.534, 0.157, -0.250);
	
	vec2 enc = texture(gbuffer0, texCoord).rg;      
    vec3 currentNormal;
    currentNormal.z = 1.0 - abs(enc.x) - abs(enc.y);
    currentNormal.xy = currentNormal.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	currentNormal = normalize(currentNormal);
	
	vec3 currentPos = getPos(depth, texCoord);
	// float currentDistance = length(currentPos);
	
	
	vec2 noise_texture_size = vec2(8.0,8.0);
	vec3 center_pos = currentPos;
	vec3 eye_pos = eye;
	float center_depth = distance(eye_pos, center_pos);
	float radius = g_occlusion_radius / center_depth;
	float max_distance_inv = 1.0 / g_occlusion_max_distance;
	// float attenuation_angle_threshold = 0.1;
	
	vec3 noise = texture(snoise, (texCoord * screenSize) / noise_texture_size).xyz * 2.0 - 1.0;
	vec3 center_normal = currentNormal;
	
	vec4 occlusion_sh2 = vec4(0.0);
	
	// for( int i=0; i<num_samples; ++i ) {
		occlusion_sh2 += doDO(points[0], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[1], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[2], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[3], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[4], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[5], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[6], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[7], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[8], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[9], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[10], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[11], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[12], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[13], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[14], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[15], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[16], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[17], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[18], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[19], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[20], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[21], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[22], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[23], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[24], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[25], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[26], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[27], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[28], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[29], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[30], noise, radius, center_pos, max_distance_inv, center_normal);
		occlusion_sh2 += doDO(points[31], noise, radius, center_pos, max_distance_inv, center_normal);
	// }
	
    outColor = vec4(vec3(1.0 - occlusion_sh2.rgb), 1.0);
}
