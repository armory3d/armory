uniform float shirr[27 * 6]; // Maximum of 6 SH sets

vec3 shIrradiance(vec3 nor, float scale, int probe) {
	const float c1 = 0.429043;
	const float c2 = 0.511664;
	const float c3 = 0.743125;
	const float c4 = 0.886227;
	const float c5 = 0.247708;
	vec3 cl00, cl1m1, cl10, cl11, cl2m2, cl2m1, cl20, cl21, cl22;
	if (probe == 0) {
		cl00 = vec3(shirr[0], shirr[1], shirr[2]);
		cl1m1 = vec3(shirr[3], shirr[4], shirr[5]);
		cl10 = vec3(shirr[6], shirr[7], shirr[8]);
		cl11 = vec3(shirr[9], shirr[10], shirr[11]);
		cl2m2 = vec3(shirr[12], shirr[13], shirr[14]);
		cl2m1 = vec3(shirr[15], shirr[16], shirr[17]);
		cl20 = vec3(shirr[18], shirr[19], shirr[20]);
		cl21 = vec3(shirr[21], shirr[22], shirr[23]);
		cl22 = vec3(shirr[24], shirr[25], shirr[26]);
	}
	else if (probe == 1) {
		cl00 = vec3(shirr[27 + 0], shirr[27 + 1], shirr[27 + 2]); cl1m1 = vec3(shirr[27 + 3], shirr[27 + 4], shirr[27 + 5]);
		cl10 = vec3(shirr[27 + 6], shirr[27 + 7], shirr[27 + 8]); cl11 = vec3(shirr[27 + 9], shirr[27 + 10], shirr[27 + 11]);
		cl2m2 = vec3(shirr[27 + 12], shirr[27 + 13], shirr[27 + 14]); cl2m1 = vec3(shirr[27 + 15], shirr[27 + 16], shirr[27 + 17]);
		cl20 = vec3(shirr[27 + 18], shirr[27 + 19], shirr[27 + 20]); cl21 = vec3(shirr[27 + 21], shirr[27 + 22], shirr[27 + 23]);
		cl22 = vec3(shirr[27 + 24], shirr[27 + 25], shirr[27 + 26]);
	}
	else if (probe == 2) {
		cl00 = vec3(shirr[27 * 2 + 0], shirr[27 * 2 + 1], shirr[27 * 2 + 2]); cl1m1 = vec3(shirr[27 * 2 + 3], shirr[27 * 2 + 4], shirr[27 * 2 + 5]);
		cl10 = vec3(shirr[27 * 2 + 6], shirr[27 * 2 + 7], shirr[27 * 2 + 8]); cl11 = vec3(shirr[27 * 2 + 9], shirr[27 * 2 + 10], shirr[27 * 2 + 11]);
		cl2m2 = vec3(shirr[27 * 2 + 12], shirr[27 * 2 + 13], shirr[27 * 2 + 14]); cl2m1 = vec3(shirr[27 * 2 + 15], shirr[27 * 2 + 16], shirr[27 * 2 + 17]);
		cl20 = vec3(shirr[27 * 2 + 18], shirr[27 * 2 + 19], shirr[27 * 2 + 20]); cl21 = vec3(shirr[27 * 2 + 21], shirr[27 * 2 + 22], shirr[27 * 2 + 23]);
		cl22 = vec3(shirr[27 * 2 + 24], shirr[27 * 2 + 25], shirr[27 * 2 + 26]);
	}
	else if (probe == 3) {
		cl00 = vec3(shirr[27 * 3 + 0], shirr[27 * 3 + 1], shirr[27 * 3 + 2]); cl1m1 = vec3(shirr[27 * 3 + 3], shirr[27 * 3 + 4], shirr[27 * 3 + 5]);
		cl10 = vec3(shirr[27 * 3 + 6], shirr[27 * 3 + 7], shirr[27 * 3 + 8]); cl11 = vec3(shirr[27 * 3 + 9], shirr[27 * 3 + 10], shirr[27 * 3 + 11]);
		cl2m2 = vec3(shirr[27 * 3 + 12], shirr[27 * 3 + 13], shirr[27 * 3 + 14]); cl2m1 = vec3(shirr[27 * 3 + 15], shirr[27 * 3 + 16], shirr[27 * 3 + 17]);
		cl20 = vec3(shirr[27 * 3 + 18], shirr[27 * 3 + 19], shirr[27 * 3 + 20]); cl21 = vec3(shirr[27 * 3 + 21], shirr[27 * 3 + 22], shirr[27 * 3 + 23]);
		cl22 = vec3(shirr[27 * 3 + 24], shirr[27 * 3 + 25], shirr[27 * 3 + 26]);
	}
	else if (probe == 4) {
		cl00 = vec3(shirr[27 * 4 + 0], shirr[27 * 4 + 1], shirr[27 * 4 + 2]); cl1m1 = vec3(shirr[27 * 4 + 3], shirr[27 * 4 + 4], shirr[27 * 4 + 5]);
		cl10 = vec3(shirr[27 * 4 + 6], shirr[27 * 4 + 7], shirr[27 * 4 + 8]); cl11 = vec3(shirr[27 * 4 + 9], shirr[27 * 4 + 10], shirr[27 * 4 + 11]);
		cl2m2 = vec3(shirr[27 * 4 + 12], shirr[27 * 4 + 13], shirr[27 * 4 + 14]); cl2m1 = vec3(shirr[27 * 4 + 15], shirr[27 * 4 + 16], shirr[27 * 4 + 17]);
		cl20 = vec3(shirr[27 * 4 + 18], shirr[27 * 4 + 19], shirr[27 * 4 + 20]); cl21 = vec3(shirr[27 * 4 + 21], shirr[27 * 4 + 22], shirr[27 * 4 + 23]);
		cl22 = vec3(shirr[27 * 4 + 24], shirr[27 * 4 + 25], shirr[27 * 4 + 26]);
	}
	else if (probe == 5) {
		cl00 = vec3(shirr[27 * 5 + 0], shirr[27 * 5 + 1], shirr[27 * 5 + 2]); cl1m1 = vec3(shirr[27 * 5 + 3], shirr[27 * 5 + 4], shirr[27 * 5 + 5]);
		cl10 = vec3(shirr[27 * 5 + 6], shirr[27 * 5 + 7], shirr[27 * 5 + 8]); cl11 = vec3(shirr[27 * 5 + 9], shirr[27 * 5 + 10], shirr[27 * 5 + 11]);
		cl2m2 = vec3(shirr[27 * 5 + 12], shirr[27 * 5 + 13], shirr[27 * 5 + 14]); cl2m1 = vec3(shirr[27 * 5 + 15], shirr[27 * 5 + 16], shirr[27 * 5 + 17]);
		cl20 = vec3(shirr[27 * 5 + 18], shirr[27 * 5 + 19], shirr[27 * 5 + 20]); cl21 = vec3(shirr[27 * 5 + 21], shirr[27 * 5 + 22], shirr[27 * 5 + 23]);
		cl22 = vec3(shirr[27 * 5 + 24], shirr[27 * 5 + 25], shirr[27 * 5 + 26]);
	}
	return (
		c1 * cl22 * (nor.y * nor.y - (-nor.z) * (-nor.z)) +
		c3 * cl20 * nor.x * nor.x +
		c4 * cl00 -
		c5 * cl20 +
		2.0 * c1 * cl2m2 * nor.y * (-nor.z) +
		2.0 * c1 * cl21  * nor.y * nor.x +
		2.0 * c1 * cl2m1 * (-nor.z) * nor.x +
		2.0 * c2 * cl11  * nor.y +
		2.0 * c2 * cl1m1 * (-nor.z) +
		2.0 * c2 * cl10  * nor.x
	) * scale;
}
