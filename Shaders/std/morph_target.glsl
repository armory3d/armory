uniform sampler2D morphDataPos;
uniform sampler2D morphDataNor;
uniform vec2 morphScaleOffset;
uniform float morphWeights[32];

void getMorphedVertex(vec2 uvCoord, inout vec3 A){
    for(int i = 0; i<32; i++ )
    {
        vec2 tempCoord = uvCoord;
        tempCoord.y *= i;
        vec3 morph = texture(morphDataPos, tempCoord).rgb * morphScaleOffset.x + morphScaleOffset.y;
        A += morphWeights[i] * morph;
    }
}

void getMorphedNormal(vec2 uvCoord, vec3 oldNor, inout vec3 morphNor){
    for(int i = 0; i<32; i++ )
    {
        vec2 tempCoord = uvCoord;
        tempCoord.y *= i;
        vec3 norm = morphWeights[i] + (texture(morphDataNor, tempCoord).rgb * 2.0 - 1.0);
        morphNor += norm;
    }

    morphNor += oldNor;
    morphNor = normalize(morphNor);
}