// Deferred water based on shader by Wojciech Toman
// http://www.gamedev.net/page/resources/_/technical/graphics-programming-and-theory/rendering-water-as-a-post-process-effect-r2642
// Seascape https://www.shadertoy.com/view/Ms2SD1 
// Caustics https://www.shadertoy.com/view/4ljXWh
// Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License
#version 450

#ifdef GL_ES
precision mediump float;
#endif

const float PI = 3.1415926535;
const float TwoPI = (2.0 * PI);

uniform sampler2D gbuffer0;
uniform sampler2D tex;
uniform sampler2D senvmapRadiance;

uniform float time;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec3 light;

in vec2 texCoord;
in vec3 viewRay;

const float timeScale = 1000.0;
const float waterLevel = 0.0;
const float fadeSpeed = 0.15;
const float maxAmplitude = 2.5;
const vec3 sunColor = vec3(1.0, 1.0, 1.0);
const float shoreHardness = 1.0;
const float refractionStrength = 0.0;
const vec3 foamExistence = vec3(0.65, 1.35, 0.5);
const float sunScale = 3.0;
const float shininess = 0.7;
const float specular_intensity = 0.32;
const vec3 depthColour = vec3(0.0078, 0.5176, 0.9);
const vec3 bigDepthColour = vec3(0.0039, 0.00196, 0.345);
const vec3 extinction = vec3(7.0, 30.0, 40.0); // Horizontal
const float visibility = 2.0;
const vec2 scale = vec2(0.005, 0.005);
const float refractionScale = 0.005;
const vec2 wind = vec2(-0.3, 0.7);

const float SEA_HEIGHT = 0.6;
const float SEA_CHOPPY = 4.0;
const float SEA_SPEED = 1.0;
const float SEA_FREQ = 0.16;
// const vec3 SEA_BASE = vec3(0.1,0.19,0.22);
const vec3 SEA_BASE = vec3(0.1,0.19,0.37);
// const vec3 SEA_WATER_COLOR = vec3(0.8,0.9,0.6);
const vec3 SEA_WATER_COLOR = vec3(0.6,0.7,0.9);
const mat2 octave_m = mat2(1.6,1.2,-1.2,1.6);

vec2 envMapEquirect(vec3 normal) {
	float phi = acos(normal.z);
	float theta = atan(-normal.y, normal.x) + PI;
	return vec2(theta / TwoPI, phi / PI);
}

float hash( vec2 p ) {
	float h = dot(p,vec2(127.1,311.7));	
    return fract(sin(h)*43758.5453123);
}
float noise( vec2 p ) {
    vec2 i = floor( p );
    vec2 f = fract( p );	
	vec2 u = f*f*(3.0-2.0*f);
    return -1.0+2.0*mix(
				mix( hash( i + vec2(0.0,0.0) ), 
                     hash( i + vec2(1.0,0.0) ), u.x),
                mix( hash( i + vec2(0.0,1.0) ), 
                     hash( i + vec2(1.0,1.0) ), u.x), u.y);
}
float sea_octave(vec2 uv, float choppy) {
    uv += noise(uv);        
    vec2 wv = 1.0-abs(sin(uv));
    vec2 swv = abs(cos(uv));    
    wv = mix(wv,swv,wv);
    return pow(1.0-pow(wv.x * wv.y,0.65),choppy);
}
float map(vec3 p) {
    float freq = SEA_FREQ;
    float amp = SEA_HEIGHT;
    float choppy = SEA_CHOPPY;
    vec2 uv = p.xy;
	uv.x *= 0.75;
    
    float d, h = 0.0;
    // for(int i = 0; i < 2; i++) {        
    	d = sea_octave((uv+(time * SEA_SPEED))*freq,choppy);
    	d += sea_octave((uv-(time * SEA_SPEED))*freq,choppy);
        h += d * amp;        
    	uv *= octave_m; freq *= 1.9; amp *= 0.22;
        choppy = mix(choppy,1.0,0.2);
		//
		d = sea_octave((uv+(time * SEA_SPEED))*freq,choppy);
    	d += sea_octave((uv-(time * SEA_SPEED))*freq,choppy);
        h += d * amp;        
    	uv *= octave_m; freq *= 1.9; amp *= 0.22;
        choppy = mix(choppy,1.0,0.2);
		//
    // }
    return p.z - h;
}
float map_detailed(vec3 p) {
    float freq = SEA_FREQ;
    float amp = SEA_HEIGHT;
    float choppy = SEA_CHOPPY;
    vec2 uv = p.xy; uv.x *= 0.75;
    
    float d, h = 0.0;    
    // for(int i = 0; i < 4; i++) {       
    	d = sea_octave((uv+(time * SEA_SPEED))*freq,choppy);
    	d += sea_octave((uv-(time * SEA_SPEED))*freq,choppy);
        h += d * amp;        
    	uv *= octave_m; freq *= 1.9; amp *= 0.22;
        choppy = mix(choppy,1.0,0.2);
		//
		d = sea_octave((uv+(time * SEA_SPEED))*freq,choppy);
    	d += sea_octave((uv-(time * SEA_SPEED))*freq,choppy);
        h += d * amp;        
    	uv *= octave_m; freq *= 1.9; amp *= 0.22;
        choppy = mix(choppy,1.0,0.2);
		d = sea_octave((uv+(time * SEA_SPEED))*freq,choppy);
    	d += sea_octave((uv-(time * SEA_SPEED))*freq,choppy);
        h += d * amp;        
    	uv *= octave_m; freq *= 1.9; amp *= 0.22;
        choppy = mix(choppy,1.0,0.2);
		d = sea_octave((uv+(time * SEA_SPEED))*freq,choppy);
    	d += sea_octave((uv-(time * SEA_SPEED))*freq,choppy);
        h += d * amp;        
    	uv *= octave_m; freq *= 1.9; amp *= 0.22;
        choppy = mix(choppy,1.0,0.2);
		d = sea_octave((uv+(time * SEA_SPEED))*freq,choppy);
    	d += sea_octave((uv-(time * SEA_SPEED))*freq,choppy);
        h += d * amp;        
    	uv *= octave_m; freq *= 1.9; amp *= 0.22;
        choppy = mix(choppy,1.0,0.2);
    // }
    return p.z - h;
}
vec3 getNormal(vec3 p, float eps) {
    vec3 n;
    n.z = map_detailed(p);    
    n.x = map_detailed(vec3(p.x+eps,p.y,p.z)) - n.z;
    n.y = map_detailed(vec3(p.x,p.y+eps,p.z)) - n.z;
    n.z = eps;
    return normalize(n);
}
vec3 heightMapTracing(vec3 ori, vec3 dir) {
    vec3 p;
    float tm = 0.0;
    float tx = 1000.0;    
    float hx = map_detailed(ori + dir * tx);
    if(hx > 0.0) return p;   
    float hm = map_detailed(ori + dir * tm);    
    float tmid = 0.0;
    // for(int i = 0; i < 5; i++) {
        tmid = mix(tm,tx, hm/(hm-hx));                
        p = ori + dir * tmid;
    	float hmid = map_detailed(p);
		if(hmid < 0.0) {
        	tx = tmid;
            hx = hmid;
        } else {
            tm = tmid;
            hm = hmid;
        }
		//
		tmid = mix(tm,tx, hm/(hm-hx));                   
        p = ori + dir * tmid;                   
    	hmid = map_detailed(p);
		if(hmid < 0.0) {
        	tx = tmid;
            hx = hmid;
        } else {
            tm = tmid;
            hm = hmid;
        }
		tmid = mix(tm,tx, hm/(hm-hx));                   
        p = ori + dir * tmid;                   
    	hmid = map_detailed(p);
		if(hmid < 0.0) {
        	tx = tmid;
            hx = hmid;
        } else {
            tm = tmid;
            hm = hmid;
        }
		tmid = mix(tm,tx, hm/(hm-hx));                   
        p = ori + dir * tmid;                   
    	hmid = map_detailed(p);
		if(hmid < 0.0) {
        	tx = tmid;
            hx = hmid;
        } else {
            tm = tmid;
            hm = hmid;
        }
		tmid = mix(tm,tx, hm/(hm-hx));                   
        p = ori + dir * tmid;                   
    	hmid = map_detailed(p);
		if(hmid < 0.0) {
        	tx = tmid;
            hx = hmid;
        } else {
            tm = tmid;
            hm = hmid;
        }
    // }
    return p;
}
vec3 getSkyColor(vec3 e) {
    e.z = max(e.z,0.0);
    vec3 ret;
    ret.x = pow(1.0-e.z,2.0);
    ret.z = 1.0-e.z;
    ret.y = 0.6+(1.0-e.z)*0.4;
    return ret;
}
float diffuse(vec3 n,vec3 l,float p) {
    return pow(dot(n,l) * 0.4 + 0.6,p);
}
float specular(vec3 n,vec3 l,vec3 e,float s) {    
    float nrm = (s + 8.0) / (3.1415 * 8.0);
    return pow(max(dot(reflect(e,n),l),0.0),s) * nrm;
}
vec3 getSeaColor(vec3 p, vec3 n, vec3 l, vec3 eye, vec3 dist) {  
    float fresnel = 1.0 - max(dot(n,-eye),0.0);
    fresnel = pow(fresnel,3.0) * 0.65;
        
    vec3 reflected = getSkyColor(reflect(eye,n));
	// vec3 reflected = textureLod(senvmapRadiance, envMapEquirect(reflect(eye,n)), 1.0).rgb;    
    vec3 refracted = SEA_BASE + diffuse(n,l,80.0) * SEA_WATER_COLOR * 0.12; 
    
    vec3 color = mix(refracted,reflected,fresnel);
    
    float atten = max(1.0 - dot(dist,dist) * 0.001, 0.0);
    color += SEA_WATER_COLOR * (p.z - SEA_HEIGHT) * 0.18 * atten;
    
    color += vec3(specular(n,l,eye,60.0));
    
    return color;
}

// mat3 cotangentFrame(vec3 nor, vec3 pos, vec2 uv) {
//     // Get edge vectors of the pixel triangle
//     vec3 dp1 = dFdx(pos);
//     vec3 dp2 = dFdy(pos);
//     vec2 duv1 = dFdx(uv);
//     vec2 duv2 = dFdy(uv);
//     // Solve the linear system
//     vec3 dp2perp = cross(dp2, nor);
//     vec3 dp1perp = cross(nor, dp1);
//     vec3 T = dp2perp * duv1.x + dp1perp * duv2.x;
//     vec3 B = dp2perp * duv1.y + dp1perp * duv2.y;
//     // Construct a scale-invariant frame 
//     float invmax = inversesqrt(max(dot(T,T), dot(B,B)));
//     return mat3(T * invmax, B * invmax, nor);
// }

vec3 getPos(float depth) {	
    vec3 vray = normalize(viewRay);
	const float znear = 0.1;
	const float zfar = 1000.0;
	const float projectionA = zfar / (zfar - znear);
	const float projectionB = (-zfar * znear) / (zfar - znear);
	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
	float viewZDist = dot(eyeLook, vray);
	vec3 wposition = eye + vray * (linearDepth / viewZDist);
	return wposition;
}

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

// vec3 getNormal(vec2 tc) {
// 	vec2 enc = texture(gbuffer0, tc).rg;
// 	vec3 n;
// 	n.z = 1.0 - abs(enc.x) - abs(enc.y);
// 	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
// 	n = normalize(n);
// 	return n;
// }

vec3 caustic(vec2 uv) {
    vec2 p = mod(uv*TwoPI, TwoPI)-250.0;
    float loctime = time * .5+23.0;

	vec2 i = vec2(p);
	float c = 1.0;
	float inten = .005;

	// for (int n = 0; n < MAX_ITER; n++) {
		float t = loctime * (1.0 - (3.5 / float(0+1)));
		i = p + vec2(cos(t - i.x) + sin(t + i.y), sin(t - i.y) + cos(t + i.x));
		c += 1.0/length(vec2(p.x / (sin(i.x+t)/inten),p.y / (cos(i.y+t)/inten)));
		
		t = loctime * (1.0 - (3.5 / float(0+1)));
		i = p + vec2(cos(t - i.x) + sin(t + i.y), sin(t - i.y) + cos(t + i.x));
		c += 1.0/length(vec2(p.x / (sin(i.x+t)/inten),p.y / (cos(i.y+t)/inten)));
		
		t = loctime * (1.0 - (3.5 / float(0+1)));
		i = p + vec2(cos(t - i.x) + sin(t + i.y), sin(t - i.y) + cos(t + i.x));
		c += 1.0/length(vec2(p.x / (sin(i.x+t)/inten),p.y / (cos(i.y+t)/inten)));
		
		t = loctime * (1.0 - (3.5 / float(0+1)));
		i = p + vec2(cos(t - i.x) + sin(t + i.y), sin(t - i.y) + cos(t + i.x));
		c += 1.0/length(vec2(p.x / (sin(i.x+t)/inten),p.y / (cos(i.y+t)/inten)));
	// }
    
	c /= float(4);
	c = 1.17-pow(c, 1.4);
	vec3 color = vec3(pow(abs(c), 8.0));
    color = clamp(color + vec3(0.0, 0.35, 0.5), 0.0, 1.0);
    color = mix(color, vec3(1.0,1.0,1.0),0.3);
    
    return color;
}
float causticX(float x, float power, float gtime)
{
    float p = mod(x*TwoPI, TwoPI)-250.0;
    float time = gtime * .5+23.0;

	float i = p;
	float c = 1.0;
	float inten = .005;

	// for (int n = 0; n < MAX_ITER/2; n++) {
		float t = time * (1.0 - (3.5 / float(0+1)));
		i = p + cos(t - i) + sin(t + i);
		c += 1.0/length(p / (sin(i+t)/inten));
		
		t = time * (1.0 - (3.5 / float(1+1)));
		i = p + cos(t - i) + sin(t + i);
		c += 1.0/length(p / (sin(i+t)/inten));
	// }
	c /= float(4);
	c = 1.17-pow(c, power);
    
    return c;
}
float godRays(vec2 uv) {
    float light = 0.0;
    light += pow(causticX((uv.x+0.08*uv.y)/1.7+0.5, 1.8, time*0.65),10.0)*0.05;
    light -= pow((1.0-uv.y)*0.3,2.0)*0.2;
    light += pow(causticX(sin(uv.x), 0.3,time*0.7),9.0)*0.4; 
    light += pow(causticX(cos(uv.x*2.3), 0.3,time*1.3),4.0)*0.1;  
    light -= pow((1.0-uv.y)*0.3,3.0);
    light = clamp(light,0.0,1.0);
    return light;
}

void main() {	
	vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, mask, depth
	float gdepth = 1.0 - g0.a;
	vec4 colorOriginal = texture(tex, texCoord);
	if (gdepth == 0.0) {
		gl_FragColor = colorOriginal;
		return;
	}
	
    vec3 color = colorOriginal.rgb;
    vec3 position = getPos(gdepth);
    
    // Underwater
    if (waterLevel >= eye.z) {
		float t = length(eye - position);
		// color *= caustic(vec2(mix(position.x,position.y,0.2),mix(position.z,position.y,0.2))*1.1);
		color = mix(colorOriginal.rgb, vec3(0.0, 0.05, 0.2), 1.0 - exp(-0.3 * pow(t,1.0) ));
		const float skyColor = 0.8;
		color += godRays(texCoord)*mix(skyColor,1.0,texCoord.y*texCoord.y)*vec3(0.7,1.0,1.0);
		gl_FragColor = vec4(color, 1.0);
		return;
    }
    if (position.z <= waterLevel + maxAmplitude) {
		// vec3 ld = normalize(vec3(0.0,0.8,1.0));
		vec3 ld = normalize(vec3(0.3,-0.3,1.0));
		vec3 lightDir = light - position.xyz;
		vec3 eyeDir = eye - position.xyz;
		vec3 l = normalize(lightDir);
		vec3 v = normalize(eyeDir);
        
		vec3 surfacePoint = heightMapTracing(eye, -v);
        float depth = length(position - surfacePoint);
        float depthZ = surfacePoint.z - position.z;
		
		// float dist = length(surfacePoint - eye);
		// float epsx = clamp(dot(dist/2.0,dist/2.0) * 0.001, 0.01, 0.1);
		
		float dist = max(0.1, length(surfacePoint - eye) * 1.2);
		// float epsx = dot(dist,dist) * 0.001;
		float epsx = dot(dist,dist) * 0.0008;
		vec3 normal = getNormal(surfacePoint, epsx);
		
		// vec3 normal = getNormal(surfacePoint, 0.1);
		
        float fresnel = 1.0 - max(dot(normal,-v),0.0);
    	fresnel = pow(fresnel,3.0) * 0.65;
        
		
		// vec2 texco = texCoord.xy;
        // texco.x += sin((time * timeScale) * 0.002 + 3.0 * abs(position.z)) * (refractionScale * min(depthZ, 1.0));
        // vec3 refraction = texture(tex, texco).rgb;
		// vec3 _p = getPos(1.0 - texture(gbuffer0, texco).a);
		// if (_p.z > waterLevel) {
        //     refraction = colorOriginal.rgb;
		// }
		
		// vec3 reflect = textureLod(senvmapRadiance, envMapEquirect(reflect(v,normal)), 2.0).rgb;
        
        // vec3 depthN = vec3(depth * fadeSpeed);
        // vec3 waterCol = vec3(clamp(length(sunColor) / sunScale, 0.0, 1.0));
        // refraction = mix(mix(refraction, depthColour * waterCol, clamp(depthN / visibility, 0.0, 1.0)), bigDepthColour * waterCol, clamp(depthZ / extinction, 0.0, 1.0));

        // float foam = 0.0;    
        // // texco = (surfacePoint.xy + v.xy * 0.1) * 0.05 + (time * timeScale) * 0.00001 * wind + sin((time * timeScale) * 0.001 + position.x) * 0.005;
        // // vec2 texco2 = (surfacePoint.xy + v.xy * 0.1) * 0.05 + (time * timeScale) * 0.00002 * wind + sin((time * timeScale) * 0.001 + position.y) * 0.005;
        // // if (depthZ < foamExistence.x) {
        // //     foam = (texture(fmap, texco).r + texture(fmap, texco2).r) * 0.5;
		// // }
        // // else if (depthZ < foamExistence.y) {
        // //     foam = mix((texture(fmap, texco).r + texture(fmap, texco2).r) * 0.5, 0.0,
        // //                  (depthZ - foamExistence.x) / (foamExistence.y - foamExistence.x));
        // // }
        // // if (maxAmplitude - foamExistence.z > 0.0001) {
        // //     foam += (texture(fmap, texco).r + texture(fmap, texco2).r) * 0.5 * 
        // //         clamp((waterLevel - (waterLevel + foamExistence.z)) / (maxAmplitude - foamExistence.z), 0.0, 1.0);
        // // }

        // vec3 mirrorEye = (2.0 * dot(v, normal) * normal - v);
        // float dotSpec = clamp(dot(mirrorEye.xyz, -lightDir) * 0.5 + 0.5, 0.0, 1.0);
        // vec3 specular = (1.0 - fresnel) * clamp(-lightDir.z, 0.0, 1.0) * ((pow(dotSpec, 512.0)) * (shininess * 1.8 + 0.2))* sunColor;
        // specular += specular * 25 * clamp(shininess - 0.05, 0.0, 1.0) * sunColor;   
        // color = mix(refraction, reflect, fresnel);
        // color = clamp(color + max(specular, foam * sunColor), 0.0, 1.0);
        // color = mix(refraction, color, clamp(depth * shoreHardness, 0.0, 1.0));
		 
		color = getSeaColor(surfacePoint,normal,ld,-v,surfacePoint-eye);
		// color = pow(color, vec3(2.2));
		color = mix(colorOriginal.rgb, color, clamp(depthZ * 1.8, 0.0, 1.0));
	}
    
    // if (position.z > waterLevel) {
        // color = colorOriginal.rgb;
	// }

	gl_FragColor.rgb = color;
	
}
