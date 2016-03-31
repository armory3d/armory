// SSR based on implementation by Ben Hopkins
// Work in progress
#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform sampler2D gbuffer0; // Normal, depth
uniform sampler2D gbuffer1; // Position, roughness
uniform sampler2D gbuffer2;
uniform mat4 P;
uniform mat4 invP;
uniform mat4 V;
uniform vec3 eye;

in vec2 texCoord;
in vec3 cameraRay;

vec3 ScreenSpaceToViewSpace(vec3 cameraRay, float depth) {
	return (cameraRay * depth);
}

// void swapIfBigger(inout float aa, inout float bb) {
// 	if( aa > bb) {
// 		float tmp = aa;
// 		aa = bb;
// 		bb = tmp;
// 	}
// }

// Projection params: x is 1.0 (or –1.0 if currently rendering with a flipped projection matrix), y is the camera’s near plane, z is the camera’s far plane and w is 1/FarPlane.

// Linear01Depth: Z buffer to linear 0..1 depth (0 at eye, 1 at far plane) inline float Linear01Depth( float z ) {  } // Z buffer to linear depth inline float
float Linear01Depth(float z) {
	// return 1.0 / (_ZBufferParams.x * z + _ZBufferParams.y);
	return z;
	// x = 1 - 100/0.1 = -999
	// y = 100/0.1 = 1000
	// 1 / (-999 * 200 + 1000)
}

// double zc0, zc1;
// // OpenGL would be this:
// // zc0 = (1.0 - m_FarClip / m_NearClip) / 2.0;
// // zc1 = (1.0 + m_FarClip / m_NearClip) / 2.0;
// // D3D is this:
// zc0 = 1.0 - m_FarClip / m_NearClip;
// zc1 = m_FarClip / m_NearClip;
// // now set _ZBufferParams with (zc0, zc1, zc0/m_FarClip, zc1/m_FarClip);

    // // Values used to linearize the Z buffer (http://www.humus.name/temp/Linearize%20depth.txt)
    // // x = 1-far/near
    // // y = far/near
    // // z = x/far
    // // w = y/far
    // uniform float4 _ZBufferParams; 

bool rayIntersectsDepthBF(float zA, float zB, vec2 uv) {
	// vec4 uv4 = vec4(uv, 0.0, 0.0);
	vec2 uv4 = uv;
	float cameraZ = Linear01Depth(texture(gbuffer0, uv4).a) * - 100.0;//_ProjectionParams.z;	
	float backZ = texture(_BackFaceDepthTex, uv4).r * - 100;//_ProjectionParams.z;
	
	return zB <= cameraZ && zA >= backZ - _PixelZSize;
}

float distanceSquared( vec2 a, vec2 b) { a -= b; return dot(a, a); }


// Trace a ray in screenspace from rayOrigin (in camera space) pointing in rayDirection (in camera space)
// using jitter to offset the ray based on (jitter * _PixelStride).
//
// Returns true if the ray hits a pixel in the depth buffer
// and outputs the hitPixel (in UV space), the hitPoint (in camera space) and the number
// of iterations it took to get there.
bool traceScreenSpaceRay( vec3 rayOrigin, 
									vec3 rayDirection, 
									float jitter, 
									out vec2 hitPixel, 
									out vec3 hitPoint, 
									out float iterationCount, bool debugHalf) {
	// Clip to the near plane    
	float rayLength = ((rayOrigin.z + rayDirection.z * _MaxRayDistance) > -_ProjectionParams.y) ?
						(-_ProjectionParams.y - rayOrigin.z) / rayDirection.z : _MaxRayDistance;
	vec3 rayEnd = rayOrigin + rayDirection * rayLength;
	
	// Project into homogeneous clip space
	vec4 H0 = P * vec4( rayOrigin, 1.0);
	vec4 H1 = P * vec4( rayEnd, 1.0);
	
	float k0 = 1.0 / H0.w, k1 = 1.0 / H1.w;
	
	// The interpolated homogeneous version of the camera-space points  
	vec3 Q0 = rayOrigin * k0, Q1 = rayEnd * k1;
	
	// Screen-space endpoints
	vec2 P0 = H0.xy * k0, P1 = H1.xy * k1;
	
	// If the line is degenerate, make it cover at least one pixel
	// to avoid handling zero-pixel extent as a special case later
	P1 += (distanceSquared(P0, P1) < 0.0001) ? 0.01 : 0.0;
	
	vec2 delta = P1 - P0;
	
	// Permute so that the primary iteration is in x to collapse
	// all quadrant-specific DDA cases later
	bool permute = false;
	if (abs(delta.x) < abs(delta.y)) { 
		// This is a more-vertical line
		permute = true; delta = delta.yx; P0 = P0.yx; P1 = P1.yx; 
	}
	
	float stepDir = sign(delta.x);
	float invdx = stepDir / delta.x;
	
	// Track the derivatives of Q and k
	vec3  dQ = (Q1 - Q0) * invdx;
	float dk = (k1 - k0) * invdx;
	vec2  dP = vec2(stepDir, delta.y * invdx);
	
	// Calculate pixel stride based on distance of ray origin from camera.
	// Since perspective means distant objects will be smaller in screen space
	// we can use this to have higher quality reflections for far away objects
	// while still using a large pixel stride for near objects (and increase performance)
	// this also helps mitigate artifacts on distant reflections when we use a large
	// pixel stride.
	float strideScaler = 1.0 - min( 1.0, -rayOrigin.z / _PixelStrideZCuttoff);
	float pixelStride = 1.0 + strideScaler * _PixelStride;
	
	// Scale derivatives by the desired pixel stride and then
	// offset the starting values by the jitter fraction
	dP *= pixelStride; dQ *= pixelStride; dk *= pixelStride;
	P0 += dP * jitter; Q0 += dQ * jitter; k0 += dk * jitter;
	
	float i, zA = 0.0, zB = 0.0;
	
	// Track ray step and derivatives in a float4 to parallelize
	float4 pqk = float4( P0, Q0.z, k0);
	float4 dPQK = float4( dP, dQ.z, dk);
	bool intersect = false;
	
	for( i=0; i<_Iterations && intersect == false; i++) {
		pqk += dPQK;
		
		zA = zB;
		zB = (dPQK.z * 0.5 + pqk.z) / (dPQK.w * 0.5 + pqk.w);
		swapIfBigger( zB, zA);
		
		hitPixel = permute ? pqk.yx : pqk.xy;
		hitPixel *= _OneDividedByRenderBufferSize;
		
		intersect = rayIntersectsDepthBF( zA, zB, hitPixel);
	}
	
	// Binary search refinement
	if( pixelStride > 1.0 && intersect) {
		pqk -= dPQK;
		dPQK /= pixelStride;
		
		float originalStride = pixelStride * 0.5;
		float stride = originalStride;
		
		zA = pqk.z / pqk.w;
		zB = zA;
		
		for( float j=0; j<_BinarySearchIterations; j++)
		{
			pqk += dPQK * stride;
			
			zA = zB;
			zB = (dPQK.z * -0.5 + pqk.z) / (dPQK.w * -0.5 + pqk.w);
			swapIfBigger( zB, zA);
			
			hitPixel = permute ? pqk.yx : pqk.xy;
			hitPixel *= _OneDividedByRenderBufferSize;
			
			originalStride *= 0.5;
			stride = rayIntersectsDepthBF( zA, zB, hitPixel) ? -originalStride : originalStride;
		}
	}

	
	Q0.xy += dQ.xy * i;
	Q0.z = pqk.z;
	hitPoint = Q0 / pqk.w;
	iterationCount = i;
			
	return intersect;
}

float calculateAlphaForIntersection( bool intersect, 
											float iterationCount, 
											float specularStrength,
											vec2 hitPixel,
											vec3 hitPoint,
											vec3 vsRayOrigin,
											vec3 vsRayDirection) {
	float alpha = min( 1.0, specularStrength * 1.0);
	
	// Fade ray hits that approach the maximum iterations
	alpha *= 1.0 - (iterationCount / _Iterations);
	
	// Fade ray hits that approach the screen edge
	float screenFade = _ScreenEdgeFadeStart;
	vec2 hitPixelNDC = (hitPixel * 2.0 - 1.0);
	float maxDimension = min( 1.0, max( abs( hitPixelNDC.x), abs( hitPixelNDC.y)));
	alpha *= 1.0 - (max( 0.0, maxDimension - screenFade) / (1.0 - screenFade));
	
	// Fade ray hits base on how much they face the camera
	float eyeFadeStart = _EyeFadeStart;
	float eyeFadeEnd = _EyeFadeEnd;
	swapIfBigger( eyeFadeStart, eyeFadeEnd);
	
	float eyeDirection = clamp( vsRayDirection.z, eyeFadeStart, eyeFadeEnd);
	alpha *= 1.0 - ((eyeDirection - eyeFadeStart) / (eyeFadeEnd - eyeFadeStart));
	
	// Fade ray hits based on distance from ray origin
	alpha *= 1.0 - clamp( distance( vsRayOrigin, hitPoint) / _MaxRayDistance, 0.0, 1.0);
	
	alpha *= intersect;
	
	return alpha;
}



void main() {
	
	vec4 specRoughPixel = texture(_CameraGBufferTexture1, texCoord);
	vec3 specularStrength = specRoughPixel.a;
	
	float decodedDepth = Linear01Depth(texture(_CameraDepthTexture, texCoord).r);
	
	vec3 vsRayOrigin = ScreenSpaceToViewSpace(cameraRay, decodedDepth);
	
	vec3 decodedNormal = (texture( _CameraGBufferTexture2, texCoord)).rgb * 2.0 - 1.0;
	decodedNormal = mul( (mat3)_NormalMatrix, decodedNormal);
	
	vec3 vsRayDirection = normalize( reflect( normalize( vsRayOrigin), normalize(decodedNormal)));
	
	vec2 hitPixel; 
	vec3 hitPoint;
	float iterationCount;
	
	vec2 uv2 = texCoord * _RenderBufferSize;
	float c = (uv2.x + uv2.y) * 0.25;
	float jitter = fmod( c, 1.0);

	bool intersect = traceScreenSpaceRay( vsRayOrigin, vsRayDirection, jitter, hitPixel, hitPoint, iterationCount, texCoord.x > 0.5);
	float alpha = calculateAlphaForIntersection( intersect, iterationCount, specularStrength, hitPixel, hitPoint, vsRayOrigin, vsRayDirection);
	hitPixel = lerp( texCoord, hitPixel, intersect);
	
	// Comment out the line below to get faked specular,
	// in no way physically correct but will tint based
	// on spec. Physically correct handling of spec is coming...
	specRoughPixel = vec4( 1.0, 1.0, 1.0, 1.0);
	
	return vec4( (texture( _MainTex, hitPixel)).rgb * specRoughPixel.rgb, alpha);
	
	// vec4 texColor = texture(tex, texCoord);
	// gl_FragColor = texColor * (1.0 - intensity) + reflCol * intensity;
}
