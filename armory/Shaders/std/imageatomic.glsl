
// Courtesy of
// https://github.com/GreatBlambo/voxel_cone_tracing
// https://www.seas.upenn.edu/~pcozzi/OpenGLInsights/OpenGLInsights-SparseVoxelization.pdf


// Converts a normalized vec4 (0..1) to a packed uint RGBA8
uint convVec4ToRGBA8(vec4 val) {
	uvec4 col = uvec4(clamp(val * 255.0 + 0.5, 0.0, 255.0));
    return (col.w << 24U) | (col.z << 16U) | (col.y << 8U) | col.x;
}

// Converts a packed uint RGBA8 to normalized vec4 (0..1)
vec4 convRGBA8ToVec4(uint val) {
    uvec4 col = uvec4(
        val & 0xFFU,
        (val >> 8U) & 0xFFU,
        (val >> 16U) & 0xFFU,
        (val >> 24U) & 0xFFU
    );
    return vec4(col) / 255.0;
}


uint encUnsignedNibble(uint m, uint n) {
	return (m & 0xFEFEFEFE)
		| (n & 0x00000001)
		| (n & 0x00000002) << 7U
		| (n & 0x00000004) << 14U
		| (n & 0x00000008) << 21U;
}

uint decUnsignedNibble(uint m) {
	return (m & 0x00000001)
		| (m & 0x00000100) >> 7U
		| (m & 0x00010000) >> 14U
		| (m & 0x01000000) >> 21U;
}

// Pack RGBA8 (m) with 4-bit count (n in 0..15) into a single uint.
// Packing scheme: clear the LSB of each byte in m, then store each bit of n
// into that LSB position: bit0->byte0.LSB, bit1->byte1.LSB, bit2->byte2.LSB, bit3->byte3.LSB
uint packColorWithCount(uint m, uint n) {
    // clear LSB of each byte
    uint base = m & 0xFEFEFEFEu;
    uint b0 = (n & 0x1u);            // goes to bit 0
    uint b1 = (n & 0x2u) << 7u;      // 0x2 << 7 -> 0x100 (bit 8)
    uint b2 = (n & 0x4u) << 14u;     // -> bit 16
    uint b3 = (n & 0x8u) << 21u;     // -> bit 24
    return base | b0 | b1 | b2 | b3;
}

// Unpack the 4-bit count from the packed representation
uint unpackCount(uint m) {
    return (m & 0x1u) | ((m >> 7u) & 0x2u) | ((m >> 14u) & 0x4u) | ((m >> 21u) & 0x8u);
}

// Extract pure RGBA8 bytes (with LSBs zeroed) from the packed uint so convRGBA8ToVec4 works.
uint extractColorBytes(uint m) {
    return m & 0xFEFEFEFEu;
}

const int PACK_RETRY_LIMIT = 8;
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
