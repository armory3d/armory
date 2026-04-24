package iron.data;

#if !macro
import kha.FastFloat;
import kha.arrays.Float32Array;
import kha.arrays.Uint32Array;
import kha.arrays.Int16Array;
#end

#if macro
typedef Float32Array = haxe.io.Float32Array;
typedef Uint32Array = haxe.io.UInt32Array;
typedef Int16Array = haxe.io.UInt16Array;
typedef FastFloat = Float;
#end

#if js
typedef TSceneFormat = {
#else
@:structInit class TSceneFormat {
#end
	@:optional public var name: String;
	@:optional public var mesh_datas: Array<TMeshData>;
	@:optional public var light_datas: Array<TLightData>;
	@:optional public var probe_datas: Array<TProbeData>;
	@:optional public var camera_datas: Array<TCameraData>;
	@:optional public var camera_ref: String; // Active camera
	@:optional public var material_datas: Array<TMaterialData>;
	@:optional public var particle_datas: Array<TParticleData>;
	@:optional public var shader_datas: Array<TShaderData>;
	@:optional public var speaker_datas: Array<TSpeakerData>;
	@:optional public var world_datas: Array<TWorldData>;
	@:optional public var world_ref: String;
	@:optional public var objects: Array<TObj>;
	@:optional public var groups: Array<TGroup>;
	@:optional public var gravity: Float32Array;
	@:optional public var traits: Array<TTrait>; // Scene root traits
	@:optional public var embedded_datas: Array<String>; // Preload for this scene, images only for now
	@:optional public var frame_time: Null<FastFloat>;
	@:optional public var irradiance: Float32Array; // Blob with spherical harmonics, bands 0,1,2
	@:optional public var terrain_datas: Array<TTerrainData>;
	@:optional public var terrain_ref: String;
}

#if js
typedef TMeshData = {
#else
@:structInit class TMeshData {
#end
	public var name: String;
	public var sorting_index: Int;
	public var vertex_arrays: Array<TVertexArray>;
	public var index_arrays: Array<TIndexArray>;
	@:optional public var dynamic_usage: Null<Bool>;
	@:optional public var skin: TSkin;
	@:optional public var instanced_data: Float32Array;
	@:optional public var instanced_type: Null<Int>; // off, loc, loc+rot, loc+scale, loc+rot+scale
	@:optional public var scale_pos: Null<FastFloat>; // Unpack pos from (-1,1) coords
	@:optional public var scale_tex: Null<FastFloat>; // Unpack tex from (-1,1) coords
	@:optional public var morph_target: TMorphTarget;
}

#if js
typedef TMorphTarget = {
#else
@:structInit class TMorphTarget {
#end
	public var morph_target_data_file: String;
	public var morph_scale: FastFloat;
	public var morph_offset: FastFloat;
	public var num_morph_targets: Int;
	public var morph_img_size: Int;
	public var morph_block_size: Int;
	public var morph_target_ref: Array<String>;
	public var morph_target_defaults: Float32Array;
}

#if js
typedef TSkin = {
#else
@:structInit class TSkin {
#end
	public var transform: TTransform;
	public var bone_ref_array: Array<String>;
	public var bone_len_array: Float32Array;
	public var transformsI: Array<Float32Array>; // per-bone, size = 16, with skin.transform, pre-inverted
	public var bone_count_array: Int16Array;
	public var bone_index_array: Int16Array;
	public var bone_weight_array: Int16Array;
	public var constraints: Array<TConstraint>;
}

#if js
typedef TVertexArray = {
#else
@:structInit class TVertexArray {
#end
	public var attrib: String;
	public var values: Int16Array;
	public var data: String; // short4norm, short2norm
	@:optional public var padding: Null<Int>;
	@:optional public var size: Null<Int>;
}

#if js
typedef TIndexArray = {
#else
@:structInit class TIndexArray {
#end
	public var values: Uint32Array; // size = 3
	public var material: Int;
	@:optional public var vertex_map: Uint32Array; // size = 3
}

#if js
typedef TLightData = {
#else
@:structInit class TLightData {
#end
	public var name: String;
	public var type: String; // sun, point, spot
	public var color: Float32Array;
	public var strength: FastFloat;
	@:optional public var cast_shadow: Null<Bool>;
	@:optional public var near_plane: Null<FastFloat>;
	@:optional public var far_plane: Null<FastFloat>;
	@:optional public var fov: Null<FastFloat>;
	@:optional public var shadows_bias: Null<FastFloat>;
	@:optional public var shadowmap_size: Null<Int>;
	@:optional public var shadowmap_cube: Null<Bool>; // Omni shadows for point
	@:optional public var spot_size: Null<FastFloat>;
	@:optional public var spot_blend: Null<FastFloat>;
	@:optional public var light_size: Null<FastFloat>; // Shadow soft size
	@:optional public var size: Null<FastFloat>; // Area light
	@:optional public var size_y: Null<FastFloat>;
}

#if js
typedef TCameraData = {
#else
@:structInit class TCameraData {
#end
	public var name: String;
	public var near_plane: FastFloat;
	public var far_plane: FastFloat;
	public var fov: FastFloat;
	@:optional public var clear_color: Float32Array;
	@:optional public var aspect: Null<FastFloat>;
	@:optional public var frustum_culling: Null<Bool>;
	@:optional public var ortho: Float32Array; // Indicates ortho camera, left, right, bottom, top
}

#if js
typedef TMaterialData = {
#else
@:structInit class TMaterialData {
#end
	public var name: String;
	public var shader: String;
	public var contexts: Array<TMaterialContext>;
	@:optional public var skip_context: String;
	@:optional public var override_context: TShaderOverride;
}

#if js
typedef TShaderOverride = {
#else
@:structInit class TShaderOverride {
#end
	@:optional public var cull_mode: String;
	@:optional public var addressing: String;
	@:optional public var filter: String;
	@:optional public var shared_sampler: String;
}

#if js
typedef TMaterialContext = {
#else
@:structInit class TMaterialContext {
#end
	public var name: String;
	@:optional public var depth_read: Null<Bool>;
	@:optional public var bind_constants: Array<TBindConstant>;
	@:optional public var bind_textures: Array<TBindTexture>;
}

#if js
typedef TBindConstant = {
#else
@:structInit class TBindConstant {
#end
	public var name: String;
	@:optional public var vec4Value: Float32Array;
	@:optional public var vec3Value: Float32Array;
	@:optional public var vec2Value: Float32Array;
	@:optional public var floatValue: Null<FastFloat>;
	@:optional public var boolValue: Null<Bool>;
	@:optional public var intValue: Null<Int>;
}

#if js
typedef TBindTexture = {
#else
@:structInit class TBindTexture {
#end
	public var name: String;
	public var file: String;
	@:optional public var format: String; // RGBA32, RGBA64, R8
	@:optional public var generate_mipmaps: Null<Bool>;
	@:optional public var mipmaps: Array<String>; // Reference image names
	@:optional public var u_addressing: String;
	@:optional public var v_addressing: String;
	@:optional public var min_filter: String;
	@:optional public var mag_filter: String;
	@:optional public var mipmap_filter: String;
	@:optional public var source: String; // file, movie
}

#if js
typedef TShaderData = {
#else
@:structInit class TShaderData {
#end
	public var name: String;
	public var next_pass: String;
	public var contexts: Array<TShaderContext>;
}

#if js
typedef TShaderContext = {
#else
@:structInit class TShaderContext {
#end
	public var name: String;
	public var depth_write: Bool;
	public var compare_mode: String;
	public var cull_mode: String;
	public var vertex_elements: Array<TVertexElement>;
	public var vertex_shader: String;
	public var fragment_shader: String;
	@:optional public var geometry_shader: String;
	@:optional public var tesscontrol_shader: String;
	@:optional public var tesseval_shader: String;
	@:optional public var constants: Array<TShaderConstant>;
	@:optional public var texture_units: Array<TTextureUnit>;
	@:optional public var blend_source: String;
	@:optional public var blend_destination: String;
	@:optional public var blend_operation: String;
	@:optional public var alpha_blend_source: String;
	@:optional public var alpha_blend_destination: String;
	@:optional public var alpha_blend_operation: String;
	@:optional public var color_writes_red: Array<Bool>; // Per target masks
	@:optional public var color_writes_green: Array<Bool>;
	@:optional public var color_writes_blue: Array<Bool>;
	@:optional public var color_writes_alpha: Array<Bool>;
	@:optional public var color_attachments: Array<String>; // RGBA32, RGBA64, R8
	@:optional public var depth_attachment: String; // DEPTH32
	@:optional public var conservative_raster: Null<Bool>;
	@:optional public var shader_from_source: Null<Bool>; // Build shader at runtime using fromSource()
}

#if js
typedef TVertexElement = {
#else
@:structInit class TVertexElement {
#end
	public var name: String;
	public var data: String; // "float4", "short2norm"
}

#if js
typedef TShaderConstant = {
#else
@:structInit class TShaderConstant {
#end
	public var name: String;
	public var type: String;
	@:optional public var link: String;
	@:optional public var vec4Value: Float32Array;
	@:optional public var vec3Value: Float32Array;
	@:optional public var vec2Value: Float32Array;
	@:optional public var floatValue: Null<FastFloat>;
	@:optional public var boolValue: Null<Bool>;
	@:optional public var intValue: Null<Int>;
	@:optional public var is_arm_parameter: Null<Bool>;
}

#if js
typedef TTextureUnit = {
#else
@:structInit class TTextureUnit {
#end
	public var name: String;
	@:optional public var is_image: Null<Bool>; // image2D
	@:optional public var link: String;
	@:optional public var addressing_u: String;
	@:optional public var addressing_v: String;
	@:optional public var filter_min: String;
	@:optional public var filter_mag: String;
	@:optional public var mipmap_filter: String;
	@:optional public var default_image_file: String;
	@:optional public var is_arm_parameter: Null<Bool>;
}

#if js
typedef TSpeakerData = {
#else
@:structInit class TSpeakerData {
#end
	public var name: String;
	public var sound: String;
	public var muted: Bool;
	public var loop: Bool;
	public var stream: Bool;
	public var volume: FastFloat;
	public var pitch: FastFloat;
	public var volume_min: FastFloat;
	public var volume_max: FastFloat;
	public var attenuation: FastFloat;
	public var distance_max: FastFloat;
	public var distance_reference: FastFloat;
	public var play_on_start: Bool;
}

#if js
typedef TTerrainData = {
#else
@:structInit class TTerrainData {
#end
	public var name: String;
	public var sectors_x: Int;
	public var sectors_y: Int;
	public var sector_size: FastFloat;
	public var height_scale: FastFloat;
	public var material_ref: String;
}

#if js
typedef TWorldData = {
#else
@:structInit class TWorldData {
#end
	public var name: String;
	public var background_color: Int;
	public var probe: TProbeData;
	@:optional public var sun_direction: Float32Array; // Sky data
	@:optional public var turbidity: Null<FastFloat>;
	@:optional public var ground_albedo: Null<FastFloat>;
	@:optional public var envmap: String;
	@:optional public var nishita_density: Float32Array; // Rayleigh, Mie, ozone
}

#if js
typedef TProbeData = {
#else
@:structInit class TProbeData {
#end
	public var name: String;
	public var type: String; // grid, planar, cubemap
	public var strength: FastFloat;
	@:optional public var irradiance: String; // Reference to TIrradiance blob
	@:optional public var radiance: String;
	@:optional public var radiance_mipmaps: Null<Int>;
}

#if js
typedef TTilesheetAction = {
#else
@:structInit class TTilesheetAction {
#end
	public var name: String;
	public var start: Int;
	public var end: Int;
	public var loop: Bool;
	public var tilesx: Int;
	public var tilesy: Int;
	public var framerate: Int;
	@:optional public var mesh: String; // Optional mesh to swap to when playing this action
	@:optional public var events: Array<TTilesheetEvent>; // Optional events triggered on specific frames
}

#if js
typedef TTilesheetEvent = {
#else
@:structInit class TTilesheetEvent {
#end
	public var name: String; // Event name
	public var frame: Int; // Frame number when event triggers
}

#if js
typedef TTilesheetData = {
#else
@:structInit class TTilesheetData {
#end
	public var actions: Array<TTilesheetAction>;
	public var start_action: String;
	public var flipx: Bool;
	public var flipy: Bool;
}

#if js
typedef TParticleData = {
#else
@:structInit class TParticleData {
#end
	// Format
	public var fps: Int;
	public var name: String;
	public var type: Int; // 0 - Emitter, Hair
	// Arm
	public var auto_start: Bool;
	public var is_unique: Bool;
	public var local_coords: Bool;
	public var loop: Bool;
	// Emission
	public var count: Int;
	// public var hair_length: FastFloat; TODO
	public var frame_start: FastFloat;
	public var frame_end: FastFloat;
	public var lifetime: FastFloat;
	public var lifetime_random: FastFloat;
	public var emit_from: Int; // 0 - Vert, 1 - Face, 2 - Volume
	// Velocity
	public var object_align_factor: Float32Array;
	public var factor_random: FastFloat;
	// Rotation
	public var use_rotations: Bool;
	public var rotation_mode: Int; // 0 - None, 1 - Normal, 2 - Normal-Tangent, 3 - Velocity/Hair, 4 - Global X, 5 - Global Y, 6 - Global Z, 7 - Object X, 8 - Object Y, 9 - Object Z
	public var rotation_factor_random: Float;
	public var phase_factor: Float;
	public var phase_factor_random: Float;
	public var use_dynamic_rotation: Bool;
	// Physics
	public var physics_type: Int; // 0 - No, 1 - Newton
	public var mass: FastFloat;
	// Render
	public var particle_size: FastFloat; // Object scale
	public var size_random: FastFloat; // Random scale
	public var show_emitter: Bool;
	public var instance_object: String; // Object reference
	// Field Weights
	public var weight_gravity: FastFloat;
	public var weight_texture: FastFloat;
	// Textures
	public var texture_slots: Dynamic;
}

#if js
typedef TParticleReference = {
#else
@:structInit class TParticleReference {
#end
	public var name: String;
	public var particle: String;
	public var seed: Int;
}

#if js
typedef TObj = {
#else
@:structInit class TObj {
#end
	public var type: String; // object, mesh_object, light_object, camera_object, speaker_object, decal_object
	public var name: String;
	public var data_ref: String;
	public var transform: TTransform;
	@:optional public var material_refs: Array<String>;
	@:optional public var particle_refs: Array<TParticleReference>;
	@:optional public var render_emitter: Bool;
	@:optional public var is_particle: Null<Bool>; // This object is used as a particle object
	@:optional public var children: Array<TObj>;
	@:optional public var group_ref: String; // instance_type
	@:optional public var lods: Array<TLod>;
	@:optional public var lod_material: Null<Bool>;
	@:optional public var traits: Array<TTrait>;
	@:optional public var properties: Array<TProperty>;
	@:optional public var vertex_groups: Array<TVertex_groups>;
	@:optional public var camera_list: Array<String>;
	@:optional public var constraints: Array<TConstraint>;
	@:optional public var dimensions: Float32Array; // Geometry objects
	@:optional public var object_actions: Array<String>;
	@:optional public var bone_actions: Array<String>;
	@:optional public var anim: TAnimation; // Bone/object animation
	@:optional public var parent: TObj;
	@:optional public var parent_bone: String;
	@:optional public var parent_bone_tail: Float32Array; // Translate from head to tail
	@:optional public var parent_bone_tail_pose: Float32Array;
	@:optional public var parent_bone_connected: Null<Bool>;
	@:optional public var visible: Null<Bool>;
	@:optional public var visible_mesh: Null<Bool>;
	@:optional public var visible_shadow: Null<Bool>;
	@:optional public var mobile: Null<Bool>;
	@:optional public var spawn: Null<Bool>; // Auto add object when creating scene
	@:optional public var local_only: Null<Bool>; // Apply parent matrix
	@:optional public var tilesheet: TTilesheetData; // Embedded tilesheet data
	@:optional public var sampled: Null<Bool>; // Object action
	@:optional public var is_ik_fk_only: Null<Bool>; // Bone IK or FK only
	@:optional public var relative_bone_constraints: Null<Bool>; // Use parent relative bone constraints
}

#if js
typedef TProperty = {
#else
@:structInit class TProperty {
#end
	public var name: String;
	public var value: Dynamic;
}

#if js
typedef TVertex_groups = {
#else
@:structInit class TVertex_groups {
#end
	public var name: String;
	public var value: Dynamic;
}

#if js
typedef TGroup = {
#else
@:structInit class TGroup {
#end
	public var name: String;
	public var instance_offset: Float32Array;
	public var object_refs: Array<String>;
}

#if js
typedef TLod = {
#else
@:structInit class TLod {
#end
	public var object_ref: String; // Empty when limiting draw distance
	public var screen_size: FastFloat; // (0-1) size compared to lod0
}

#if js
typedef TConstraint = {
#else
@:structInit class TConstraint {
#end
	public var name: String;
	public var type: String;
	@:optional public var bone: String; // Bone constraint
	@:optional public var target: String;
	@:optional public var use_x: Null<Bool>;
	@:optional public var use_y: Null<Bool>;
	@:optional public var use_z: Null<Bool>;
	@:optional public var invert_x: Null<Bool>;
	@:optional public var invert_y: Null<Bool>;
	@:optional public var invert_z: Null<Bool>;
	@:optional public var use_offset: Null<Bool>;
	@:optional public var influence: Null<FastFloat>;
}

#if js
typedef TTrait = {
#else
@:structInit class TTrait {
#end
	public var type: String;
	public var class_name: String;
	@:optional public var parameters: Array<String>; // constructor params
	@:optional public var props: Array<Dynamic>; // name - type - value list
}

#if js
typedef TTransform = {
#else
@:structInit class TTransform {
#end
	@:optional public var target: String;
	public var values: Float32Array;
}

#if js
typedef TAnimation = {
#else
@:structInit class TAnimation {
#end
	public var tracks: Array<TTrack>;
	@:optional public var begin: Null<Int>; // Frames, for non-sampled
	@:optional public var end: Null<Int>;
	@:optional public var has_delta: Null<Bool>; // Delta transform
	@:optional public var marker_frames: Uint32Array;
	@:optional public var marker_names: Array<String>;
}

#if js
typedef TAnimationTransform = {
#else
@:structInit class TAnimationTransform {
#end
	public var type: String; // translation, translation_x, ...
	@:optional public var name: String;
	@:optional public var values: Float32Array; // translation
	@:optional public var value: Null<FastFloat>; // translation_x
}

#if js
typedef TTrack = {
#else
@:structInit class TTrack {
#end
	public var target: String;
	public var frames: Uint32Array;
	public var values: Float32Array; // sampled - full matrix transforms, non-sampled - values
	@:optional public var ref_values: Array<Array<String>>; // ref values
}
