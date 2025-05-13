str_tex_proc = """
//	<https://www.shadertoy.com/view/4dS3Wd>
//	By Morgan McGuire @morgan3d, http://graphicscodex.com
float hash_f(const float n) { return fract(sin(n) * 1e4); }
float hash_f(const vec2 p) { return fract(1e4 * sin(17.0 * p.x + p.y * 0.1) * (0.1 + abs(sin(p.y * 13.0 + p.x)))); }
float hash_f(const vec3 co){ return fract(sin(dot(co.xyz, vec3(12.9898,78.233,52.8265)) * 24.384) * 43758.5453); }

float noise(const vec3 x) {
	const vec3 step = vec3(110, 241, 171);

	vec3 i = floor(x);
	vec3 f = fract(x);
 
	// For performance, compute the base input to a 1D hash from the integer part of the argument and the 
	// incremental change to the 1D based on the 3D -> 1D wrapping
    float n = dot(i, step);

	vec3 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix( hash_f(n + dot(step, vec3(0, 0, 0))), hash_f(n + dot(step, vec3(1, 0, 0))), u.x),
                   mix( hash_f(n + dot(step, vec3(0, 1, 0))), hash_f(n + dot(step, vec3(1, 1, 0))), u.x), u.y),
               mix(mix( hash_f(n + dot(step, vec3(0, 0, 1))), hash_f(n + dot(step, vec3(1, 0, 1))), u.x),
                   mix( hash_f(n + dot(step, vec3(0, 1, 1))), hash_f(n + dot(step, vec3(1, 1, 1))), u.x), u.y), u.z);
}

//  Shader-code adapted from Blender
//  https://github.com/sobotka/blender/blob/master/source/blender/gpu/shaders/material/gpu_shader_material_tex_wave.glsl & /gpu_shader_material_fractal_noise.glsl
float fractal_noise(const vec3 p, const float o)
{
  float fscale = 1.0;
  float amp = 1.0;
  float sum = 0.0;
  float octaves = clamp(o, 0.0, 16.0);
  int n = int(octaves);
  for (int i = 0; i <= n; i++) {
    float t = noise(fscale * p);
    sum += t * amp;
    amp *= 0.5;
    fscale *= 2.0;
  }
  float rmd = octaves - floor(octaves);
  if (rmd != 0.0) {
    float t = noise(fscale * p);
    float sum2 = sum + t * amp;
    sum *= float(pow(2, n)) / float(pow(2, n + 1) - 1.0);
    sum2 *= float(pow(2, n + 1)) / float(pow(2, n + 2) - 1);
    return (1.0 - rmd) * sum + rmd * sum2;
  }
  else {
    sum *= float(pow(2, n)) / float(pow(2, n + 1) - 1); 
    return sum;
  }
}
"""

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

str_tex_voronoi = """
//Shader-code adapted from Blender
//https://github.com/sobotka/blender/blob/master/source/blender/gpu/shaders/material/gpu_shader_material_tex_voronoi.glsl
float voronoi_distance(const vec3 a, const vec3 b, const int metric, const float exponent)
{
  if (metric == 0)  // SHD_VORONOI_EUCLIDEAN
  {
    return distance(a, b);
  }
  else if (metric == 1)  // SHD_VORONOI_MANHATTAN
  {
    return abs(a.x - b.x) + abs(a.y - b.y) + abs(a.z - b.z);
  }
  else if (metric == 2)  // SHD_VORONOI_CHEBYCHEV
  {
    return max(abs(a.x - b.x), max(abs(a.y - b.y), abs(a.z - b.z)));
  }
  else if (metric == 3)  // SHD_VORONOI_MINKOWSKI
  {
    return pow(pow(abs(a.x - b.x), exponent) + pow(abs(a.y - b.y), exponent) +
                   pow(abs(a.z - b.z), exponent),
               1.0 / exponent);
  }
  else {
    return 0.5;
  }
}

vec3 tex_voronoi(const vec3 coord, const float r, const int metric, const int outp, const float scale, const float exp)
{
  float randomness = clamp(r, 0.0, 1.0);

  vec3 scaledCoord = coord * scale;
  vec3 cellPosition = floor(scaledCoord);
  vec3 localPosition = scaledCoord - cellPosition;

  float minDistance = 8.0;
  vec3 targetOffset, targetPosition;
  for (int k = -1; k <= 1; k++) {
    for (int j = -1; j <= 1; j++) {
      for (int i = -1; i <= 1; i++) {
        vec3 cellOffset = vec3(float(i), float(j), float(k));
        vec3 pointPosition = cellOffset;
        if(randomness != 0.) {
            pointPosition += vec3(hash_f(cellPosition+cellOffset), hash_f(cellPosition+cellOffset+972.37), hash_f(cellPosition+cellOffset+342.48)) * randomness;}
        float distanceToPoint = voronoi_distance(pointPosition, localPosition, metric, exp);
        if (distanceToPoint < minDistance) {
          targetOffset = cellOffset;
          minDistance = distanceToPoint;
          targetPosition = pointPosition;
        }
      }
    }
  }
  if(outp == 0){return vec3(minDistance);}
  else if(outp == 1) {
      if(randomness == 0.) {return vec3(hash_f(cellPosition+targetOffset), hash_f(cellPosition+targetOffset+972.37), hash_f(cellPosition+targetOffset+342.48));}
      return (targetPosition - targetOffset)/randomness;
  }
  return (targetPosition + cellPosition) / scale;
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
float tex_noise(const vec3 p, const float detail, const float distortion) {
    vec3 pk = p;
    if (distortion != 0.0) {
    pk += vec3(noise(p) * distortion);
  }
  return fractal_noise(pk, detail);
}
"""

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

float noise_tex(const vec3 p) {
    const float F3 = 0.3333333;
    const float G3 = 0.1666667;

    vec3 s = floor(p + dot(p, vec3(F3)));
    vec3 x = p - s + dot(s, vec3(G3));
    vec3 e = step(vec3(0.0), x - x.yzx);
    vec3 i1 = e * (1.0 - e.zxy);
    vec3 i2 = 1.0 - e.zxy * (1.0 - e);

    vec3 x1 = x - i1 + G3;
    vec3 x2 = x - i2 + 2.0 * G3;
    vec3 x3 = x - 1.0 + 3.0 * G3;

    vec4 w;
    w.x = max(0.6 - dot(x, x), 0.0);
    w.y = max(0.6 - dot(x1, x1), 0.0);
    w.z = max(0.6 - dot(x2, x2), 0.0);
    w.w = max(0.6 - dot(x3, x3), 0.0);

    w = w * w;
    w = w * w;

    vec4 d;
    d.x = dot(random3(s), x);
    d.y = dot(random3(s + i1), x1);
    d.z = dot(random3(s + i2), x2);
    d.w = dot(random3(s + 1.0), x3);

    d *= w;
    return clamp(dot(d, vec4(52.0)), 0.0, 1.0);
}

float tex_musgrave_f(const vec3 p, float detail, float distortion) {
    // Apply distortion to the input coordinates smoothly with noise_tex
    vec3 distorted_p = p + distortion * vec3(
        noise_tex(p + vec3(5.2, 1.3, 7.1)),
        noise_tex(p + vec3(1.7, 9.2, 3.8)),
        noise_tex(p + vec3(8.3, 2.8, 4.5))
    );

    float value = 0.0;
    float amplitude = 1.0;
    float frequency = 1.0;

    // Use 'detail' as number of octaves, clamped between 1 and 8
    int octaves = int(clamp(detail, 1.0, 8.0));

    for (int i = 0; i < octaves; i++) {
        value += amplitude * noise_tex(distorted_p * frequency);
        frequency *= 2.0;
        amplitude *= 0.5;
    }

    return clamp(value, 0.0, 1.0);
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
float tex_wave_f(const vec3 p, const int type, const int profile, const float dist, const float detail, const float detail_scale) {
    float n;
    if(type == 0) n = (p.x + p.y + p.z) * 9.5;
    else n = length(p) * 13.0;
    if(dist != 0.0) n += dist * fractal_noise(p * detail_scale, detail) * 2.0 - 1.0;
    if(profile == 0) { return 0.5 + 0.5 * sin(n - PI); }
    else {
        n /= 2.0 * PI;
        return n - floor(n);
    }
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

# Save division like Blender does it. If dividing by 0, the result is 0.
# https://github.com/blender/blender/blob/df1e9b662bd6938f74579cea9d30341f3b6dd02b/intern/cycles/kernel/shaders/node_vector_math.osl
str_safe_divide = """
vec3 safe_divide(const vec3 a, const vec3 b) {
\treturn vec3((b.x != 0.0) ? a.x / b.x : 0.0,
\t            (b.y != 0.0) ? a.y / b.y : 0.0,
\t            (b.z != 0.0) ? a.z / b.z : 0.0);
}
"""

# https://github.com/blender/blender/blob/df1e9b662bd6938f74579cea9d30341f3b6dd02b/intern/cycles/kernel/shaders/node_vector_math.osl
str_project = """
vec3 project(const vec3 v, const vec3 v_proj) {
\tfloat lenSquared = dot(v_proj, v_proj);
\treturn (lenSquared != 0.0) ? (dot(v, v_proj) / lenSquared) * v_proj : vec3(0);
}
"""

# Adapted from godot engine math_funcs.h
str_wrap = """
float wrap(const float value, const float max, const float min) {
\tfloat range = max - min;
\treturn (range != 0.0) ? value - (range * floor((value - min) / range)) : min;
}
vec3 wrap(const vec3 value, const vec3 max, const vec3 min) {
\treturn vec3(wrap(value.x, max.x, min.x),
\t            wrap(value.y, max.y, min.y),
\t            wrap(value.z, max.z, min.z));
}
"""

str_blackbody = """
vec3 blackbody(const float temperature){

  vec3 rgb = vec3(0.0, 0.0, 0.0);

  vec3 r = vec3(0.0, 0.0, 0.0);
  vec3 g = vec3(0.0, 0.0, 0.0);
  vec3 b = vec3(0.0, 0.0, 0.0);

  float t_inv = float(1.0 / temperature);

  if (temperature >= 12000.0) {

    rgb = vec3(0.826270103, 0.994478524, 1.56626022);

  } else if(temperature < 965.0) {

    rgb = vec3(4.70366907, 0.0, 0.0);

  } else {

    if (temperature >= 6365.0) {
      vec3 r = vec3(3.78765709e+03, 9.36026367e-06, 3.98995841e-01);
      vec3 g = vec3(-5.00279505e+02, -4.59745390e-06, 1.09090465e+00);
      vec4 b = vec4(6.72595954e-13, -2.73059993e-08, 4.24068546e-04, -7.52204323e-01);

      rgb = vec3(r.r * t_inv + r.g * temperature + r.b, g.r * t_inv + g.g * temperature + g.b, ((b.r * temperature + b.g) * temperature + b.b) * temperature + b.a );

    } else if (temperature >= 3315.0) {
      vec3 r = vec3(4.60124770e+03, 2.89727618e-05, 1.48001316e-01);
      vec3 g = vec3(-1.18134453e+03, -2.18913373e-05, 1.30656109e+00);
      vec4 b = vec4(-2.22463426e-13, -1.55078698e-08, 3.81675160e-04, -7.30646033e-01);

      rgb = vec3(r.r * t_inv + r.g * temperature + r.b, g.r * t_inv + g.g * temperature + g.b, ((b.r * temperature + b.g) * temperature + b.b) * temperature + b.a );

    } else if (temperature >= 1902.0) {
      vec3 r = vec3(4.66849800e+03, 2.85655028e-05, 1.29075375e-01);
      vec3 g = vec3(-1.42546105e+03, -4.01730887e-05, 1.44002695e+00);
      vec4 b = vec4(-2.02524603e-11, 1.79435860e-07, -2.60561875e-04, -1.41761141e-02);

      rgb = vec3(r.r * t_inv + r.g * temperature + r.b, g.r * t_inv + g.g * temperature + g.b, ((b.r * temperature + b.g) * temperature + b.b) * temperature + b.a );

    } else if (temperature >= 1449.0) {
      vec3 r = vec3(4.10671449e+03, -8.61949938e-05, 6.41423749e-01);
      vec3 g = vec3(-1.22075471e+03, 2.56245413e-05, 1.20753416e+00);
      vec4 b = vec4(0.0, 0.0, 0.0, 0.0);

      rgb = vec3(r.r * t_inv + r.g * temperature + r.b, g.r * t_inv + g.g * temperature + g.b, ((b.r * temperature + b.g) * temperature + b.b) * temperature + b.a );

    } else if (temperature >= 1167.0) {
      vec3 r = vec3(3.37763626e+03, -4.34581697e-04, 1.64843306e+00);
      vec3 g = vec3(-1.00402363e+03, 1.29189794e-04, 9.08181524e-01);
      vec4 b = vec4(0.0, 0.0, 0.0, 0.0);

      rgb = vec3(r.r * t_inv + r.g * temperature + r.b, g.r * t_inv + g.g * temperature + g.b, ((b.r * temperature + b.g) * temperature + b.b) * temperature + b.a );

    } else {
      vec3 r = vec3(2.52432244e+03, -1.06185848e-03, 3.11067539e+00);
      vec3 g = vec3(-7.50343014e+02, 3.15679613e-04, 4.73464526e-01);
      vec4 b = vec4(0.0, 0.0, 0.0, 0.0);

      rgb = vec3(r.r * t_inv + r.g * temperature + r.b, g.r * t_inv + g.g * temperature + g.b, ((b.r * temperature + b.g) * temperature + b.b) * temperature + b.a );

    }
  }

  return rgb;

}
"""

# Adapted from https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/gpu/shaders/material/gpu_shader_material_map_range.glsl
str_map_range_linear = """
float map_range_linear(const float value, const float fromMin, const float fromMax, const float toMin, const float toMax) {
  if (fromMax != fromMin) {
    return float(toMin + ((value - fromMin) / (fromMax - fromMin)) * (toMax - toMin));
  }
  else {
    return float(0.0);
  }
}
"""

str_map_range_stepped = """
float map_range_stepped(const float value, const float fromMin, const float fromMax, const float toMin, const float toMax, const float steps) {
  if (fromMax != fromMin) {
    float factor = (value - fromMin) / (fromMax - fromMin);
    factor = (steps > 0.0) ? floor(factor * (steps + 1.0)) / steps : 0.0;
    return float(toMin + factor * (toMax - toMin));
  }
  else {
    return float(0.0);
  }
}
"""

str_map_range_smoothstep = """
float map_range_smoothstep(const float value, const float fromMin, const float fromMax, const float toMin, const float toMax)
{
  if (fromMax != fromMin) {
    float factor = (fromMin > fromMax) ? 1.0 - smoothstep(fromMax, fromMin, value) :
                                         smoothstep(fromMin, fromMax, value);
    return float(toMin + factor * (toMax - toMin));
  }
  else {
    return float(0.0);
  }
}
"""

str_map_range_smootherstep = """
float safe_divide(float a, float b)
{
  return (b != 0.0) ? a / b : 0.0;
}

float smootherstep(float edge0, float edge1, float x)
{
  x = clamp(safe_divide((x - edge0), (edge1 - edge0)), 0.0, 1.0);
  return x * x * x * (x * (x * 6.0 - 15.0) + 10.0);
}

float map_range_smootherstep(const float value, const float fromMin, const float fromMax, const float toMin, const float toMax) {
  if (fromMax != fromMin) {
    float factor = (fromMin > fromMax) ? 1.0 - smootherstep(fromMax, fromMin, value) :
                                         smootherstep(fromMin, fromMax, value);
    return float(toMin + factor * (toMax - toMin));
  }
  else {
    return float(0.0);
  }
}
"""

str_rotate_around_axis = """
vec3 rotate_around_axis(const vec3 p, const vec3 axis, const float angle)
{
  float costheta = cos(angle);
  float sintheta = sin(angle);
  vec3 r;

  r.x = ((costheta + (1.0 - costheta) * axis.x * axis.x) * p.x) +
        (((1.0 - costheta) * axis.x * axis.y - axis.z * sintheta) * p.y) +
        (((1.0 - costheta) * axis.x * axis.z + axis.y * sintheta) * p.z);

  r.y = (((1.0 - costheta) * axis.x * axis.y + axis.z * sintheta) * p.x) +
        ((costheta + (1.0 - costheta) * axis.y * axis.y) * p.y) +
        (((1.0 - costheta) * axis.y * axis.z - axis.x * sintheta) * p.z);

  r.z = (((1.0 - costheta) * axis.x * axis.z - axis.y * sintheta) * p.x) +
        (((1.0 - costheta) * axis.y * axis.z + axis.x * sintheta) * p.y) +
        ((costheta + (1.0 - costheta) * axis.z * axis.z) * p.z);

  return r;
}
"""

str_euler_to_mat3 = """
mat3 euler_to_mat3(vec3 euler)
{
  float cx = cos(euler.x);
  float cy = cos(euler.y);
  float cz = cos(euler.z);
  float sx = sin(euler.x);
  float sy = sin(euler.y);
  float sz = sin(euler.z);

  mat3 mat;
  mat[0][0] = cy * cz;
  mat[0][1] = cy * sz;
  mat[0][2] = -sy;

  mat[1][0] = sy * sx * cz - cx * sz;
  mat[1][1] = sy * sx * sz + cx * cz;
  mat[1][2] = cy * sx;

  mat[2][0] = sy * cx * cz + sx * sz;
  mat[2][1] = sy * cx * sz - sx * cz;
  mat[2][2] = cy * cx;
  return mat;
}
"""