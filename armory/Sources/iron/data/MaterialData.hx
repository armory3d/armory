package iron.data;

import haxe.ds.Vector;
import iron.data.SceneFormat;
import iron.data.ShaderData;
import iron.object.MeshObject;

class MaterialData {

	static var uidCounter = 0;
	public var uid: Float;
	public var name: String;
	public var raw: TMaterialData;
	public var shader: ShaderData;

	public var contexts: Array<MaterialContext> = null;

	public function new(raw: TMaterialData, done: MaterialData->Void, file = "") {
		uid = ++uidCounter; // Start from 1
		this.raw = raw;
		this.name = raw.name;

		var ref = raw.shader.split("/");
		var object_file = "";
		var data_ref = "";
		if (ref.length == 2) { // File reference
			object_file = ref[0];
			data_ref = ref[1];
		}
		else { // Local data
			object_file = file;
			data_ref = raw.shader;
		}

		Data.getShader(object_file, data_ref, function(b: ShaderData) {
			shader = b;

			// Contexts have to be in the same order as in raw data for now
			contexts = [];
			while (contexts.length < raw.contexts.length) contexts.push(null);
			var contextsLoaded = 0;

			for (i in 0...raw.contexts.length) {
				var c = raw.contexts[i];
				new MaterialContext(c, function(self: MaterialContext) {
					contexts[i] = self;
					contextsLoaded++;
					if (contextsLoaded == raw.contexts.length) done(this);
				});
			}
		}, raw.override_context);
	}

	public static function parse(file: String, name: String, done: MaterialData->Void) {
		Data.getSceneRaw(file, function(format: TSceneFormat) {
			var raw: TMaterialData = Data.getMaterialRawByName(format.material_datas, name);
			if (raw == null) {
				trace('Material data "$name" not found!');
				done(null);
			}
			new MaterialData(raw, done, file);
		});
	}

	public function getContext(name: String): MaterialContext {
		for (c in contexts) {
			// 'mesh' will fetch both 'mesh' and 'meshheight' contexts
			if (c.raw.name.substr(0, name.length) == name) return c;
		}
		return null;
	}
}

class MaterialContext {
	public var raw: TMaterialContext;
	public var textures: Vector<kha.Image> = null;
	public var id = 0;
	static var num = 0;

	public function new(raw: TMaterialContext, done: MaterialContext->Void) {
		this.raw = raw;
		id = num++;

		if (raw.bind_textures != null && raw.bind_textures.length > 0) {

			textures = new Vector(raw.bind_textures.length);
			var texturesLoaded = 0;

			for (i in 0...raw.bind_textures.length) {
				var tex = raw.bind_textures[i];

				if (tex.file == "" || tex.source == "movie") { // Empty texture
					texturesLoaded++;
					if (texturesLoaded == raw.bind_textures.length) done(this);
					continue;
				}

				Data.getImage(tex.file, function(image: kha.Image) {
					textures[i] = image;
					texturesLoaded++;

					// Set mipmaps
					if (tex.mipmaps != null) {
						var mipmaps: Array<kha.Image> = [];
						while (mipmaps.length < tex.mipmaps.length) mipmaps.push(null);
						var mipmapsLoaded = 0;

						for (j in 0...tex.mipmaps.length) {
							var name = tex.mipmaps[j];

							Data.getImage(name, function(mipimg: kha.Image) {
								mipmaps[j] = mipimg;
								mipmapsLoaded++;

								if (mipmapsLoaded == tex.mipmaps.length) {
									image.setMipmaps(mipmaps);
									tex.mipmaps = null;
									tex.generate_mipmaps = false;

									if (texturesLoaded == raw.bind_textures.length) done(this);
								}
							});
						}
					}
					else if (tex.generate_mipmaps == true && image != null) {
						image.generateMipmaps(1000);
						tex.mipmaps = null;
						tex.generate_mipmaps = false;

						if (texturesLoaded == raw.bind_textures.length) done(this);
					}
					else if (texturesLoaded == raw.bind_textures.length) done(this);

				}, false, tex.format != null ? tex.format : "RGBA32");
			}
		}
		else done(this);
	}

	public function setTextureParameters(g: kha.graphics4.Graphics, textureIndex: Int, context: ShaderContext, unitIndex: Int) {
		// This function is called by MeshObject for samplers set using material context
		context.setTextureParameters(g, unitIndex, raw.bind_textures[textureIndex]);
	}
}
