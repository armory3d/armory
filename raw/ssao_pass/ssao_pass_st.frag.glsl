// Based on SSAO by Reinder Nijhoff 2016 @reindernijhoff
// https://www.shadertoy.com/view/ls3GWS

#version 450

#ifdef GL_ES
precision mediump float;
#endif

#define SAMPLES 8
#define INTENSITY 3.5
#define SCALE 3.5
#define BIAS 0.75
#define SAMPLE_RAD 0.1
#define MAX_DISTANCE 0.34

#define MOD3 vec3(.1031,.11369,.13787)

uniform mat4 invP;

uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

in vec2 texCoord;

float hash12(vec2 p)
{
    vec3 p3  = fract(vec3(p.xyx) * MOD3);
    p3 += dot(p3, p3.yzx + 19.19);
    return fract((p3.x + p3.y) * p3.z);
}

// vec3 getPosition(vec2 uv) {
//     float fl = texture(iChannel0, vec2(0.)).x; 
//     float d = texture(iChannel0, uv).w;
       
//     vec2 p = uv*2.-1.;
//     mat3 ca = mat3(1.,0.,0.,0.,1.,0.,0.,0.,-1./1.5);
//     vec3 rd = normalize( ca * vec3(p,fl) );
    
//     vec3 pos = rd * d;
//     return pos;
// }
vec3 getViewPos(vec2 texCoord, float depth) {
	float x = texCoord.s * 2.0 - 1.0;
	float y = texCoord.t * 2.0 - 1.0;
	float z = depth * 2.0 - 1.0;
	vec4 posProj = vec4(x, y, z, 1.0);
	vec4 posView = invP * posProj;
	posView /= posView.w;
	return posView.xyz;
}

float doAmbientOcclusion(vec2 tcoord,vec2 uv, vec3 p, vec3 cnorm)
{
    // vec3 diff = getPosition(tcoord + uv) - p;
	float depth = texture(gbuffer0, tcoord + uv).a;
    vec3 diff = getViewPos(tcoord + uv, depth) - p;
    float l = length(diff);
    vec3 v = diff/l;
    float d = l*SCALE;
    float ao = max(0.0,dot(cnorm,v)-BIAS)*(1.0/(1.0+d));
    ao *= smoothstep(MAX_DISTANCE,MAX_DISTANCE * 0.5, l);
    return ao;
}

float spiralAO(vec2 uv, vec3 p, vec3 n, float rad)
{
    float goldenAngle = 2.4;
    float ao = 0.;
    float inv = 1. / float(SAMPLES);
    float radius = 0.;

    float rotatePhase = hash12( uv*100. ) * 6.28;
    float rStep = inv * rad;
    vec2 spiralUV;

    // for (int i = 0; i < SAMPLES; i++) {
        spiralUV.x = sin(rotatePhase);
        spiralUV.y = cos(rotatePhase);
        radius += rStep;
        ao += doAmbientOcclusion(uv, spiralUV * radius, p, n);
        rotatePhase += goldenAngle;
		
		spiralUV.x = sin(rotatePhase);
        spiralUV.y = cos(rotatePhase);
        radius += rStep;
        ao += doAmbientOcclusion(uv, spiralUV * radius, p, n);
        rotatePhase += goldenAngle;
		
		spiralUV.x = sin(rotatePhase);
        spiralUV.y = cos(rotatePhase);
        radius += rStep;
        ao += doAmbientOcclusion(uv, spiralUV * radius, p, n);
        rotatePhase += goldenAngle;
		
		spiralUV.x = sin(rotatePhase);
        spiralUV.y = cos(rotatePhase);
        radius += rStep;
        ao += doAmbientOcclusion(uv, spiralUV * radius, p, n);
        rotatePhase += goldenAngle;
		
		spiralUV.x = sin(rotatePhase);
        spiralUV.y = cos(rotatePhase);
        radius += rStep;
        ao += doAmbientOcclusion(uv, spiralUV * radius, p, n);
        rotatePhase += goldenAngle;
		
		spiralUV.x = sin(rotatePhase);
        spiralUV.y = cos(rotatePhase);
        radius += rStep;
        ao += doAmbientOcclusion(uv, spiralUV * radius, p, n);
        rotatePhase += goldenAngle;
		
		spiralUV.x = sin(rotatePhase);
        spiralUV.y = cos(rotatePhase);
        radius += rStep;
        ao += doAmbientOcclusion(uv, spiralUV * radius, p, n);
        rotatePhase += goldenAngle;
		
		spiralUV.x = sin(rotatePhase);
        spiralUV.y = cos(rotatePhase);
        radius += rStep;
        ao += doAmbientOcclusion(uv, spiralUV * radius, p, n);
        rotatePhase += goldenAngle;
    //}
    ao *= inv;
    return ao;
}

void main() {
	vec4 g0 = texture(gbuffer0, texCoord);
	float depth = g0.a;
	vec3 n = g0.rgb * 2.0 - 1.0;    
    vec3 p = getViewPos(texCoord, depth);

    float ao = 0.;
    float rad = SAMPLE_RAD/p.z;

    ao = spiralAO(texCoord, p, n, rad);

    ao = 1. - ao * INTENSITY;
    
    gl_FragColor = vec4(ao,ao,ao,1.);
}
