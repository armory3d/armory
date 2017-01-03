// Auto-generated
let project = new Project('untitled');

project.addSources('Sources');
project.addLibrary("../../..");
project.addLibrary("iron");
project.addShaders('build/compiled/ShaderRaws/Material/Material_mesh.frag.glsl');
project.addShaders('build/compiled/ShaderRaws/Material/Material_mesh.vert.glsl');
project.addShaders('build/compiled/ShaderRaws/Material/Material_shadowmap.frag.glsl');
project.addShaders('build/compiled/ShaderRaws/Material/Material_shadowmap.vert.glsl');
project.addShaders('build/compiled/Shaders/blur_edge_pass/blur_edge_pass_EnvCol_SSAO_SMAA.frag.glsl');
project.addShaders('build/compiled/Shaders/blur_edge_pass/blur_edge_pass_EnvCol_SSAO_SMAA.vert.glsl');
project.addShaders('build/compiled/Shaders/compositor_pass/compositor_pass_EnvCol_SSAO_SMAA_CompoTonemap.frag.glsl');
project.addShaders('build/compiled/Shaders/compositor_pass/compositor_pass_EnvCol_SSAO_SMAA_CompoTonemap.vert.glsl');
project.addShaders('build/compiled/Shaders/deferred_indirect/deferred_indirect_EnvCol_SSAO_SMAA.frag.glsl');
project.addShaders('build/compiled/Shaders/deferred_indirect/deferred_indirect_EnvCol_SSAO_SMAA.vert.glsl');
project.addShaders('build/compiled/Shaders/deferred_light/deferred_light_EnvCol_SSAO_SMAA.frag.glsl');
project.addShaders('build/compiled/Shaders/deferred_light/deferred_light_EnvCol_SSAO_SMAA.vert.glsl');
project.addShaders('build/compiled/Shaders/smaa_blend_weight/smaa_blend_weight_EnvCol_SSAO_SMAA.frag.glsl');
project.addShaders('build/compiled/Shaders/smaa_blend_weight/smaa_blend_weight_EnvCol_SSAO_SMAA.vert.glsl');
project.addShaders('build/compiled/Shaders/smaa_edge_detect/smaa_edge_detect_EnvCol_SSAO_SMAA.frag.glsl');
project.addShaders('build/compiled/Shaders/smaa_edge_detect/smaa_edge_detect_EnvCol_SSAO_SMAA.vert.glsl');
project.addShaders('build/compiled/Shaders/smaa_neighborhood_blend/smaa_neighborhood_blend_EnvCol_SSAO_SMAA.frag.glsl');
project.addShaders('build/compiled/Shaders/smaa_neighborhood_blend/smaa_neighborhood_blend_EnvCol_SSAO_SMAA.vert.glsl');
project.addShaders('build/compiled/Shaders/ssao_pass/ssao_pass_EnvCol_SSAO_SMAA.frag.glsl');
project.addShaders('build/compiled/Shaders/ssao_pass/ssao_pass_EnvCol_SSAO_SMAA.vert.glsl');
project.addShaders('build/compiled/Shaders/world/world_EnvCol_SSAO_SMAA.frag.glsl');
project.addShaders('build/compiled/Shaders/world/world_EnvCol_SSAO_SMAA.vert.glsl');
project.addAssets('build/compiled/ShaderDatas/blur_edge_pass/blur_edge_pass_EnvCol_SSAO_SMAA.arm');
project.addAssets('build/compiled/ShaderDatas/compositor_pass/compositor_pass_EnvCol_SSAO_SMAA_CompoTonemap.arm');
project.addAssets('build/compiled/ShaderDatas/deferred_indirect/deferred_indirect_EnvCol_SSAO_SMAA.arm');
project.addAssets('build/compiled/ShaderDatas/deferred_light/deferred_light_EnvCol_SSAO_SMAA.arm');
project.addAssets('build/compiled/ShaderDatas/smaa_blend_weight/smaa_blend_weight_EnvCol_SSAO_SMAA.arm');
project.addAssets('build/compiled/ShaderDatas/smaa_edge_detect/smaa_edge_detect_EnvCol_SSAO_SMAA.arm');
project.addAssets('build/compiled/ShaderDatas/smaa_neighborhood_blend/smaa_neighborhood_blend_EnvCol_SSAO_SMAA.arm');
project.addAssets('build/compiled/ShaderDatas/ssao_pass/ssao_pass_EnvCol_SSAO_SMAA.arm');
project.addAssets('build/compiled/ShaderDatas/world/world_EnvCol_SSAO_SMAA.arm');
project.addAssets('build/compiled/ShaderRaws/Material/Material_data.arm');
project.addAssets('build/compiled/Assets/Scene.arm');
project.addAssets('build/compiled/Assets/envmaps/World_irradiance.arm');
project.addAssets('build/compiled/Assets/materials/World_material.arm');
project.addAssets('build/compiled/Assets/meshes/mesh_Cube.arm');
project.addAssets('build/compiled/Assets/renderpaths/armory_default.arm');


resolve(project);
