#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gmap;

uniform float u1;
uniform float u2;
uniform float u3;
uniform float u4;
uniform float u5;
uniform float u6;

in vec2 texCoord;

vec3 rand(vec2 coord) {
	float noiseX = fract(sin(dot(coord, vec2(12.9898,78.233))) * 43758.5453) * 2.0 - 1.0;
	float noiseY = fract(sin(dot(coord, vec2(12.9898,78.233)*2.0)) * 43758.5453) * 2.0 - 1.0;
	float noiseZ = fract(sin(dot(coord, vec2(12.9898,78.233)*3.0)) * 43758.5453) * 2.0 - 1.0;
	return vec3(noiseX, noiseY, noiseZ) * 0.001;
}

vec3 normalFromDepth(float depth, vec2 texcoords) {
	const vec2 offset1 = vec2(0.0, 0.001);
	const vec2 offset2 = vec2(0.001, 0.0);

	float depth1 = texture(gmap, texcoords + offset1).r * 2.0 - 1.0;
	float depth2 = texture(gmap, texcoords + offset2).r * 2.0 - 1.0;

	vec3 p1 = vec3(offset1, depth1 - depth);
	vec3 p2 = vec3(offset2, depth2 - depth);

	vec3 normal = cross(p1, p2);
	normal.z = -normal.z;

	return normalize(normal);
}

// vec3 ndc_to_view(vec2 ndc, float depth, vec2 clipPlanes, vec2 tanFov) {
// 	float z = depth * clipPlanes.x + clipPlanes.y; // go from [0,1] to [zNear, zFar]
// 	return vec3(ndc * tanFov, -1.0) * z; // view space position
// }

// vec2 view_to_ndc(vec3 view, vec2 clipPlanes, vec2 tanFov) {
// 	return -view.xy / (tanFov*view.z);
// }

void main() {
	const float zn = 1.0;
	const float zf = 100.0;
	// float zscale = 0.8;
	// float total_strength = 1.0;
	// float base = 0.15;
	// float area = 0.05 * zscale;
	// float falloff = 0.002 * zscale;
	// float radius = 0.01 * zscale;
	float zscale = u1;
	float total_strength = u2;
	float base = u3;
	float area = u4;
	float falloff = u5 * zscale;
	float radius = u6 * zscale;
	
	const int samples = 16;
	vec3 sample_sphere[samples];
	sample_sphere[0] = vec3( 0.5381, 0.1856,-0.4319);
	sample_sphere[1] = vec3( 0.1379, 0.2486, 0.4430);
	sample_sphere[2] = vec3( 0.3371, 0.5679,-0.0057);
	sample_sphere[3] = vec3(-0.6999,-0.0451,-0.0019);
	sample_sphere[4] = vec3( 0.0689,-0.1598,-0.8547);
	sample_sphere[5] = vec3( 0.0560, 0.0069,-0.1843);
	sample_sphere[6] = vec3(-0.0146, 0.1402, 0.0762);
	sample_sphere[7] = vec3( 0.0100,-0.1924,-0.0344);
	sample_sphere[8] = vec3(-0.3577,-0.5301,-0.4358);
	sample_sphere[9] = vec3(-0.3169, 0.1063, 0.0158);
	sample_sphere[10] = vec3( 0.0103,-0.5869, 0.0046);
	sample_sphere[11] = vec3(-0.0897,-0.4940, 0.3287);
	sample_sphere[12] = vec3( 0.7119,-0.0154,-0.0918);
	sample_sphere[13] = vec3(-0.0533, 0.0596,-0.5411);
	sample_sphere[14] = vec3( 0.0352,-0.0631, 0.5460);
	sample_sphere[15] = vec3(-0.4776, 0.2847,-0.0271);
	
 	vec3 rvec = normalize(rand(texCoord)) * 0.4;
	float depth = texture(gmap, texCoord).r * 2.0 - 1.0;
	vec3 normal = normalFromDepth(depth, texCoord);
	vec3 position = vec3(texCoord, depth);
	
	float radius_depth = radius / (depth);
	float occlusion = 0.0;
	for (int i = 0; i < samples; ++i) {
		vec3 ray = radius_depth * reflect(sample_sphere[i], rvec);
		vec3 hemi_ray = position + sign(dot(ray,normal)) * ray;
		float occ_depth = texture(gmap, clamp(hemi_ray.xy, 0.0, 1.0)).r * 2.0 - 1.0;
		float difference = depth - occ_depth;
		occlusion += step(falloff, difference) * (1.0 - smoothstep(falloff, area, difference));
	}

	float ao = 1.0 - total_strength * occlusion * (1.0 / samples);
  	float aocol = clamp(ao + base, 0.0, 1.0);
	gl_FragColor = vec4(aocol, 0.0, 0.0, 1.0);
	
	// vec2 uTanFovs = vec2(0.83632286848, 0.41398034288);
	// float uRadius = 100;
	// float uGiBoost = 1.0;
	// int uSampleCnt = 16;
	// vec2 uClipZ = vec2(0.1, 100.0);
	// const float ATTF = 1e-5;
	// vec3 p = ndc_to_view(texCoord*2.0-1.0, depth, uClipZ, uTanFovs); // get view pos
	// float occ = 0.0;
	// float occCnt = 0.0;
	// for(int i=0; i<uSampleCnt && depth < 1.0; ++i) {
	// 	vec3 dir = reflect(sample_sphere[i].xyz, rvec); // a la Crysis
	// 	dir -= 2.0*dir*step(dot(normal,dir),0.0);      // a la Starcraft
	// 	vec3 sp = p + (dir * uRadius) * (depth * 1e2); // scale radius with depth
	// 	vec2 spNdc = view_to_ndc(sp, uClipZ, uTanFovs); // get sample ndc coords
	// 	float spNd = (texture(gmap, (spNdc*0.5 + 0.5)).r - 0.5) * 2.0;
	// 	vec3 occEye = -sp/sp.z*(spNd*uClipZ.x+uClipZ.y); // compute correct pos
	// 	vec3 occVec = occEye - p; // vector
	// 	float att2 = 1.0+ATTF*length(occVec); // quadratic attenuation
	// 	occ += max(0.0,dot(normalize(occVec),normal)-0.25) / (att2*att2);
	// 	++occCnt;
	// }
	// vec3 vocc = occCnt > 0.0 ? vec3(1.0-occ*uGiBoost/occCnt) : vec3(1.0);
	// gl_FragColor = vec4(vocc, 1.0);
}
