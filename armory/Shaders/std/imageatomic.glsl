
// Courtesy of
// https://github.com/GreatBlambo/voxel_cone_tracing
// https://www.seas.upenn.edu/~pcozzi/OpenGLInsights/OpenGLInsights-SparseVoxelization.pdf


uint convVec4ToRGBA8(vec4 val) {
	vec4 col = vec4(val) * 255;
	return (uint(col.w) & 0x000000FF) << 24U
		 | (uint(col.z) & 0x000000FF) << 16U
		 | (uint(col.y) & 0x000000FF) << 8U
		 | (uint(col.x) & 0x000000FF);
}

vec4 convRGBA8ToVec4(uint val) {
	uvec4 col = uvec4(
		float((val & 0x000000FF)),
		float((val & 0x0000FF00) >> 8U),
		float((val & 0x00FF0000) >> 16U),
		float((val & 0xFF000000) >> 24U));
	return vec4(col) / 255;
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
