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
const float DIFFUSE_CONE_APERTURE = 0.872665f;

const vec3 DIFFUSE_CONE_DIRECTIONS[16] = {
	vec3(0.57735f, 0.57735f, 0.57735f),
	vec3(0.57735f, -0.57735f, -0.57735f),
	vec3(-0.57735f, 0.57735f, -0.57735f),
	vec3(-0.57735f, -0.57735f, 0.57735f),
	vec3(-0.903007f, -0.182696f, -0.388844f),
	vec3(-0.903007f, 0.182696f, 0.388844f),
	vec3(0.903007f, -0.182696f, 0.388844f),
	vec3(0.903007f, 0.182696f, -0.388844f),
	vec3(-0.388844f, -0.903007f, -0.182696f),
	vec3(0.388844f, -0.903007f, 0.182696f),
	vec3(0.388844f, 0.903007f, -0.182696f),
	vec3(-0.388844f, 0.903007f, 0.182696f),
	vec3(-0.182696f, -0.388844f, -0.903007f),
	vec3(0.182696f, 0.388844f, -0.903007f),
	vec3(-0.182696f, 0.388844f, 0.903007f),
	vec3(0.182696f, -0.388844f, 0.903007f)
};
