#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform sampler2D gbuffer0; // Normal, depth
uniform sampler2D gbuffer1; // Position, roughness
uniform sampler2D gbuffer2;
uniform mat4 P;
uniform mat4 V;

const float rayStep = 0.25;
const float minRayStep = 0.1;
const float maxSteps = 20;
const float searchDist = 5;
const float searchDistInv = 0.2;
const int numBinarySearchSteps = 5;
const float maxDDepth = 1.0;
const float maxDDepthInv = 1.0;
const float reflectionSpecularFalloffExponent = 3.0;

in vec2 texCoord;

vec3 hitCoord;
float dDepth;

vec3 binarySearch(vec3 dir) {
    float depth;
	vec4 projectedCoord;
	
    // for (int i = 0; i < numBinarySearchSteps; i++) {
        projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth > 0.0) {
            hitCoord += dir;
		}
        dir *= 0.5;
        hitCoord -= dir;
		
		projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth > 0.0) {
            hitCoord += dir;
		}
        dir *= 0.5;
        hitCoord -= dir;
		
		projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth > 0.0) {
            hitCoord += dir;
		}
        dir *= 0.5;
        hitCoord -= dir;
		
		projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth > 0.0) {
            hitCoord += dir;
		}
        dir *= 0.5;
        hitCoord -= dir;
		
		projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth > 0.0) {
            hitCoord += dir;
		}
        dir *= 0.5;
        hitCoord -= dir;
    // }

    projectedCoord = P * vec4(hitCoord, 1.0); 
    projectedCoord.xy /= projectedCoord.w;
    projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
    return vec3(projectedCoord.xy, depth);
}

vec4 rayCast(vec3 dir) {
    dir *= rayStep;
    float depth;
	
    // for (int i = 0; i < maxSteps; i++) {
        hitCoord += dir;
        vec4 projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth < 0.0) {
            return vec4(binarySearch(dir), 1.0);
		}
		
		hitCoord += dir;
        projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth < 0.0) {
            return vec4(binarySearch(dir), 1.0);
		}
		
		hitCoord += dir;
        projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth < 0.0) {
            return vec4(binarySearch(dir), 1.0);
		}
		
		hitCoord += dir;
        projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth < 0.0) {
            return vec4(binarySearch(dir), 1.0);
		}
		
		hitCoord += dir;
        projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth < 0.0) {
            return vec4(binarySearch(dir), 1.0);
		}
		
		hitCoord += dir;
        projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth < 0.0) {
            return vec4(binarySearch(dir), 1.0);
		}
		
		hitCoord += dir;
        projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth < 0.0) {
            return vec4(binarySearch(dir), 1.0);
		}
		
		hitCoord += dir;
        projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth < 0.0) {
            return vec4(binarySearch(dir), 1.0);
		}
		
		hitCoord += dir;
        projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth < 0.0) {
            return vec4(binarySearch(dir), 1.0);
		}
		
		hitCoord += dir;
        projectedCoord = P * vec4(hitCoord, 1.0);
        projectedCoord.xy /= projectedCoord.w;
        projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
        depth = texture(gbuffer0, projectedCoord.xy).a;
        dDepth = hitCoord.z - depth;
        if (dDepth < 0.0) {
            return vec4(binarySearch(dir), 1.0);
		}
    // }
	
    return vec4(0.0, 0.0, 0.0, 0.0);
}

void main() {
	// vec2 gTexCoord = gl_FragCoord.xy * gTexSizeInv;
    // Samples
    float roughness = texture(gbuffer1, texCoord).a;
	float specular = 1.0 - roughness;
    if (specular == 0.0) {
		vec4 texColor = texture(tex, texCoord);
        gl_FragColor = texColor;
        // gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
        return;
    }

    vec4 viewNormal = vec4(texture(gbuffer0, texCoord).rgb, 1.0);
	viewNormal = V * viewNormal;
	viewNormal /= viewNormal.w;
	
    vec4 viewPos = vec4(texture(gbuffer1, texCoord).rgb, 1.0);
	viewPos = V * viewPos;
	viewPos /= viewPos.w;

    // Reflection vector
    vec3 reflected = normalize(reflect(normalize(viewPos.xyz), normalize(viewNormal.xyz)));

    // Ray cast
    hitCoord = viewPos.xyz;
    dDepth = 0.0;
	
    vec4 coords = rayCast(reflected * max(minRayStep, -viewPos.z));
    vec2 dCoords = abs(vec2(0.5, 0.5) - coords.xy);

    float screenEdgeFactor = clamp(1.0 - (dCoords.x + dCoords.y), 0.0, 1.0);

	float intensity = pow(specular, reflectionSpecularFalloffExponent) *
        screenEdgeFactor * clamp(-reflected.z, 0.0, 1.0) *
        clamp((searchDist - length(viewPos.xyz - hitCoord)) * searchDistInv, 0.0, 1.0) * coords.w;

    vec4 reflCol = vec4(texture(tex, coords.xy).rgb, 1.0);
	
	vec4 texColor = texture(tex, texCoord);
	gl_FragColor = texColor * (1.0 - intensity) + reflCol * intensity;
}
