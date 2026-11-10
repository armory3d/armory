# Add Parallax Occlusion Mapping node support
# Append to existing nodes_shader.py

def parse_parallaxocclusionnode(node, out_socket, state):
    """
    Parallax Occlusion Mapping (POM) node with self-shadowing.
    
    Inputs:
        - Height: Height map texture (0-1 range)
        - UV: UV coordinates (optional, defaults to texcoord)
        - Scale: Depth scale factor
        - Min Layers: Minimum raymarch steps
        - Max Layers: Maximum raymarch steps
    
    Outputs:
        - UV: Displaced UV coordinates
        - Shadow: Self-shadowing factor (0-1)
    """
    import arm.material.cycles as cycles
    import arm.material.make_state as state_mod
    
    # Get inputs
    height_map = cycles.parse_value_input(node.inputs['Height']) if node.inputs['Height'].is_linked else '0.5'
    uv_input = cycles.parse_vector_input(node.inputs['UV']) if node.inputs['UV'].is_linked else 'texCoord'
    scale = cycles.parse_value_input(node.inputs['Scale']) if node.inputs['Scale'].is_linked else str(node.inputs['Scale'].default_value)
    min_layers = str(int(node.inputs['Min Layers'].default_value))
    max_layers = str(int(node.inputs['Max Layers'].default_value))
    
    # Add POM function to shader
    state_mod.curdata['shader'].add_function('''
vec3 parallax_occlusion_mapping(
    sampler2D heightMap,
    vec2 texCoords,
    vec3 viewDir,
    float heightScale,
    float minLayers,
    float maxLayers
) {
    // Calculate number of layers based on view angle
    float numLayers = mix(maxLayers, minLayers, abs(dot(vec3(0.0, 0.0, 1.0), viewDir)));
    float layerDepth = 1.0 / numLayers;
    float currentLayerDepth = 0.0;
    
    vec2 p = viewDir.xy / viewDir.z * heightScale;
    vec2 deltaTexCoords = p / numLayers;
    
    vec2 currentTexCoords = texCoords;
    float currentDepthMapValue = texture(heightMap, currentTexCoords).r;
    
    // Raymarch until we find intersection
    while (currentLayerDepth < currentDepthMapValue) {
        currentTexCoords -= deltaTexCoords;
        currentDepthMapValue = texture(heightMap, currentTexCoords).r;
        currentLayerDepth += layerDepth;
    }
    
    // Binary search refinement
    vec2 prevTexCoords = currentTexCoords + deltaTexCoords;
    float afterDepth = currentDepthMapValue - currentLayerDepth;
    float beforeDepth = texture(heightMap, prevTexCoords).r - currentLayerDepth + layerDepth;
    float weight = afterDepth / (afterDepth - beforeDepth);
    vec2 finalTexCoords = prevTexCoords * weight + currentTexCoords * (1.0 - weight);
    
    // Return UV and depth for shadowing
    float finalDepth = currentLayerDepth;
    return vec3(finalTexCoords, finalDepth);
}

float pom_self_shadow(
    sampler2D heightMap,
    vec2 texCoords,
    vec3 lightDir,
    float initialHeight,
    float heightScale
) {
    float shadowMultiplier = 1.0;
    const float numShadowLayers = 16.0;
    float layerDepth = initialHeight / numShadowLayers;
    
    vec2 deltaTexCoords = lightDir.xy / lightDir.z * heightScale / numShadowLayers;
    
    vec2 currentTexCoords = texCoords;
    float currentDepth = initialHeight - layerDepth;
    float currentHeight = texture(heightMap, currentTexCoords).r;
    
    while (currentDepth > 0.0) {
        if (currentHeight > currentDepth) {
            float newShadowMultiplier = (currentDepth - currentHeight) * (l.0 - currentDepth / initialHeight);
            shadowMultiplier = max(shadowMultiplier, newShadowMultiplier);
        }
        currentDepth -= layerDepth;
        currentTexCoords += deltaTexCoords;
        currentHeight = texture(heightMap, currentTexCoords).r;
    }
    
    return 1.0 - clamp(shadowMultiplier * 2.0, 0.0, 1.0);
}
''')
    
    # Generate unique variable names
    var_name = cycles.node_name(node.name)
    
    # Output the appropriate socket
    if out_socket.name == 'UV':
        return f'parallax_occlusion_mapping(heightTex, {uv_input}.xy, vViewPosition, {scale}, {min_layers}.0, {max_layers}.0).xy'
    elif out_socket.name == 'Shadow':
        return f'pom_self_shadow(heightTex, {uv_input}.xy, lightDir, 0.0, {scale})'
    return 'vec2(0.0)'
