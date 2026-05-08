package iron.data;

import haxe.Json;
import iron.data.SceneFormat;
import iron.system.ArmPack;
import iron.system.Lz4;
using StringTools;

// Global data list and asynchronous data loading
class Data {

	public static var cachedSceneRaws: Map<String, TSceneFormat> = new Map();
	public static var cachedMeshes: Map<String, MeshData> = new Map();
	public static var cachedLights: Map<String, LightData> = new Map();
	public static var cachedCameras: Map<String, CameraData> = new Map();
	public static var cachedMaterials: Map<String, MaterialData> = new Map();
	public static var cachedParticles: Map<String, ParticleData> = new Map();
	public static var cachedWorlds: Map<String, WorldData> = new Map();
	public static var cachedShaders: Map<String, ShaderData> = new Map();
	#if rp_probes
	public static var cachedProbes: Map<String, ProbeData> = new Map();
	#end

	public static var cachedBlobs: Map<String, kha.Blob> = new Map();
	public static var cachedImages: Map<String, kha.Image> = new Map();
	#if arm_audio
	public static var cachedSounds: Map<String, kha.Sound> = new Map();
	#end
	public static var cachedVideos: Map<String, kha.Video> = new Map();
	public static var cachedFonts: Map<String, kha.Font> = new Map();

	public static var assetsLoaded = 0;
	static var loadingMeshes: Map<String, Array<MeshData->Void>> = new Map();
	static var loadingLights: Map<String, Array<LightData->Void>> = new Map();
	static var loadingCameras: Map<String, Array<CameraData->Void>> = new Map();
	static var loadingMaterials: Map<String, Array<MaterialData->Void>> = new Map();
	static var loadingParticles: Map<String, Array<ParticleData->Void>> = new Map();
	static var loadingWorlds: Map<String, Array<WorldData->Void>> = new Map();
	static var loadingShaders: Map<String, Array<ShaderData->Void>> = new Map();
	static var loadingSceneRaws: Map<String, Array<TSceneFormat->Void>> = new Map();
	#if rp_probes
	static var loadingProbes: Map<String, Array<ProbeData->Void>> = new Map();
	#end
	static var loadingBlobs: Map<String, Array<kha.Blob->Void>> = new Map();
	static var loadingImages: Map<String, Array<kha.Image->Void>> = new Map();
	#if arm_audio
	static var loadingSounds: Map<String, Array<kha.Sound->Void>> = new Map();
	#end
	static var loadingVideos: Map<String, Array<kha.Video->Void>> = new Map();
	static var loadingFonts: Map<String, Array<kha.Font->Void>> = new Map();

	#if krom_windows
	public static inline var sep = "\\";
	#else
	public static inline var sep = "/";
	#end

	#if arm_data_dir
	#if krom_android
	public static var dataPath = "data" + sep;
	#else
	public static var dataPath = "." + sep + "data" + sep;
	#end
	#else
	public static var dataPath = "";
	#end

	public function new() {}

	public static function deleteAll() {
		for (c in cachedMeshes) c.delete();
		cachedMeshes = new Map();
		for (c in cachedShaders) c.delete();
		cachedShaders = new Map();
		cachedSceneRaws = new Map();
		cachedLights = new Map();
		cachedCameras = new Map();
		cachedMaterials = new Map();
		cachedParticles = new Map();
		cachedWorlds = new Map();
		if (RenderPath.active != null) RenderPath.active.unload();

		for (c in cachedBlobs) c.unload();
		cachedBlobs = new Map();
		for (c in cachedImages) c.unload();
		cachedImages = new Map();
		#if arm_audio
		for (c in cachedSounds) c.unload();
		cachedSounds = new Map();
		#end
		for (c in cachedVideos) c.unload();
		cachedVideos = new Map();
		for (c in cachedFonts) c.unload();
		cachedFonts = new Map();
	}

	public static function getMesh(file: String, name: String, done: MeshData->Void) {
		var handle = file + name;
		var cached = cachedMeshes.get(handle);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingMeshes.get(handle);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingMeshes.set(handle, [done]);

		MeshData.parse(file, name, function(b: MeshData) {
			cachedMeshes.set(handle, b);
			b.handle = handle;
			for (f in loadingMeshes.get(handle)) f(b);
			loadingMeshes.remove(handle);
		});
	}

	public static function deleteMesh(handle: String) {
		// Remove cached mesh
		var mesh = cachedMeshes.get(handle);
		if (mesh == null) return;
		mesh.delete();
		cachedMeshes.remove(handle);
	}

	public static function getLight(file: String, name: String, done: LightData->Void) {
		var handle = file + name;
		var cached = cachedLights.get(handle);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingLights.get(handle);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingLights.set(handle, [done]);

		LightData.parse(file, name, function(b: LightData) {
			cachedLights.set(handle, b);
			for (f in loadingLights.get(handle)) f(b);
			loadingLights.remove(handle);
		});
	}

	#if rp_probes
	public static function getProbe(file: String, name: String, done: ProbeData->Void) {
		var handle = file + name;
		var cached = cachedProbes.get(handle);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingProbes.get(handle);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingProbes.set(handle, [done]);

		ProbeData.parse(file, name, function(b: ProbeData) {
			cachedProbes.set(handle, b);
			for (f in loadingProbes.get(handle)) f(b);
			loadingProbes.remove(handle);
		});
	}
	#end

	public static function getCamera(file: String, name: String, done: CameraData->Void) {
		var handle = file + name;
		var cached = cachedCameras.get(handle);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingCameras.get(handle);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingCameras.set(handle, [done]);

		CameraData.parse(file, name, function(b: CameraData) {
			cachedCameras.set(handle, b);
			for (f in loadingCameras.get(handle)) f(b);
			loadingCameras.remove(handle);
		});
	}

	public static function getMaterial(file: String, name: String, done: MaterialData->Void) {
		var handle = file + name;
		var cached = cachedMaterials.get(handle);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingMaterials.get(handle);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingMaterials.set(handle, [done]);

		MaterialData.parse(file, name, function(b: MaterialData) {
			cachedMaterials.set(handle, b);
			for (f in loadingMaterials.get(handle)) f(b);
			loadingMaterials.remove(handle);
		});
	}

	public static function getParticle(file: String, name: String, done: ParticleData->Void) {
		var handle = file + name;
		var cached = cachedParticles.get(handle);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingParticles.get(handle);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingParticles.set(handle, [done]);

		ParticleData.parse(file, name, function(b: ParticleData) {
			cachedParticles.set(handle, b);
			for (f in loadingParticles.get(handle)) f(b);
			loadingParticles.remove(handle);
		});
	}

	public static function getWorld(file: String, name: String, done: WorldData->Void) {
		if (name == null) { // No world defined in scene
			done(null);
			return;
		}

		var handle = file + name;
		var cached = cachedWorlds.get(handle);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingWorlds.get(handle);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingWorlds.set(handle, [done]);

		WorldData.parse(file, name, function(b: WorldData) {
			cachedWorlds.set(handle, b);
			for (f in loadingWorlds.get(handle)) f(b);
			loadingWorlds.remove(handle);
		});
	}

	public static function getShader(file: String, name: String, done: ShaderData->Void, overrideContext: TShaderOverride = null) {
		// Only one context override per shader data for now
		var cacheName = name;
		if (overrideContext != null) cacheName += "2";
		var cached = cachedShaders.get(cacheName); // Shader must have unique name
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingShaders.get(cacheName);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingShaders.set(cacheName, [done]);

		ShaderData.parse(file, name, function(b: ShaderData) {
			cachedShaders.set(cacheName, b);
			for (f in loadingShaders.get(cacheName)) f(b);
			loadingShaders.remove(cacheName);
		}, overrideContext);
	}

	public static function getSceneRaw(file: String, done: TSceneFormat->Void) {
		var cached = cachedSceneRaws.get(file);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingSceneRaws.get(file);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingSceneRaws.set(file, [done]);

		// If no extension specified, set to .arm
		var compressed = file.endsWith(".lz4");
		var isJson = file.endsWith(".json");
		var ext = (compressed || isJson || file.endsWith(".arm")) ? "" : ".arm";

		getBlob(file + ext, function(b: kha.Blob) {
			var parsed: TSceneFormat = null;

			#if arm_compress
			if (compressed) {
				var bytes = b.toBytes();

				// First 8 bytes contain data size for decoding
				var packedSize = haxe.Int64.toInt(bytes.getInt64(0));

				parsed = ArmPack.decode(Lz4.decode(bytes.sub(8, bytes.length - 8), packedSize));
			}

			else #end if (isJson) {
				var s = b.toString();
				parsed = s.charAt(0) == "{" ? Json.parse(s) : ArmPack.decode(b.toBytes());
			}
			else {
				parsed = ArmPack.decode(b.toBytes());
			}

			returnSceneRaw(file, parsed);
		});
	}

	static function returnSceneRaw(file: String, parsed: TSceneFormat) {
		cachedSceneRaws.set(file, parsed);
		for (f in loadingSceneRaws.get(file)) f(parsed);
		loadingSceneRaws.remove(file);
	}

	public static function getMeshRawByName(datas: Array<TMeshData>, name: String): TMeshData {
		if (name == "") return datas[0];
		for (dat in datas) if (dat.name == name) return dat;
		return null;
	}

	public static function getLightRawByName(datas: Array<TLightData>, name: String): TLightData {
		if (name == "") return datas[0];
		for (dat in datas) if (dat.name == name) return dat;
		return null;
	}

	#if rp_probes
	public static function getProbeRawByName(datas: Array<TProbeData>, name: String): TProbeData {
		if (name == "") return datas[0];
		for (dat in datas) if (dat.name == name) return dat;
		return null;
	}
	#end

	public static function getCameraRawByName(datas: Array<TCameraData>, name: String): TCameraData {
		if (name == "") return datas[0];
		for (dat in datas) if (dat.name == name) return dat;
		return null;
	}

	public static function getMaterialRawByName(datas: Array<TMaterialData>, name: String): TMaterialData {
		if (name == "") return datas[0];
		for (dat in datas) if (dat.name == name) return dat;
		return null;
	}

	public static function getParticleRawByName(datas: Array<TParticleData>, name: String): TParticleData {
		if (name == "") return datas[0];
		for (dat in datas) if (dat.name == name) return dat;
		return null;
	}

	public static function getWorldRawByName(datas: Array<TWorldData>, name: String): TWorldData {
		if (name == "") return datas[0];
		for (dat in datas) if (dat.name == name) return dat;
		return null;
	}

	public static function getShaderRawByName(datas: Array<TShaderData>, name: String): TShaderData {
		if (name == "") return datas[0];
		for (dat in datas) if (dat.name == name) return dat;
		return null;
	}

	#if arm_audio
	public static function getSpeakerRawByName(datas: Array<TSpeakerData>, name: String): TSpeakerData {
		if (name == "") return datas[0];
		for (dat in datas) if (dat.name == name) return dat;
		return null;
	}
	#end

	// Raw assets
	public static function getBlob(file: String, done: kha.Blob->Void) {
		var cached = cachedBlobs.get(file); // Is already cached
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingBlobs.get(file); // Is already being loaded
		if (loading != null) {
			loading.push(done);
			//return;
		}

		loadingBlobs.set(file, [done]); // Start loading

		kha.Assets.loadBlobFromPath(resolvePath(file), function(b: kha.Blob) {
			cachedBlobs.set(file, b);
			for (f in loadingBlobs.get(file)) f(b);
			loadingBlobs.remove(file);
			assetsLoaded++;
		});
	}

	public static function deleteBlob(handle: String) {
		var blob = cachedBlobs.get(handle);
		if (blob == null) return;
		blob.unload();
		cachedBlobs.remove(handle);
	}

	public static function getImage(file: String, done: kha.Image->Void, readable = false, format = "RGBA32") {
		#if (cpp || hl || arm_use_k_images)
		if (!file.endsWith(".k")) {
			file = file.substring(0, file.length - 4) + ".k";
		}
		#end

		var cached = cachedImages.get(file);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingImages.get(file);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingImages.set(file, [done]);

		#if arm_image_embed
		var imageBlob = cachedBlobs.get(file);
		if (imageBlob != null) {
			kha.Image.fromEncodedBytes(imageBlob.bytes, ".k", function(b: kha.Image) {
				cachedImages.set(file, b);
				for (f in loadingImages.get(file)) f(b);
				loadingImages.remove(file);
				assetsLoaded++;
			}, null, readable);
			return;
		}
		#end

		kha.Assets.loadImageFromPath(resolvePath(file), readable, function(b: kha.Image) {
			cachedImages.set(file, b);
			for (f in loadingImages.get(file)) f(b);
			loadingImages.remove(file);
			assetsLoaded++;
		});
	}

	public static function deleteImage(handle: String) {
		var image = cachedImages.get(handle);
		if (image == null) return;
		image.unload();
		cachedImages.remove(handle);
	}

	/**
	  Load sound file from disk into ram.
	  @param	file A String matching the file name of the sound file on disk.
	  @param	done Completion handler function to do something after the sound is loaded.
	 */
	#if arm_audio
	public static function getSound(file: String, done: kha.Sound->Void) {
		#if arm_soundcompress
		if (file.endsWith(".wav")) file = file.substring(0, file.length - 4) + ".ogg";
		#end

		var cached = cachedSounds.get(file);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingSounds.get(file);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingSounds.set(file, [done]);

		kha.Assets.loadSoundFromPath(resolvePath(file), function(b: kha.Sound) {
			#if arm_soundcompress
			b.uncompress(function () {
			#end
				cachedSounds.set(file, b);
				for (f in loadingSounds.get(file)) f(b);
				loadingSounds.remove(file);
				assetsLoaded++;
			#if arm_soundcompress
			});
			#end
		});
	}

	public static function deleteSound(handle: String) {
		var sound = cachedSounds.get(handle);
		if (sound == null) return;
		sound.unload();
		cachedSounds.remove(handle);
	}
	#end // arm_audio

	public static function getVideo(file: String, done: kha.Video->Void) {
		#if (cpp || hl)
		file = file.substring(0, file.length - 4) + ".avi";
		#elseif krom
		file = file.substring(0, file.length - 4) + ".webm";
		#end
		var cached = cachedVideos.get(file);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingVideos.get(file);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingVideos.set(file, [done]);

		kha.Assets.loadVideoFromPath(resolvePath(file), function(b: kha.Video) {
			cachedVideos.set(file, b);
			for (f in loadingVideos.get(file)) f(b);
			loadingVideos.remove(file);
			assetsLoaded++;
		});
	}

	public static function deleteVideo(handle: String) {
		var video = cachedVideos.get(handle);
		if (video == null) return;
		video.unload();
		cachedVideos.remove(handle);
	}

	public static function getFont(file: String, done: kha.Font->Void) {
		var cached = cachedFonts.get(file);
		if (cached != null) {
			done(cached);
			return;
		}

		var loading = loadingFonts.get(file);
		if (loading != null) {
			loading.push(done);
			return;
		}

		loadingFonts.set(file, [done]);

		kha.Assets.loadFontFromPath(resolvePath(file), function(b: kha.Font) {
			cachedFonts.set(file, b);
			for (f in loadingFonts.get(file)) f(b);
			loadingFonts.remove(file);
			assetsLoaded++;
		});
	}

	public static function deleteFont(handle: String) {
		var font = cachedFonts.get(handle);
		if (font == null) return;
		font.unload();
		cachedFonts.remove(handle);
	}

	public static function isAbsolute(file: String): Bool {
		return file.charAt(0) == "/" || file.charAt(1) == ":" || file.charAt(4) == ":" || (file.charAt(0) == "\\" && file.charAt(1) == "\\");
	}

	static inline function isUp(file: String): Bool {
		return file.charAt(0) == "." && file.charAt(1) == ".";
	}

	/**
	  Extract filename from path.
	*/
	static inline function baseName(path: String): String {
		var slash = path.lastIndexOf(sep);
		return slash >= 0 ? path.substr(slash + 1) : path;
	}

	static inline function resolvePath(file: String): String {
		if (isAbsolute(file) || isUp(file)) return file;
		#if arm_data_dir
		return dataPath + file;
		#else
		return baseName(file);
		#end
	}
}
