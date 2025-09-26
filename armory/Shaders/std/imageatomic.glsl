
// Courtesy of
// https://github.com/GreatBlambo/voxel_cone_tracing
// https://www.seas.upenn.edu/~pcozzi/OpenGLInsights/OpenGLInsights-SparseVoxelization.pdf


uint packRGBA8(vec4 color) {
    uvec4 rgba = uvec4(clamp(color, 0.0, 1.0) * 255.0 + 0.5);
    return (rgba.r & 0xFFu) |
           ((rgba.g & 0xFFu) << 8) |
           ((rgba.b & 0xFFu) << 16) |
           ((rgba.a & 0xFFu) << 24);
}

vec4 unpackRGBA8(uint packed) {
    return vec4( float( packed        & 0xFFu),
                 float((packed >> 8)  & 0xFFu),
                 float((packed >> 16) & 0xFFu),
                 float((packed >> 24) & 0xFFu) ) / 255.0;
}

uint packNormalRGB8(vec3 n) {
    // map [-1,1] → [0,255]
    uvec3 enc = uvec3(clamp((n * 0.5 + 0.5) * 255.0 + 0.5, 0.0, 255.0));
    return (enc.r & 0xFFu) |
           ((enc.g & 0xFFu) << 8) |
           ((enc.b & 0xFFu) << 16);
}

vec3 unpackNormalRGB8(uint packed) {
    return vec3(float( packed        & 0xFFu),
                float((packed >> 8)  & 0xFFu),
                float((packed >> 16) & 0xFFu)) / 255.0 * 2.0 - 1.0;
}

// uint encUnsignedNibble(uint m, uint n) {
// 	return (m & 0xFEFEFEFE)
// 		| (n & 0x00000001)
// 		| (n & 0x00000002) << 7U
// 		| (n & 0x00000004) << 14U
// 		| (n & 0x00000008) << 21U;
// }

// uint decUnsignedNibble(uint m) {
// 	return (m & 0x00000001)
// 		| (m & 0x00000100) >> 7U
// 		| (m & 0x00010000) >> 14U
// 		| (m & 0x01000000) >> 21U;
// }

// void imageAtomicRGBA8Avg(layout(r32ui) uimage3D img, ivec3 coords, vec4 val) {
// 	// LSBs are used for the sample counter of the moving average.
// 	val *= 255.0;
// 	uint newVal = encUnsignedNibble(convVec4ToRGBA8(val), 1);
// 	uint prevStoredVal = 0;
// 	uint currStoredVal;
// 	int counter = 0;
// 	// Loop as long as destination value gets changed by other threads
// 	while ((currStoredVal = imageAtomicCompSwap(img, coords, prevStoredVal, newVal)) != prevStoredVal && counter < 16) {
// 		vec4 rval = convRGBA8ToVec4(currStoredVal & 0xFEFEFEFE);
// 		uint n = decUnsignedNibble(currStoredVal);
// 		rval = rval * n + val;
// 		rval /= ++n;
// 		rval = round(rval / 2) * 2;
// 		newVal = encUnsignedNibble(convVec4ToRGBA8(rval), n);
// 		prevStoredVal = currStoredVal;
// 		counter++;
// 	}
// }

// void imageAtomicFloatAdd(layout(r32ui) coherent volatile uimage3D imgUI, ivec3 coords, float val) {
// 	uint newVal = floatBitsToUint(val);
// 	uint prevVal = 0;
// 	uint curVal;
// 	// Loop as long as destination value gets changed by other threads
// 	while ((curVal = imageAtomicCompSwap(imgUI, coords, prevVal, newVal)) != prevVal) {
// 		prevVal = curVal;
// 		newVal = floatBitsToUint((val + uintBitsToFloat(curVal)));
// 	}
// }

// void imageAtomicRGBA8Avg( layout ( r32ui ) coherent volatile uimage3D imgUI , ivec3 coords , vec4 val ) {
// 	val.rgb *= 255.0f; // Optimise following calculations
// 	uint newVal = convVec4ToRGBA8(val);
// 	uint prevStoredVal = 0;
// 	uint curStoredVal;
// 	// Loop as long as destination value gets changed by other threads
// 	while ((curStoredVal = imageAtomicCompSwap(imgUI, coords, prevStoredVal, newVal)) != prevStoredVal) {
// 		prevStoredVal = curStoredVal;
// 		vec4 rval = convRGBA8ToVec4(curStoredVal);
// 		rval.xyz = (rval.xyz * rval.w) ; // Denormalize
// 		vec4 curValF = rval + val; // Add new value
// 		curValF.xyz /= (curValF.w); // Renormalize
// 		newVal = convVec4ToRGBA8(curValF);
// 	}
// }
