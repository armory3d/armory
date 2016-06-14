#version 450

#ifdef GL_ES
precision mediump float;
#endif

// #define SMAASampleLevelZeroOffset(tex, coord, offset) textureLod(tex, vec4(coord + offset * SMAA_RT_METRICS.xy, 0.0, 0.0))
#define SMAASampleLevelZeroOffset(tex, coord, offset) textureLod(tex, coord + offset * SMAA_RT_METRICS.xy, 0.0)
#define saturate(a) clamp(a, 0.0, 1.0)
#define mad(a, b, c) (a * b + c)

uniform sampler2D colorTex;

in vec2 texCoord;
in vec4 offset[3];

// Edge Detection Pixel Shaders (First Pass)

/**
 * Luma Edge Detection
 *
 * IMPORTANT NOTICE: luma edge detection requires gamma-corrected colors, and
 * thus 'colorTex' should be a non-sRGB texture.
 */
vec2 SMAALumaEdgeDetectionPS(vec2 texcoord, vec4 offset[3], sampler2D colorTex
                               //#if SMAA_PREDICATION
                               //, sampler2D predicationTex
                               //#endif
                               ) {
    // Calculate the threshold:
    //#if SMAA_PREDICATION
    //vec2 threshold = SMAACalculatePredicatedThreshold(texcoord, offset, SMAATexturePass2D(predicationTex));
    //#else
    vec2 threshold = vec2(SMAA_THRESHOLD, SMAA_THRESHOLD);
    //#endif

    // Calculate lumas:
    vec3 weights = vec3(0.2126, 0.7152, 0.0722);
    float L = dot(texture(colorTex, texcoord).rgb, weights);

    float Lleft = dot(texture(colorTex, offset[0].xy).rgb, weights);
    float Ltop  = dot(texture(colorTex, offset[0].zw).rgb, weights);

    // We do the usual threshold:
    vec4 delta;
    delta.xy = abs(L - vec2(Lleft, Ltop));
    vec2 edges = step(threshold, delta.xy);

    // Then discard if there is no edge:
    if (dot(edges, vec2(1.0, 1.0)) == 0.0)
        discard;

    // Calculate right and bottom deltas:
    float Lright = dot(texture(colorTex, offset[1].xy).rgb, weights);
    float Lbottom  = dot(texture(colorTex, offset[1].zw).rgb, weights);
    delta.zw = abs(L - vec2(Lright, Lbottom));

    // Calculate the maximum delta in the direct neighborhood:
    vec2 maxDelta = max(delta.xy, delta.zw);

    // Calculate left-left and top-top deltas:
    float Lleftleft = dot(texture(colorTex, offset[2].xy).rgb, weights);
    float Ltoptop = dot(texture(colorTex, offset[2].zw).rgb, weights);
    delta.zw = abs(vec2(Lleft, Ltop) - vec2(Lleftleft, Ltoptop));

    // Calculate the final maximum delta:
    maxDelta = max(maxDelta.xy, delta.zw);
    float finalDelta = max(maxDelta.x, maxDelta.y);

    // Local contrast adaptation:
    edges.xy *= step(finalDelta, SMAA_LOCAL_CONTRAST_ADAPTATION_FACTOR * delta.xy);

    return edges;
}

/**
 * Color Edge Detection
 *
 * IMPORTANT NOTICE: color edge detection requires gamma-corrected colors, and
 * thus 'colorTex' should be a non-sRGB texture.
 */
vec2 SMAAColorEdgeDetectionPS(vec2 texcoord, vec4 offset[3], sampler2D colorTex
                                //#if SMAA_PREDICATION
                                //, sampler2D predicationTex
                                //#endif
                                ) {
    // Calculate the threshold:
    //#if SMAA_PREDICATION
    //vec2 threshold = SMAACalculatePredicatedThreshold(texcoord, offset, predicationTex);
    //#else
    vec2 threshold = vec2(SMAA_THRESHOLD, SMAA_THRESHOLD);
    //#endif

    // Calculate color deltas:
    vec4 delta;
    vec3 C = texture(colorTex, texcoord).rgb;

    vec3 Cleft = texture(colorTex, offset[0].xy).rgb;
    vec3 t = abs(C - Cleft);
    delta.x = max(max(t.r, t.g), t.b);

    vec3 Ctop  = texture(colorTex, offset[0].zw).rgb;
    t = abs(C - Ctop);
    delta.y = max(max(t.r, t.g), t.b);

    // We do the usual threshold:
    vec2 edges = step(threshold, delta.xy);

    // Then discard if there is no edge:
    if (dot(edges, vec2(1.0, 1.0)) == 0.0)
        discard;

    // Calculate right and bottom deltas:
    vec3 Cright = texture(colorTex, offset[1].xy).rgb;
    t = abs(C - Cright);
    delta.z = max(max(t.r, t.g), t.b);

    vec3 Cbottom  = texture(colorTex, offset[1].zw).rgb;
    t = abs(C - Cbottom);
    delta.w = max(max(t.r, t.g), t.b);

    // Calculate the maximum delta in the direct neighborhood:
    vec2 maxDelta = max(delta.xy, delta.zw);

    // Calculate left-left and top-top deltas:
    vec3 Cleftleft  = texture(colorTex, offset[2].xy).rgb;
    t = abs(C - Cleftleft);
    delta.z = max(max(t.r, t.g), t.b);

    vec3 Ctoptop = texture(colorTex, offset[2].zw).rgb;
    t = abs(C - Ctoptop);
    delta.w = max(max(t.r, t.g), t.b);

    // Calculate the final maximum delta:
    maxDelta = max(maxDelta.xy, delta.zw);
    float finalDelta = max(maxDelta.x, maxDelta.y);

    // Local contrast adaptation:
    edges.xy *= step(finalDelta, SMAA_LOCAL_CONTRAST_ADAPTATION_FACTOR * delta.xy);

    return edges;
}

/**
 * Depth Edge Detection
 */
vec2 SMAADepthEdgeDetectionPS(vec2 texcoord, vec4 offset[3], sampler2D depthTex) {
    vec3 neighbours = SMAAGatherNeighbours(texcoord, offset, depthTex);
    vec2 delta = abs(neighbours.xx - vec2(neighbours.y, neighbours.z));
    vec2 edges = step(SMAA_DEPTH_THRESHOLD, delta);

    if (dot(edges, vec2(1.0, 1.0)) == 0.0)
        discard;

    return edges;
}

void main() {
    vec2 edges = SMAALumaEdgeDetectionPS(texCoord, offset, colorTex);
    gl_FragColor.rg = edges;
}
