/*
Copyright (c) 2024 Turánszki János

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
 */

const int DIFFUSE_CONE_COUNT = 16;

const float SHADOW_CONE_APERTURE = radians(15.0);

const float DIFFUSE_CONE_APERTURE = 0.872665; // ~50 degrees

mat3 makeTangentBasis(vec3 normal) {
	vec3 up = abs(normal.y) < 0.999 ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 0.0);
	vec3 tangent = normalize(cross(up, normal));
	vec3 bitangent = cross(normal, tangent);
	return mat3(tangent, bitangent, normal);
}

const vec3 DIFFUSE_CONE_DIRECTIONS[DIFFUSE_CONE_COUNT] = vec3[](
    vec3( 0.1036,  0.9688,  0.2254),
    vec3(-0.3495,  0.9086,  0.2303),
    vec3( 0.6225,  0.7593,  0.1905),
    vec3(-0.7486,  0.6551,  0.1023),
    vec3( 0.8902,  0.4554, -0.0128),
    vec3(-0.9495,  0.3120, -0.0302),
    vec3( 0.9312,  0.2467,  0.2681),
    vec3(-0.8125,  0.4214,  0.4038),
    vec3( 0.6284,  0.5562,  0.5437),
    vec3(-0.3877,  0.6817,  0.6213),
    vec3( 0.0783,  0.7758,  0.6258),
    vec3( 0.2079,  0.7419, -0.6375),
    vec3(-0.5037,  0.6832, -0.5299),
    vec3( 0.7240,  0.5869, -0.3626),
    vec3(-0.8670,  0.4762, -0.1437),
    vec3( 0.9745,  0.2243, -0.0049)
);

const float BayerMatrix8[8][8] =
{
	{ 1.0 / 65.0, 49.0 / 65.0, 13.0 / 65.0, 61.0 / 65.0, 4.0 / 65.0, 52.0 / 65.0, 16.0 / 65.0, 64.0 / 65.0 },
	{ 33.0 / 65.0, 17.0 / 65.0, 45.0 / 65.0, 29.0 / 65.0, 36.0 / 65.0, 20.0 / 65.0, 48.0 / 65.0, 32.0 / 65.0 },
	{ 9.0 / 65.0, 57.0 / 65.0, 5.0 / 65.0, 53.0 / 65.0, 12.0 / 65.0, 60.0 / 65.0, 8.0 / 65.0, 56.0 / 65.0 },
	{ 41.0 / 65.0, 25.0 / 65.0, 37.0 / 65.0, 21.0 / 65.0, 44.0 / 65.0, 28.0 / 65.0, 40.0 / 65.0, 24.0 / 65.0 },
	{ 3.0 / 65.0, 51.0 / 65.0, 15.0 / 65.0, 63.0 / 65.0, 2.0 / 65.0, 50.0 / 65.0, 14.0 / 65.0, 62.0 / 65.0 },
	{ 35.0 / 65.0, 19.0 / 65.0, 47.0 / 65.0, 31.0 / 65.0, 34.0 / 65.0, 18.0 / 65.0, 46.0 / 65.0, 30.0 / 65.0 },
	{ 11.0 / 65.0, 59.0 / 65.0, 7.0 / 65.0, 55.0 / 65.0, 10.0 / 65.0, 58.0 / 65.0, 6.0 / 65.0, 54.0 / 65.0 },
	{ 43.0 / 65.0, 27.0 / 65.0, 39.0 / 65.0, 23.0 / 65.0, 42.0 / 65.0, 26.0 / 65.0, 38.0 / 65.0, 22.0 / 65.0 }
};
