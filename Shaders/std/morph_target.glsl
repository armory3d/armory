uniform sampler2D morphDataPos;
uniform sampler2D morphDataNor;
uniform vec2 morphScaleOffset;
uniform vec2 morphDataDim;
uniform vec4 morphWeights[8];

void getMorphedVertex(vec2 uvCoord, inout vec3 A){
    for(int i = 0; i<8; i++ )
    {        
        vec4 tempCoordY = vec4( uvCoord.y -     (i * 4) * morphDataDim.y, 
                                uvCoord.y - (i * 4 + 1) * morphDataDim.y,
                                uvCoord.y - (i * 4 + 2) * morphDataDim.y,
                                uvCoord.y - (i * 4 + 3) * morphDataDim.y);

        vec3 morph = texture(morphDataPos, vec2(uvCoord.x, tempCoordY.x)).rgb * morphScaleOffset.x + morphScaleOffset.y;
        A += morphWeights[i].x * morph;

        morph = texture(morphDataPos, vec2(uvCoord.x, tempCoordY.y)).rgb * morphScaleOffset.x + morphScaleOffset.y;
        A += morphWeights[i].y * morph;

        morph = texture(morphDataPos, vec2(uvCoord.x, tempCoordY.z)).rgb * morphScaleOffset.x + morphScaleOffset.y;
        A += morphWeights[i].z * morph;

        morph = texture(morphDataPos, vec2(uvCoord.x, tempCoordY.w)).rgb * morphScaleOffset.x + morphScaleOffset.y;
        A += morphWeights[i].w * morph;
    }
}

void getMorphedNormal(vec2 uvCoord, vec3 oldNor, inout vec3 morphNor){
    
    for(int i = 0; i<8; i++ )
    {
        vec4 tempCoordY = vec4( uvCoord.y -     (i * 4) * morphDataDim.y, 
                                uvCoord.y - (i * 4 + 1) * morphDataDim.y,
                                uvCoord.y - (i * 4 + 2) * morphDataDim.y,
                                uvCoord.y - (i * 4 + 3) * morphDataDim.y);
        
        vec3 norm = oldNor + morphWeights[i].x * (texture(morphDataNor, vec2(uvCoord.x, tempCoordY.x)).rgb * 2.0 - 1.0);
        morphNor += norm;

        norm = oldNor + morphWeights[i].y * (texture(morphDataNor, vec2(uvCoord.x, tempCoordY.y)).rgb * 2.0 - 1.0);
        morphNor += norm;

        norm = oldNor + morphWeights[i].z * (texture(morphDataNor, vec2(uvCoord.x, tempCoordY.z)).rgb * 2.0 - 1.0);
        morphNor += norm;

        norm = oldNor + morphWeights[i].w * (texture(morphDataNor, vec2(uvCoord.x, tempCoordY.w)).rgb * 2.0 - 1.0);
        morphNor += norm;

    }

    morphNor = normalize(morphNor);
}