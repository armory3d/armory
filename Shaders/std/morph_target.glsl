#version 450

uniform sampler2D morphData;
uniform float morphWeights[maxMorphTargets];

in vec2 texCoord;
