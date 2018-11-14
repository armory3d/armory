str_tex_checker = """
vec3 tex_checker(const vec3 co, const vec3 col1, const vec3 col2, const float scale) {
    // Prevent precision issues on unit coordinates
    vec3 p = (co + 0.000001 * 0.999999) * scale;
    float xi = abs(floor(p.x));
    float yi = abs(floor(p.y));
    float zi = abs(floor(p.z));
    bool check = ((mod(xi, 2.0) == mod(yi, 2.0)) == bool(mod(zi, 2.0)));
    return check ? col1 : col2;
}
float tex_checker_f(const vec3 co, const float scale) {
    vec3 p = (co + 0.000001 * 0.999999) * scale;
    float xi = abs(floor(p.x));
    float yi = abs(floor(p.y));
    float zi = abs(floor(p.z));
    return float((mod(xi, 2.0) == mod(yi, 2.0)) == bool(mod(zi, 2.0)));
}
"""

# Created by inigo quilez - iq/2013
# License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License
str_tex_voronoi = """
vec4 tex_voronoi(const vec3 x) {
    vec3 p = floor(x);
    vec3 f = fract(x);
    float id = 0.0;
    float res = 100.0;
    for (int k = -1; k <= 1; k++)
    for (int j = -1; j <= 1; j++)
    for (int i = -1; i <= 1; i++) {
        vec3 b = vec3(float(i), float(j), float(k));
        vec3 pb = p + b;
        vec3 r = vec3(b) - f + texture(snoise256, (pb.xy + vec2(3.0, 1.0) * pb.z + 0.5) / 256.0).xyz;
        float d = dot(r, r);
        if (d < res) {
            id = dot(p + b, vec3(1.0, 57.0, 113.0));
            res = d;
        }
    }
    vec3 col = 0.5 + 0.5 * cos(id * 0.35 + vec3(0.0, 1.0, 2.0));
    return vec4(col, sqrt(res));
}
"""

# Based on https://www.shadertoy.com/view/4sfGzS
# Copyright © 2013 Inigo Quilez
# The MIT License - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# float tex_noise_f(const vec3 x) {
# vec3 p = floor(x);
# vec3 f = fract(x);
# f = f * f * (3.0 - 2.0 * f);
# vec2 uv = (p.xy + vec2(37.0, 17.0) * p.z) + f.xy;
# vec2 rg = texture(snoise256, (uv + 0.5) / 256.0).yx;
# return mix(rg.x, rg.y, f.z);
# }
# By Morgan McGuire @morgan3d, http://graphicscodex.com Reuse permitted under the BSD license.
# https://www.shadertoy.com/view/4dS3Wd
str_tex_noise = """
float hash(float n) { return fract(sin(n) * 1e4); }
float tex_noise_f(vec3 x) {
    const vec3 step = vec3(110, 241, 171);
    vec3 i = floor(x);
    vec3 f = fract(x);
    float n = dot(i, step);
    vec3 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(hash(n + dot(step, vec3(0, 0, 0))), hash(n + dot(step, vec3(1, 0, 0))), u.x),
                   mix(hash(n + dot(step, vec3(0, 1, 0))), hash(n + dot(step, vec3(1, 1, 0))), u.x), u.y),
               mix(mix(hash(n + dot(step, vec3(0, 0, 1))), hash(n + dot(step, vec3(1, 0, 1))), u.x),
                   mix(hash(n + dot(step, vec3(0, 1, 1))), hash(n + dot(step, vec3(1, 1, 1))), u.x), u.y), u.z);
}
float tex_noise(vec3 p) {
    p *= 1.25;
    float f = 0.5 * tex_noise_f(p); p *= 2.01;
    f += 0.25 * tex_noise_f(p); p *= 2.02;
    f += 0.125 * tex_noise_f(p); p *= 2.03;
    f += 0.0625 * tex_noise_f(p);
    return 1.0 - f;
}
"""

# Based on noise created by Nikita Miropolskiy, nikat/2013
# Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License
str_tex_musgrave = """
vec3 random3(const vec3 c) {
    float j = 4096.0 * sin(dot(c, vec3(17.0, 59.4, 15.0)));
    vec3 r;
    r.z = fract(512.0 * j);
    j *= 0.125;
    r.x = fract(512.0 * j);
    j *= 0.125;
    r.y = fract(512.0 * j);
    return r - 0.5;
}
float tex_musgrave_f(const vec3 p) {
    const float F3 = 0.3333333;
    const float G3 = 0.1666667;
    vec3 s = floor(p + dot(p, vec3(F3)));
    vec3 x = p - s + dot(s, vec3(G3));
    vec3 e = step(vec3(0.0), x - x.yzx);
    vec3 i1 = e*(1.0 - e.zxy);
    vec3 i2 = 1.0 - e.zxy*(1.0 - e);
    vec3 x1 = x - i1 + G3;
    vec3 x2 = x - i2 + 2.0*G3;
    vec3 x3 = x - 1.0 + 3.0*G3;
    vec4 w, d;
    w.x = dot(x, x);
    w.y = dot(x1, x1);
    w.z = dot(x2, x2);
    w.w = dot(x3, x3);
    w = max(0.6 - w, 0.0);
    d.x = dot(random3(s), x);
    d.y = dot(random3(s + i1), x1);
    d.z = dot(random3(s + i2), x2);
    d.w = dot(random3(s + 1.0), x3);
    w *= w;
    w *= w;
    d *= w;
    return clamp(dot(d, vec4(52.0)), 0.0, 1.0);
}
"""

# col: the incoming color
# shift: a vector containing the hue shift, the saturation modificator, the value modificator and the mix factor in this order
# this does the following:
# make rgb col to hsv
# apply hue shift through addition, sat/val through multiplication
# return an rgb color, mixed with the original one
str_hue_sat = """
vec3 hsv_to_rgb(const vec3 c) {
  const vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
  vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
  return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}
vec3 rgb_to_hsv(const vec3 c) {
    const vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}
vec3 hue_sat(const vec3 col, const vec4 shift) {
    vec3 hsv = rgb_to_hsv(col);
    hsv.x += shift.x;
    hsv.y *= shift.y;
    hsv.z *= shift.z;
    return mix(hsv_to_rgb(hsv), col, shift.w);
}
"""

# https://twitter.com/Donzanoid/status/903424376707657730
str_wavelength_to_rgb = """
vec3 wavelength_to_rgb(const float t) {
    vec3 r = t * 2.1 - vec3(1.8, 1.14, 0.3);
    return 1.0 - r * r;
}
"""

str_tex_magic = """
vec3 tex_magic(const vec3 p) {
    float a = 1.0 - (sin(p.x) + sin(p.y));
    float b = 1.0 - sin(p.x - p.y);
    float c = 1.0 - sin(p.x + p.y);
    return vec3(a, b, c);
}
float tex_magic_f(const vec3 p) {
    vec3 c = tex_magic(p);
    return (c.x + c.y + c.z) / 3.0;
}
"""

str_tex_brick = """
vec3 tex_brick(vec3 p, const vec3 c1, const vec3 c2, const vec3 c3) {
    p /= vec3(0.9, 0.49, 0.49) / 2;
    if (fract(p.y * 0.5) > 0.5) p.x += 0.5;   
    p = fract(p);
    vec3 b = step(p, vec3(0.95, 0.9, 0.9));
    return mix(c3, c1, b.x * b.y * b.z);
}
float tex_brick_f(vec3 p) {
    p /= vec3(0.9, 0.49, 0.49) / 2;
    if (fract(p.y * 0.5) > 0.5) p.x += 0.5;   
    p = fract(p);
    vec3 b = step(p, vec3(0.95, 0.9, 0.9));
    return mix(1.0, 0.0, b.x * b.y * b.z);
}
"""

str_tex_wave = """
float tex_wave_f(const vec3 p) {
    return 1.0 - sin((p.x + p.y) * 10.0);
}
"""

str_brightcontrast = """
vec3 brightcontrast(const vec3 col, const float bright, const float contr) {
    float a = 1.0 + contr;
    float b = bright - contr * 0.5;
    return max(a * col + b, 0.0);
}
"""

# https://seblagarde.wordpress.com/2013/04/29/memo-on-fresnel-equations/
# dielectric-dielectric
# approx pow(1.0 - dotNV, 7.25 / ior)
str_fresnel = """
float fresnel(float eta, float c) {
    float g = eta * eta - 1.0 + c * c;
    if (g < 0.0) return 1.0;
    g = sqrt(g);
    float a = (g - c) / (g + c);
    float b = ((g + c) * c - 1.0) / ((g - c) * c + 1.0);
    return 0.5 * a * a * (1.0 + b * b);
}
"""
