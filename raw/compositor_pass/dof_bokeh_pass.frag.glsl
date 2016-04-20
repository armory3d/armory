// Depth of Field by Martins Upitis (devlog-martinsh.blogspot.com)
#version 450

#ifdef GL_ES
precision mediump float;
#endif

#define PI 3.1415653592

uniform sampler2D tex;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

const float znear = 0.1;
const float zfar = 100.0;
const float width = 800;
const float height = 600;
const vec2 texel = vec2(1.0 / width, 1.0 / height);

const float focalDepth = 0;  // focal distance value in meters
const float focalLength = 50; // focal length in mm 18-200
const float fstop = 20; // f-stop value

const int samples = 3; // samples on the first ring
const int rings = 3; // ring count

const vec2 focus = vec2(0.5,0.5);

const float CoC = 0.03; // circle of confusion size in mm (35mm film = 0.03mm)
const float maxblur = 1.0;
const float threshold = 0.5; // highlight threshold
const float gain = 2.0; // highlight gain
const float bias = 0.5; // bokeh edge bias
const float fringe = 0.7; // bokeh chromatic aberration/fringing
const float namount = 0.0001; // dither amount

const float vignout = 1.3; // vignetting outer border
const float vignin = 0.0; // vignetting inner border
const float vignfade = 90.0; // f-stops till vignete fades

// bool pentagon = false; // Use pentagon as bokeh shape?
// float feather = 0.4; // Pentagon shape feather

// float dbsize = 1.25; //  Depth blur size

in vec2 texCoord;

// float penta(vec2 coords) { //pentagonal shape
// 	float scale = float(rings) - 1.3;
// 	vec4  HS0 = vec4( 1.0,         0.0,         0.0,  1.0);
// 	vec4  HS1 = vec4( 0.309016994, 0.951056516, 0.0,  1.0);
// 	vec4  HS2 = vec4(-0.809016994, 0.587785252, 0.0,  1.0);
// 	vec4  HS3 = vec4(-0.809016994,-0.587785252, 0.0,  1.0);
// 	vec4  HS4 = vec4( 0.309016994,-0.951056516, 0.0,  1.0);
// 	vec4  HS5 = vec4( 0.0        ,0.0         , 1.0,  1.0);
	
// 	vec4  one = vec4( 1.0 );
	
// 	vec4 P = vec4((coords),vec2(scale, scale)); 
	
// 	vec4 dist = vec4(0.0);
// 	float inorout = -4.0;
	
// 	dist.x = dot( P, HS0 );
// 	dist.y = dot( P, HS1 );
// 	dist.z = dot( P, HS2 );
// 	dist.w = dot( P, HS3 );
	
// 	dist = smoothstep( -feather, feather, dist );
	
// 	inorout += dot( dist, one );
	
// 	dist.x = dot( P, HS4 );
// 	dist.y = HS5.w - abs( P.z );
	
// 	dist = smoothstep( -feather, feather, dist );
// 	inorout += dist.x;

// 	return clamp( inorout, 0.0, 1.0 );
// }

// float bdepth(vec2 coords) { //blurring depth
// 	float d = 0.0;
// 	float kernel[9];
// 	vec2 offset[9];
	
// 	vec2 wh = vec2(texel.x, texel.y) * dbsize;
	
// 	offset[0] = vec2(-wh.x,-wh.y);
// 	offset[1] = vec2( 0.0, -wh.y);
// 	offset[2] = vec2( wh.x -wh.y);
	
// 	offset[3] = vec2(-wh.x,  0.0);
// 	offset[4] = vec2( 0.0,   0.0);
// 	offset[5] = vec2( wh.x,  0.0);
	
// 	offset[6] = vec2(-wh.x, wh.y);
// 	offset[7] = vec2( 0.0,  wh.y);
// 	offset[8] = vec2( wh.x, wh.y);
	
// 	kernel[0] = 1.0/16.0;   kernel[1] = 2.0/16.0;   kernel[2] = 1.0/16.0;
// 	kernel[3] = 2.0/16.0;   kernel[4] = 4.0/16.0;   kernel[5] = 2.0/16.0;
// 	kernel[6] = 1.0/16.0;   kernel[7] = 2.0/16.0;   kernel[8] = 1.0/16.0;
	
// 	for( int i=0; i<9; i++ )
// 	{
// 		float tmp = texture2D(bgl_DepthTexture, coords + offset[i]).r;
// 		d += tmp * kernel[i];
// 	}
// 	return d;
// }

vec3 color(vec2 coords, float blur) {
	vec3 col = vec3(0.0);
	col.r = texture(tex, coords + vec2(0.0,1.0)*texel*fringe*blur).r;
	col.g = texture(tex, coords + vec2(-0.866,-0.5)*texel*fringe*blur).g;
	col.b = texture(tex, coords + vec2(0.866,-0.5)*texel*fringe*blur).b;
	
	vec3 lumcoeff = vec3(0.299, 0.587, 0.114);
	float lum = dot(col.rgb, lumcoeff);
	float thresh = max((lum-threshold)*gain, 0.0);
	return col+mix(vec3(0.0),col,thresh*blur);
}

vec2 rand(vec2 coord) {
	float noiseX = ((fract(1.0-coord.s*(width/2.0))*0.25)+(fract(coord.t*(height/2.0))*0.75))*2.0-1.0;
	float noiseY = ((fract(1.0-coord.s*(width/2.0))*0.75)+(fract(coord.t*(height/2.0))*0.25))*2.0-1.0;
	return vec2(noiseX,noiseY);
	// if (noise) {
		// noiseX = clamp(fract(sin(dot(coord ,vec2(12.9898,78.233))) * 43758.5453),0.0,1.0)*2.0-1.0;
		// noiseY = clamp(fract(sin(dot(coord ,vec2(12.9898,78.233)*2.0)) * 43758.5453),0.0,1.0)*2.0-1.0;
	// }
}

float linearize(float depth) {
	return -zfar * znear / (depth * (zfar - znear) - zfar);
}

float vignette() {
	float dist = distance(texCoord, vec2(0.5,0.5));
	dist = smoothstep(vignout+(fstop/vignfade), vignin+(fstop/vignfade), dist);
	return clamp(dist,0.0,1.0);
}

vec3 debugFocus(vec3 col, float blur, float depth) {
	float edge = 0.002*depth; //distance based edge smoothing
	float m = clamp(smoothstep(0.0,edge,blur),0.0,1.0);
	float e = clamp(smoothstep(1.0-edge,1.0,blur),0.0,1.0);
	col = mix(col,vec3(1.0,0.5,0.0),(1.0-m)*0.6);
	col = mix(col,vec3(0.0,0.5,1.0),((1.0-e)-(1.0-m))*0.2);
	return col;
}

void main() {
	float depthbuf = texture(gbuffer0, texCoord).a;
	float depth = linearize(depthbuf);
	
	// Blur depth
	// depth = linearize(bdepth(texCoord.xy));
	
	float fDepth = focalDepth;
	// Autofocus
	//fDepth = linearize(texture(gbuffer0, focus).a);
	
	float blur = 0.0;
	float f = focalLength; // focal length in mm
	float d = fDepth*1000.0; // focal plane in mm
	float o = depth*1000.0; // depth in mm
	float a = (o*f)/(o-f); 
	float b = (d*f)/(d-f); 
	float c = (d-f)/(d*fstop*CoC); 
	blur = abs(a-b)*c;
	blur = clamp(blur,0.0,1.0);
	
	vec2 noise = rand(texCoord)*namount*blur;
	float w = (texel.x)*blur*maxblur+noise.x;
	float h = (texel.y)*blur*maxblur+noise.y;
	vec3 col = vec3(0.0);
	if (blur < 0.05) {
		col = texture(tex, texCoord).rgb;
	}
	else {
		col = texture(tex, texCoord).rgb;
		float s = 1.0;
		int ringsamples;
		
		// for (int i = 1; i <= rings; ++i) {   
		// 	ringsamples = i * samples;
		// 	for (int j = 0 ; j < ringsamples; ++j) {
		// 		float step = PI*2.0 / float(ringsamples);
		// 		float pw = (cos(float(j)*step)*float(i));
		// 		float ph = (sin(float(j)*step)*float(i));
		// 		float p = 1.0;
		// 		if (pentagon) { 
		// 			p = penta(vec2(pw,ph));
		//		}
		// 		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		// 		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		// 	}
		// }
		
		int i = 1; // i <= rings   
		ringsamples = i * samples;
		
		int j = 0; // j < ringsamples
		float step = PI*2.0 / float(ringsamples);
		float pw = (cos(float(j)*step)*float(i));
		float ph = (sin(float(j)*step)*float(i));
		float p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p;
		j = 1; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 2; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		//------
		
		i = 2; // i <= rings   
		ringsamples = i * samples;
		
		j = 0; // j < ringsamples
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p;
		j = 1; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 2; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 3; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 4; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 5; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		//------	
		
		i = 3; // i <= rings   
		ringsamples = i * samples;
		
		j = 0; // j < ringsamples
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p;
		j = 1; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 2; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 3; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 4; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 5; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 6; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 7; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		j = 8; //////
		step = PI*2.0 / float(ringsamples);
		pw = (cos(float(j)*step)*float(i));
		ph = (sin(float(j)*step)*float(i));
		p = 1.0;
		col += color(texCoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
		s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p; 
		//------
		
		col /= s;
	}
	
	// Show focus
	//col = debugFocus(col, blur, depth);
	
	// Vignetting
	col *= vignette();
	
	gl_FragColor = vec4(col, 1.0);
}
