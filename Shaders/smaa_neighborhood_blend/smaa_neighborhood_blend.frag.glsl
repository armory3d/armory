#version 450

#include "compiled.inc"

uniform sampler2D colorTex;
uniform sampler2D blendTex;
#ifdef _Veloc
uniform sampler2D sveloc;
#endif

uniform vec2 screenSizeInv;

in vec2 texCoord;
in vec4 offset;
out vec4 fragColor;

//-----------------------------------------------------------------------------
// Neighborhood Blending Pixel Shader (Third Pass)

// Conditional move:
// void SMAAMovc(bvec2 cond, inout vec2 variable, vec2 value) {
//    /*SMAA_FLATTEN*/ if (cond.x) variable.x = value.x;
//    /*SMAA_FLATTEN*/ if (cond.y) variable.y = value.y;
//}
//void SMAAMovc(bvec4 cond, inout vec4 variable, vec4 value) {
//    SMAAMovc(cond.xy, variable.xy, value.xy);
//    SMAAMovc(cond.zw, variable.zw, value.zw);
//}

vec4 SMAANeighborhoodBlendingPS(vec2 texcoord, vec4 offset/*, sampler2D colorTex, sampler2D blendTex*/
								  //#if SMAA_REPROJECTION
								  //, sampler2D velocityTex
								  //#endif
								  ) {
	// Fetch the blending weights for current pixel:
	vec4 a;
	a.x = texture(blendTex, offset.xy).a; // Right
	a.y = texture(blendTex, offset.zw).g; // Top
	a.wz = texture(blendTex, texcoord).xz; // Bottom / Left

	// Is there any blending weight with a value greater than 0.0?
	//SMAA_BRANCH
	if (dot(a, vec4(1.0, 1.0, 1.0, 1.0)) < 1e-5) {
		vec4 color = textureLod(colorTex, texcoord, 0.0);

//#if SMAA_REPROJECTION
#ifdef _Veloc
		vec2 velocity = textureLod(sveloc, texCoord, 0.0).rg;
		// Pack velocity into the alpha channel:
		color.a = sqrt(5.0 * length(velocity));
#endif

		return color;
	}
	else {
		bool h = max(a.x, a.z) > max(a.y, a.w); // max(horizontal) > max(vertical)

		// Calculate the blending offsets:
		vec4 blendingOffset = vec4(0.0, a.y, 0.0, a.w);
		vec2 blendingWeight = a.yw;
		
		//SMAAMovc(bvec4(h, h, h, h), blendingOffset, vec4(a.x, 0.0, a.z, 0.0));
		if (h) blendingOffset.x = a.x;
		if (h) blendingOffset.y = 0.0;
		if (h) blendingOffset.z = a.z;
		if (h) blendingOffset.w = 0.0;
		
		// SMAAMovc(bvec2(h, h), blendingWeight, a.xz);
		if (h) blendingWeight.x = a.x;
		if (h) blendingWeight.y = a.z;
		
		blendingWeight /= dot(blendingWeight, vec2(1.0, 1.0));

		// Calculate the texture coordinates:
		vec4 blendingCoord = blendingOffset * vec4(screenSizeInv.xy, -screenSizeInv.xy) + texcoord.xyxy;

		// We exploit bilinear filtering to mix current pixel with the chosen
		// neighbor:
		vec4 color = blendingWeight.x * textureLod(colorTex, blendingCoord.xy, 0.0);
		color += blendingWeight.y * textureLod(colorTex, blendingCoord.zw, 0.0);

//#if SMAA_REPROJECTION
#ifdef _Veloc
		// Antialias velocity for proper reprojection in a later stage:
		vec2 velocity = blendingWeight.x * textureLod(sveloc, blendingCoord.xy, 0.0).rg;
		velocity += blendingWeight.y * textureLod(sveloc, blendingCoord.zw, 0.0).rg;

		// Pack velocity into the alpha channel:
		color.a = sqrt(5.0 * length(velocity));
#endif

		return color;
	}
	return vec4(0.0);
}

void main() {
	fragColor = SMAANeighborhoodBlendingPS(texCoord, offset/*, colorTex, blendTex*/);
}
