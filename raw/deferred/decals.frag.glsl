#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gbufferD;
#ifdef _AMTex
uniform sampler2D salbedo;
#endif
#ifdef _NMTex
uniform sampler2D snormal;
#endif

uniform mat4 invVP;
uniform mat4 invM;
uniform mat4 V;

in vec4 mvpposition;
in vec4 mposition;
in vec4 matColor;

mat3 cotangentFrame(vec3 nor, vec3 pos, vec2 uv) {
    // Get edge vectors of the pixel triangle
    vec3 dp1 = dFdx(pos);
    vec3 dp2 = dFdy(pos);
    vec2 duv1 = dFdx(uv);
    vec2 duv2 = dFdy(uv);
    // Solve the linear system
    vec3 dp2perp = cross(dp2, nor);
    vec3 dp1perp = cross(nor, dp1);
    vec3 T = dp2perp * duv1.x + dp1perp * duv2.x;
    vec3 B = dp2perp * duv1.y + dp1perp * duv2.y;
    // Construct a scale-invariant frame 
    float invmax = inversesqrt(max(dot(T,T), dot(B,B)));
    return mat3(T * invmax, B * invmax, nor);
}

// vec3 getPos(float depth) {	
//     vec3 vray = normalize(viewRay);
// 	const float znear = 0.1;
// 	const float zfar = 1000.0;
// 	const float projectionA = zfar / (zfar - znear);
// 	const float projectionB = (-zfar * znear) / (zfar - znear);
// 	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
// 	float viewZDist = dot(eyeLook, vray);
// 	vec3 wposition = eye + vray * (linearDepth / viewZDist);
// 	return wposition;
// }

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

vec4 reconstructPos(float z, vec2 uv_f) {
    vec4 sPos = vec4(uv_f * 2.0 - 1.0, z, 1.0);
    sPos = invVP * sPos;
    return vec4((sPos.xyz / sPos.w), sPos.w);
}

void main() {
	vec2 screenPosition = mvpposition.xy / mvpposition.w;
	vec2 depthUV = screenPosition * 0.5 + 0.5;
	const vec2 resoluion = vec2(800.0, 600.0);
    depthUV += vec2(0.5 / resoluion); // Half pixel offset
    float depth = texture(gbufferD, depthUV).r * 2.0 - 1.0;

	vec4 worldPos = reconstructPos(depth, depthUV);
	worldPos.w = 1.0;
    vec4 localPos = invM * worldPos;
	localPos.y *= -1.0;

	if (abs(localPos.x) > 1.0) discard;
	if (abs(localPos.y) > 1.0) discard;
	if (abs(localPos.z) > 1.0) discard;

	vec2 uv = (localPos.xy / 2.0) - 0.5; // / 2.0 - adjust decal box size 
	vec4 baseColor = texture(salbedo, uv) * matColor;
	// Alpha write is disabled in shader res, we acces all channels for blending
	gl_FragData[1] = baseColor;
	
	
	
	
	// n /= (abs(n.x) + abs(n.y) + abs(n.z));
    // n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);
	
	
	/*
	vec3 ddxWp = dFdx(worldPos);
	vec3 ddyWp = dFdy(worldPos);
	vec3 normal = normalize(cross(ddyWp, ddxWp));
	
	// Get values across and along the surface
	vec3 ddxWp = dFdx(worldPos);
	vec3 ddyWp = dFdy(worldPos);

	// Determine the normal
	vec3 normal = normalize(cross(ddyWp, ddxWp));

	// Normalizing things is cool
	binormal = normalize(ddxWp);
	tangent = normalize(ddyWp);

	// Create a matrix transforming from tangent space to view space
	mat3 tangentToView;
	tangentToView[0] = V * pixelTangent;
	tangentToView[1] = V * pixelBinormal;
	tangentToView[2] = V * pixelNormal;

	// Transform normal from tangent space into view space
	normal = tangentToView * normal;
	*/
}
