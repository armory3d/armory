package iron.data;

import haxe.Json;
import kha.arrays.Float32Array;
import iron.math.Vec4;
import iron.data.SceneFormat;
import iron.system.ArmPack;
using StringTools;

class WorldData {

	public var name: String;
	public var raw: TWorldData;
	public var envmap: kha.Image;
	public var probe: Probe;

	static var emptyIrr: Float32Array = null;

	public function new(raw: TWorldData, done: WorldData->Void) {
		this.raw = raw;
		this.name = raw.name;

		// Parse probes
		if (raw.probe != null) {
			new Probe(raw.probe, function(self: Probe) {
				probe = self;
				#if arm_skip_envmap
				done(this);
				#else
				loadEnvmap(done);
				#end
			});
		}
		else {
			#if arm_skip_envmap
			done(this);
			#else
			loadEnvmap(done);
			#end
		}
	}

	public function loadEnvmap(done: WorldData->Void) {
		if (raw.envmap != null) {
			Data.getImage(raw.envmap, function(image: kha.Image) {
				envmap = image;
				done(this);
			});
		}
		else done(this);
	}

	public static function parse(name: String, id: String, done: WorldData->Void) {
		Data.getSceneRaw(name, function(format: TSceneFormat) {
			var raw: TWorldData = Data.getWorldRawByName(format.world_datas, id);
			if (raw == null) {
				trace('World data "$id" not found!');
				done(null);
			}
			new WorldData(raw, done);
		});
	}

	public static function getEmptyIrradiance(): Float32Array {
		if (emptyIrr == null) {
			emptyIrr = new Float32Array(28);
			for (i in 0...emptyIrr.length) emptyIrr.set(i, 0.0);
		}
		return emptyIrr;
	}
}

class Probe {

	public var raw: TProbeData;
	public var radiance: kha.Image;
	public var radianceMipmaps: Array<kha.Image> = [];
	public var irradiance: Float32Array;

	public function new(raw: TProbeData, done: Probe->Void) {
		this.raw = raw;

		setIrradiance(function(irr: Float32Array) {
			irradiance = irr;
			if (raw.radiance != null) {
				Data.getImage(raw.radiance, function(rad: kha.Image) {
					radiance = rad;
					while (radianceMipmaps.length < raw.radiance_mipmaps) radianceMipmaps.push(null);
					var dot = raw.radiance.lastIndexOf(".");
					var ext = raw.radiance.substring(dot);
					var base = raw.radiance.substring(0, dot);

					var mipsLoaded = 0;
					for (i in 0...raw.radiance_mipmaps) {
						Data.getImage(base + "_" + i + ext, function(mipimg: kha.Image) {
							radianceMipmaps[i] = mipimg;
							mipsLoaded++;

							if (mipsLoaded == raw.radiance_mipmaps) {
								radiance.setMipmaps(radianceMipmaps);
								done(this);
							}
						}, true); // Readable
					}
				});
			}
			else done(this);
		});
	}

	function setIrradiance(done: Float32Array->Void) {
		// Parse probe data
		if (raw.irradiance == null) {
			done(WorldData.getEmptyIrradiance());
		}
		else {
			var ext = raw.irradiance.endsWith(".json") ? "" : ".arm";
			Data.getBlob(raw.irradiance + ext, function(b: kha.Blob) {
				var irradianceParsed: TSceneFormat = ext == "" ?
					Json.parse(b.toString()) :
					ArmPack.decode(b.toBytes());
				var irr = new Float32Array(28); // Align to mult of 4 - 27->28
				for (i in 0...27) irr[i] = irradianceParsed.irradiance[i];
				done(irr);
			});
		}
	}
}
