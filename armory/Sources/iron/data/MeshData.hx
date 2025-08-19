package iron.data;

import kha.graphics4.Usage;
import kha.graphics4.VertexData;
import kha.arrays.Int16Array;
import kha.arrays.Uint32Array;
import iron.data.SceneFormat;

class MeshData {

	public var name: String;
	public var sortingIndex: Int;
	public var raw: TMeshData;
	public var format: TSceneFormat;
	public var geom: Geometry;
	public var start = 0; // Batched
	public var count = -1;
	public var refcount = 0; // Number of users
	public var handle: String; // Handle used to retrieve this object in Data
	public var scalePos: kha.FastFloat = 1.0;
	public var scaleTex: kha.FastFloat = 1.0;
	public var isSkinned: Bool;

	public function new(raw: TMeshData, done: MeshData->Void) {
		this.raw = raw;
		this.name = raw.name;
		this.sortingIndex = raw.sorting_index;

		if (raw.scale_pos != null) scalePos = raw.scale_pos;
		if (raw.scale_tex != null) scaleTex = raw.scale_tex;

		// Mesh data
		var indices: Array<Uint32Array> = [];
		var materialIndices: Array<Int> = [];
		for (ind in raw.index_arrays) {
			indices.push(ind.values);
			materialIndices.push(ind.material);
		}

		// Skinning
		isSkinned = raw.skin != null;

		// Prepare vertex array for skinning and fill size data
		var vertexArrays = raw.vertex_arrays;
		if (isSkinned) {
			vertexArrays.push({ attrib: "bone", values: null, data: "short4norm" });
			vertexArrays.push({ attrib: "weight", values: null, data: "short4norm" });
		}
		for (i in 0...vertexArrays.length) {
			vertexArrays[i].size = getVertexSize(vertexArrays[i].data, getPadding(vertexArrays[i].padding));
		}

		// Usage, also used for instanced data
		var parsedUsage = Usage.StaticUsage;
		if (raw.dynamic_usage != null && raw.dynamic_usage == true) parsedUsage = Usage.DynamicUsage;
		var usage = parsedUsage;

		if (isSkinned) {
			var bonea = null;
			var weighta = null;
			var vertex_length = Std.int(vertexArrays[0].values.length / vertexArrays[0].size);
			var l = vertex_length * 4;
			bonea = new Int16Array(l);
			weighta = new Int16Array(l);

			var index = 0;
			var ai = 0;
			for (i in 0...vertex_length) {
				var boneCount = raw.skin.bone_count_array[i];
				for (j in index...(index + boneCount)) {
					bonea[ai] = raw.skin.bone_index_array[j];
					weighta[ai] = raw.skin.bone_weight_array[j];
					ai++;
				}
				// Fill unused weights
				for (j in boneCount...4) {
					bonea[ai] = 0;
					weighta[ai] = 0;
					ai++;
				}
				index += boneCount;
			}
			vertexArrays[vertexArrays.length - 2].values = bonea;
			vertexArrays[vertexArrays.length - 1].values = weighta;
		}

		// Make vertex buffers
		geom = new Geometry(this, indices, materialIndices, usage);
		geom.name = name;

		done(this);
	}

	public function delete() {
		geom.delete();
	}

	public static function parse(name: String, id: String, done: MeshData->Void) {
		Data.getSceneRaw(name, function(format: TSceneFormat) {
			var raw: TMeshData = Data.getMeshRawByName(format.mesh_datas, id);
			if (raw == null) {
				trace('Mesh data "$id" not found!');
				done(null);
			}

			new MeshData(raw, function(dat: MeshData) {
				dat.format = format;
				// Skinned
				#if arm_skin
				if (raw.skin != null) {
					dat.geom.skinBoneCounts = raw.skin.bone_count_array;
					dat.geom.skinBoneIndices = raw.skin.bone_index_array;
					dat.geom.skinBoneWeights = raw.skin.bone_weight_array;
					dat.geom.skeletonBoneRefs = raw.skin.bone_ref_array;
					dat.geom.skeletonBoneLens = raw.skin.bone_len_array;
					dat.geom.initSkeletonTransforms(raw.skin.transformsI);
				}
				#end
				done(dat);
			});
		});
	}

	function getVertexSize(vertex_data: String, padding: Int = 0): Int {
		switch (vertex_data) {
			case "short4norm": return 4 - padding;
			case "short2norm": return 2 - padding;
			default: return 0;
		}
	}

	inline function getPadding(padding: Null<Int>): Int {
		return padding != null ? padding : 0;
	}
}

