#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gbufferD;
#ifdef _BaseTex
uniform sampler2D sbase;
#endif
#ifdef _NorTex
uniform sampler2D snormal;
#endif
#ifdef _RoughTex
uniform sampler2D srough;
#else
uniform float roughness;
#endif
#ifdef _MetTex
uniform sampler2D smetal;
#else
uniform float metalness;
#endif

// uniform vec2 screenSize;
uniform mat4 invVP;
uniform mat4 invW;
uniform mat4 V;

in vec4 wvpposition;
in vec4 matColor;
// in vec3 orientation;
out vec4[2] fragColor;

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

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

vec4 reconstructPos(float z, vec2 uv_f) {
    vec4 sPos = vec4(uv_f * 2.0 - 1.0, z, 1.0);
    sPos = invVP * sPos;
    return vec4((sPos.xyz / sPos.w), sPos.w);
}

float packFloat(float f1, float f2) {
	int index = int(f1 * 1000);
	float alpha = f2 == 0.0 ? f2 : (f2 - 0.0001);
	float result = index + alpha;
	return result;
}

void main() {
	vec2 screenPosition = wvpposition.xy / wvpposition.w;
	vec2 depthUV = screenPosition * 0.5 + 0.5;
    // depthUV += vec2(0.5 / screenSize); // Half pixel offset
    float depth = texture(gbufferD, depthUV).r * 2.0 - 1.0;

	vec4 worldPos = reconstructPos(depth, depthUV);
	worldPos.w = 1.0;
    
	// Angle reject
	// Reconstruct normal
	// vec3 dnor = normalize(cross(dFdx(worldPos.xyz), dFdy(worldPos.xyz)));
	// Get decal box orientation
	// vec3 orientation = vec3(1.0, 0.0, 0.0);
	// if (dot(dnor, orientation) < cos(3.1415)) discard;
	
	vec4 localPos = invW * worldPos;
	localPos.y *= -1.0;

	if (abs(localPos.x) > 1.0) discard;
	if (abs(localPos.y) > 1.0) discard;
	if (abs(localPos.z) > 1.0) discard;

	vec2 texCoord = (localPos.xy / 2.0) - 0.5; // / 2.0 - adjust decal box size 
	
#ifdef _BaseTex
	vec4 baseColor = texture(sbase, texCoord) * matColor;
#else
	vec4 baseColor = matColor;
#endif
	
	// Alpha write is disabled in shader res, we acces all channels for blending
	// Use separate texture for base color in the future
	fragColor[1].rgb = baseColor.rgb;
	fragColor[1].a = baseColor.a;
	// fragColor[1].a = packFloat(roughness, metalness) * baseColor.a;
	
#ifdef _MetTex
	float metalness = texture(smetal, texCoord).r;
#endif

#ifdef _RoughTex
	float roughness = texture(srough, texCoord).r;
#endif	
	
#ifdef _NorTex
	vec3 normal = texture(snormal, texCoord).rgb * 2.0 - 1.0;
	vec3 nn = normalize(normal);
    vec3 dp1 = dFdx(worldPos.xyz);
    vec3 dp2 = dFdy(worldPos.xyz);
    vec2 duv1 = dFdx(texCoord);
    vec2 duv2 = dFdy(texCoord);
    vec3 dp2perp = cross(dp2, nn);
    vec3 dp1perp = cross(nn, dp1);
    vec3 T = dp2perp * duv1.x + dp1perp * duv2.x;
    vec3 B = dp2perp * duv1.y + dp1perp * duv2.y; 
    float invmax = inversesqrt(max(dot(T,T), dot(B,B)));
    mat3 TBN = mat3(T * invmax, B * invmax, nn);
	vec3 n = normalize(TBN * nn);
	
	n /= (abs(n.x) + abs(n.y) + abs(n.z));
    n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);
	
	fragColor[0].rg = n.xy;
#else
	fragColor[0].rg = vec2(1.0);
#endif

	// fragColor[0].b unused for now so we can rewrite it
	fragColor[0].b = 0.0;
	// use separete RG texture for normal storage in the future
	// Color mask does not disable write for all buffers so mask is overwritten
	// Half of color alpha to soft normals blend
	fragColor[0].a = baseColor.a / 2.0;
}
