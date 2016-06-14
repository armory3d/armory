/**
 * Copyright (C) 2013 Jorge Jimenez (jorge@iryoku.com)
 * Copyright (C) 2013 Jose I. Echevarria (joseignacioechevarria@gmail.com)
 * Copyright (C) 2013 Belen Masia (bmasia@unizar.es)
 * Copyright (C) 2013 Fernando Navarro (fernandn@microsoft.com)
 * Copyright (C) 2013 Diego Gutierrez (diegog@unizar.es)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is furnished to
 * do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software. As clarification, there
 * is no requirement that the copyright notice and permission be included in
 * binary distributions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

/**
 *                  _______  ___  ___       ___           ___
 *                 /       ||   \/   |     /   \         /   \
 *                |   (---- |  \  /  |    /  ^  \       /  ^  \
 *                 \   \    |  |\/|  |   /  /_\  \     /  /_\  \
 *              ----)   |   |  |  |  |  /  _____  \   /  _____  \
 *             |_______/    |__|  |__| /__/     \__\ /__/     \__\
 * 
 *                               E N H A N C E D
 *       S U B P I X E L   M O R P H O L O G I C A L   A N T I A L I A S I N G
 *
 *                         http://www.iryoku.com/smaa/
 */

#version 450

#ifdef GL_ES
precision mediump float;
#endif

#define SMAA_RT_METRICS vec4(1.0 / 800.0, 1.0 / 600.0, 800.0, 600.0)
// #define SMAA_GLSL_3
#define SMAA_PRESET_HIGH
// #include "SMAA.h"

// #define SMAA_AREATEX_SELECT(sample) sample.rg
// #define SMAA_SEARCHTEX_SELECT(sample) sample.r
// #define SMAA_DECODE_VELOCITY(sample) sample.rg

// #if defined(SMAA_PRESET_LOW)
// #define SMAA_THRESHOLD 0.15
// #define SMAA_MAX_SEARCH_STEPS 4
// #define SMAA_DISABLE_DIAG_DETECTION
// #define SMAA_DISABLE_CORNER_DETECTION
// #elif defined(SMAA_PRESET_MEDIUM)
// #define SMAA_THRESHOLD 0.1
// #define SMAA_MAX_SEARCH_STEPS 8
// #define SMAA_DISABLE_DIAG_DETECTION
// #define SMAA_DISABLE_CORNER_DETECTION
// #elif defined(SMAA_PRESET_HIGH)
#define SMAA_THRESHOLD 0.1
#define SMAA_DEPTH_THRESHOLD (0.1 * SMAA_THRESHOLD) // For depth edge detection, depends on the depth range of the scene
#define SMAA_MAX_SEARCH_STEPS 16
// Define SMAA_DISABLE_DIAG_DETECTION to disable diagonal processing
#define SMAA_MAX_SEARCH_STEPS_DIAG 8
// Define SMAA_DISABLE_CORNER_DETECTION to disable corner processing
#define SMAA_CORNER_ROUNDING 25
// If there is an neighbor edge that has SMAA_LOCAL_CONTRAST_FACTOR times bigger contrast than current edge, current edge will be discarded
#define SMAA_LOCAL_CONTRAST_ADAPTATION_FACTOR 2.0
// Predicated thresholding allows to better preserve texture details and to improve performance
#define SMAA_PREDICATION 0
// Threshold to be used in the additional predication buffer
#define SMAA_PREDICATION_THRESHOLD 0.01
// How much to scale the global threshold used for luma or color edge detection when using predication
#define SMAA_PREDICATION_SCALE 2.0
// How much to locally decrease the threshold
#define SMAA_PREDICATION_STRENGTH 0.4
// Temporal reprojection allows to remove ghosting artifacts when using temporal supersampling
#define SMAA_REPROJECTION 0
// SMAA_REPROJECTION_WEIGHT_SCALE controls the velocity weighting
#define SMAA_REPROJECTION_WEIGHT_SCALE 30.0
// #elif defined(SMAA_PRESET_ULTRA)
// #define SMAA_THRESHOLD 0.05
// #define SMAA_MAX_SEARCH_STEPS 32
// #define SMAA_MAX_SEARCH_STEPS_DIAG 16
// #define SMAA_CORNER_ROUNDING 25
// #endif

// Non-Configurable Defines
#define SMAA_AREATEX_MAX_DISTANCE 16
#define SMAA_AREATEX_MAX_DISTANCE_DIAG 20
#define SMAA_AREATEX_PIXEL_SIZE (1.0 / vec2(160.0, 560.0))
#define SMAA_AREATEX_SUBTEX_SIZE (1.0 / 7.0)
#define SMAA_SEARCHTEX_SIZE vec2(66.0, 33.0)
#define SMAA_SEARCHTEX_PACKED_SIZE vec2(64.0, 16.0)
#define SMAA_CORNER_ROUNDING_NORM (float(SMAA_CORNER_ROUNDING) / 100.0)

#define SMAA_FLATTEN
#define SMAA_BRANCH
// #define lerp(a, b, t) mix(a, b, t)
// #define saturate(a) clamp(a, 0.0, 1.0)
// #define mad(a, b, c) (a * b + c)

uniform sampler2D tex;

in vec2 texCoord;


//-----------------------------------------------------------------------------
// Misc functions
// Gathers current pixel, and the top-left neighbors.
vec3 SMAAGatherNeighbours(vec2 texcoord, vec4 offset[3], sampler2D tex) {
    float P = texture(tex, texcoord).r;
    float Pleft = texture(tex, offset[0].xy).r;
    float Ptop  = texture(tex, offset[0].zw).r;
    return vec3(P, Pleft, Ptop);
}

// Adjusts the threshold by means of predication.
vec2 SMAACalculatePredicatedThreshold(vec2 texcoord, vec4 offset[3], sampler2D predicationTex) {
    vec3 neighbours = SMAAGatherNeighbours(texcoord, offset, predicationTex);
    vec2 delta = abs(neighbours.xx - neighbours.yz);
    vec2 edges = step(SMAA_PREDICATION_THRESHOLD, delta);
    return SMAA_PREDICATION_SCALE * SMAA_THRESHOLD * (1.0 - SMAA_PREDICATION_STRENGTH * edges);
}


void main() {
    // gl_FragColor = vec4(col);
}
