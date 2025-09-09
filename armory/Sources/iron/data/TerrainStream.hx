package iron.data;

import haxe.ds.Vector;
import kha.arrays.Int16Array;
import kha.arrays.Uint32Array;
import iron.data.SceneFormat;
import iron.object.Object;
import iron.object.CameraObject;
import iron.object.MeshObject;
import iron.object.Uniforms;
import iron.Scene;

#if arm_terrain

class TerrainStream {

	public var sectors: Array<MeshObject> = [];
	public var heightTextures: Array<kha.Image> = [];
	public var ready = false;
	public var onReady: Void->Void = null;

	var raw: TTerrainData;
	var planes: Array<MeshData> = [];
	var materials: Vector<MaterialData>;

	public function new(raw: TTerrainData) {
		this.raw = raw;

		Data.getMaterial(Scene.active.raw.name, raw.material_ref, function(mat: MaterialData) {
			materials = Vector.fromData([mat]);

			var imagesLoaded = 0;
			var numSectors = raw.sectors_x * raw.sectors_y;
			for (i in 0...numSectors) {
				var j = i + 1;
				var ext = j < 10 ? "0" + j : "" + j;
				Data.getImage("heightmap_" + ext + ".png", function(image: kha.Image) {
					heightTextures[i] = image;
					imagesLoaded++;
					if (imagesLoaded == numSectors) {
						loaded();
					}
				}, true); // Readable
			}
		});
	}

	public function notifyOnReady(f: Void->Void) {
		onReady = f;
		if (ready) onReady();
	}

	function loaded() {
		for (i in 0...4) {
			makePlane(i, raw.sector_size, raw.sector_size, heightTextures[0].width, heightTextures[0].height);
		}

		for (i in 0...raw.sectors_x * raw.sectors_y) {
			makeSector(i);
		}

		iron.App.notifyOnInit(function() {
			Uniforms.externalTextureLinks.push(textureLink);
		});

		ready = true;
		if (onReady != null) onReady();
	}

	function makePlane(index: Int, sizeX: Float, sizeY: Float, vertsX: Int, vertsY: Int) {
		// Pack positions to (-1, 1) range
		var halfX = sizeX / 2;
		var halfY = sizeY / 2;
		var halfZ = raw.height_scale / 2;
		var scalePos = Math.max(halfX, Math.max(halfY, halfZ));
		var inv = 1 / scalePos;

		var posa = new Int16Array(vertsX * vertsY * 4);
		var nora = new Int16Array(vertsX * vertsY * 2);
		var texa = new Int16Array(vertsX * vertsY * 2);
		var inda = new Uint32Array((vertsX - 1) * (vertsY - 1) * 6);
		var stepX = sizeX / (vertsX - 1);
		var stepY = sizeY / (vertsY - 1);
		for (i in 0...vertsX * vertsY) {
			var x = (i % vertsX) * stepX - halfX;
			var y = Std.int(i / vertsX) * stepY - halfY;
			posa[i * 4    ] = Std.int(x * 32767 * inv);
			posa[i * 4 + 1] = Std.int(y * 32767 * inv);
			posa[i * 4 + 2] = Std.int(-halfZ * 32767 * inv);
			nora[i * 2    ] = 0;
			nora[i * 2 + 1] = 0;
			posa[i * 4 + 3] = 32767;
			x = (i % vertsX) / vertsX;
			y = (Std.int(i / vertsX)) / vertsY;
			texa[i * 2    ] = Std.int(x * 32767);
			texa[i * 2 + 1] = Std.int(y * 32767);
		}
		for (i in 0...(vertsX - 1) * (vertsY - 1)) {
			var x = i % (vertsX - 1);
			var y = Std.int(i / (vertsY - 1));
			inda[i * 6    ] = y * vertsX + x;
			inda[i * 6 + 1] = y * vertsX + x + 1;
			inda[i * 6 + 2] = (y + 1) * vertsX + x;
			inda[i * 6 + 3] = y * vertsX + x + 1;
			inda[i * 6 + 4] = (y + 1) * vertsX + x + 1;
			inda[i * 6 + 5] = (y + 1) * vertsX + x;
		}

		// Positions, normals and indices
		var pos: TVertexArray = { attrib: "pos", values: posa, data: "short4norm" };
		var nor: TVertexArray = { attrib: "nor", values: nora, data: "short2norm" };
		var tex: TVertexArray = { attrib: "tex", values: texa, data: "short2norm" };
		var ind: TIndexArray = { material: 0, values: inda };

		var rawmeshData: TMeshData = {
			name: "Terrain",
			vertex_arrays: [pos, nor, tex],
			index_arrays: [ind],
			scale_pos: scalePos,
			scale_tex: 1.0,
			sorting_index: 0
		};

		new MeshData(rawmeshData, function(data: MeshData) {
			planes[index] = data;
			data.geom.calculateAABB();
		});
	}

	function makeSector(index: Int) {
		var object = Scene.active.addMeshObject(planes[0], materials);
		sectors[index] = object;
		object.uid = index;
		object.name = "Terrain." + index;
		object.transform.loc.x = (index % raw.sectors_x) * 2;
		object.transform.loc.y = Std.int(index / raw.sectors_x) * 2;
		object.transform.loc.z = 0;
		object.transform.buildMatrix();
		object.transform.dim.x = raw.sector_size;
		object.transform.dim.y = raw.sector_size;
		object.transform.dim.z = raw.height_scale;
	}

	public function remove() {}

	public function update(camera: CameraObject) {
		if (!ready) return;
	}

	function textureLink(object: Object, mat: MaterialData, link: String): kha.Image {
		if (link == "_TerrainHeight") {
			return heightTextures[object.uid];
		}
		return null;
	}
}

#end
