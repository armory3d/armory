#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gbufferD;

uniform vec3 eye;
uniform vec3 eyeLook;

in vec3 viewRay;
in vec2 texCoord;

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

vec3 getPos(float depth) {	
    vec3 vray = normalize(viewRay);
	const float znear = 0.1;
	const float zfar = 1000.0;
	const float projectionA = zfar / (zfar - znear);
	const float projectionB = (-zfar * znear) / (zfar - znear);
	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
	float viewZDist = dot(eyeLook, vray);
	vec3 wposition = eye + vray * (linearDepth / viewZDist);
	return wposition;
}

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

void main() {
	discard;
		
	// n /= (abs(n.x) + abs(n.y) + abs(n.z));
    // n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);
	


	//Sample a value from the depth buffer
	// float4 sampledDepth = tex2D(depthSampler, texCoord);
	
	
	
	
	// objectPosition gives us a position inside (or not) of our 1x1x1 cube
	// centered at (0, 0, 0)
	// vec4 objectPosition = invW * worldPositionFromDepthBuffer;
	
	// Reject anything outside
	// if (0.5 - abs(objectPosition.xyz) < 0.0) {
		// discard;
	// }
	
	// Add 0.5 to get texture coordinates
	//float2 textureCoordinate = objectPosition.xz + 0.5;
	// vec2 decalTexCoord = objectPosition.xy + 0.5;
	// vec4 decalCol = texture(sdecalTex, decalTexCoord);
	
	// gl_FragColor = decalCol;
}
