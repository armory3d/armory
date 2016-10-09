// http://simonstechblog.blogspot.sk/2013/01/implementing-voxel-cone-tracing.html
// http://leifnode.com/2015/05/voxel-cone-traced-global-illumination/
// http://www.seas.upenn.edu/%7Epcozzi/OpenGLInsights/OpenGLInsights-SparseVoxelization.pdf
// https://github.com/Cigg/Voxel-Cone-Tracing
// https://research.nvidia.com/sites/default/files/publications/GIVoxels-pg2011-authors.pdf
#version 450
#extension GL_ARB_shader_image_load_store : enable

in fragData {
#ifdef _Tex
    vec2 texuv;
#endif
    flat int axis;
    vec4 lPos;
} frag;

uniform layout(RGBA8) image3D voxels;
#ifdef _BaseTex
	uniform sampler2D sbase;
#endif
uniform vec4 baseCol;
uniform sampler2D shadowMap;
const int voxelDimensions = 512;

void main() {
#ifdef _BaseTex
    vec4 matCol = texture(sbase, frag.texuv);
#else
	vec4 matCol = baseCol;
#endif

    // vec4 lPosH = frag.lPos / frag.lPos.w;
    // float distanceFromLight = texture(shadowMap, lPosH.xy).r * 2.0 - 1.0;
    // const float shadowsBias = 0.0001;
	// float visibility = float(distanceFromLight > lPosH.z - shadowsBias);
	float visibility = 1.0;

	ivec3 camPos = ivec3(gl_FragCoord.x, gl_FragCoord.y, voxelDimensions * gl_FragCoord.z);
	ivec3 texPos;
	if (frag.axis == 1) {
	    texPos.x = voxelDimensions - camPos.z;
		texPos.z = camPos.x;
		texPos.y = camPos.y;
	}
	else if (frag.axis == 2) {
	    texPos.z = camPos.y;
		texPos.y = voxelDimensions - camPos.z;
		texPos.x = camPos.x;
	}
	else {
	    texPos = camPos;
	}
	texPos.z = voxelDimensions - texPos.z - 1;
    imageStore(voxels, texPos, vec4(matCol.rgb * visibility, 1.0));
}