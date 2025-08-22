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
const float DIFFUSE_CONE_APERTURE_WIDE = radians(50.0);  // for z=0.7071 cones
const float DIFFUSE_CONE_APERTURE_NARROW = radians(30.0); // for z≈0.935 cones
const float REFERENCE_APERTURE = 0.872665; // 50 degrees in radians


mat3 makeTangentBasis(vec3 n) {
    vec3 t, b;
    if (n.z < -0.9999999) {
        t = vec3(0.0, -1.0, 0.0);
        b = vec3(-1.0, 0.0, 0.0);
    } else {
        float a = 1.0 / (1.0 + n.z);
        float b_ = -n.x * n.y * a;
        t = vec3(1.0 - n.x * n.x * a, b_, -n.x);
        b = vec3(b_, 1.0 - n.y * n.y * a, -n.y);
    }
    return mat3(t, b, n);
}

// 16 optimized cone directions for hemisphere sampling (Z-up, normalized)
const vec3 DIFFUSE_CONE_DIRECTIONS[16] = vec3[](
    vec3(0.707107, 0.000000, 0.707107),  // Front
    vec3(-0.707107, 0.000000, 0.707107), // Back
    vec3(0.000000, 0.707107, 0.707107),  // Right
    vec3(0.000000, -0.707107, 0.707107), // Left
    vec3(0.500000, 0.500000, 0.707107),  // Front-right
    vec3(-0.500000, 0.500000, 0.707107), // Back-right
    vec3(0.500000, -0.500000, 0.707107), // Front-left
    vec3(-0.500000, -0.500000, 0.707107),// Back-left
    vec3(0.353553, 0.000000, 0.935414),  // Narrow front
    vec3(-0.353553, 0.000000, 0.935414), // Narrow back
    vec3(0.000000, 0.353553, 0.935414),  // Narrow right
    vec3(0.000000, -0.353553, 0.935414), // Narrow left
    vec3(0.270598, 0.270598, 0.923880),  // Narrow front-right
    vec3(-0.270598, 0.270598, 0.923880), // Narrow back-right
    vec3(0.270598, -0.270598, 0.923880), // Narrow front-left
    vec3(-0.270598, -0.270598, 0.923880) // Narrow back-left
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
