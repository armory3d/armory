package armory.renderpath;

import iron.RenderPath;
import iron.object.LightObject;

import armory.math.Helper;

class Inc {
	static var path: RenderPath;
	public static var superSample = 1.0;

	static var pointIndex = 0;
	static var spotIndex = 0;
	static var lastFrame = -1;

	#if (rp_voxels && arm_config)
	static var voxelsCreated = false;
	#end

	public static function init(_path: RenderPath) {
		path = _path;

		#if arm_config
		var config = armory.data.Config.raw;
		for (l in iron.Scene.active.lights) {
			l.data.raw.shadowmap_size = l.data.raw.type == "sun" ?
				config.rp_shadowmap_cascade :
				config.rp_shadowmap_cube;
		}
		superSample = config.rp_supersample;
		#else

		#if (rp_supersampling == 1.5)
		superSample = 1.5;
		#elseif (rp_supersampling == 2)
		superSample = 2.0;
		#elseif (rp_supersampling == 4)
		superSample = 4.0;
		#end

		#end
	}

	#if arm_shadowmap_atlas
	public static function updatePointLightAtlasData(): Void {
		var atlas = ShadowMapAtlas.shadowMapAtlases.get(ShadowMapAtlas.shadowMapAtlasName("point"));
		if (atlas != null) {
			if(LightObject.pointLightsData == null) {
				LightObject.pointLightsData = new kha.arrays.Float32Array(
					LightObject.maxLightsCluster * ShadowMapTile.tilesLightType("point") * 4 ); // max possible visible lights * 6 or 2 (faces) * 4 (xyzw)
			}

			var n = iron.Scene.active.lights.length > LightObject.maxLightsCluster ? LightObject.maxLightsCluster : iron.Scene.active.lights.length;
			var i = 0;
			var j = 0;
			for (light in iron.Scene.active.lights) {
				if (i >= n)
					break;
				if (LightObject.discardLightCulled(light)) continue;
				if (light.data.raw.type == "point") {
					if (!light.data.raw.cast_shadow) {
						j += 4 * 6;
						continue;
					}
					for(k in 0...6) {
						LightObject.pointLightsData[j	 ] = light.tileOffsetX[k]; // posx
						LightObject.pointLightsData[j + 1] = light.tileOffsetY[k]; // posy
						LightObject.pointLightsData[j + 2] = light.tileScale[k]; // tile scale factor relative to atlas
						LightObject.pointLightsData[j + 3] = 0; // padding
						j += 4;
					}
				}
				i++;
			}
		}
	}

	public static function bindShadowMapAtlas() {
		for (atlas in ShadowMapAtlas.shadowMapAtlases) {
			path.bindTarget(atlas.target, atlas.target);
		}
	}

	static function getShadowMapAtlas(atlas:ShadowMapAtlas):String {
		inline function createDepthTarget(name: String, size: Int) {
			var t = new RenderTargetRaw();
			t.name = name;
			t.width = t.height = size;
			t.format = "DEPTH16";
			return path.createRenderTarget(t);
		}

		var rt = path.renderTargets.get(atlas.target);
		// Create shadowmap atlas texture on the fly and replace existing on size change
		if (rt == null) {
			rt = createDepthTarget(atlas.target, atlas.sizew);
		}
		else if (atlas.updateRenderTarget) {
			atlas.updateRenderTarget = false;
			// Resize shadow map
			rt.unload();
			rt = createDepthTarget(atlas.target, atlas.sizew);
		}
		return atlas.target;
	}

	public static function drawShadowMapAtlas() {
		#if rp_shadowmap
		#if rp_probes
		// Share shadow map with probe
		if (lastFrame == RenderPath.active.frame)
			return;
		lastFrame = RenderPath.active.frame;
		#end
		// add new lights to the atlases
		#if arm_debug
		beginShadowsLogicProfile();
		// reset data on rejected lights
		for (atlas in ShadowMapAtlas.shadowMapAtlases) {
			atlas.rejectedLights = [];
		}
		#end
		for (light in iron.Scene.active.lights) {
			if (!light.lightInAtlas && !light.culledLight && light.visible && light.shadowMapScale > 0.0
				&& light.data.raw.strength > 0.0 && light.data.raw.cast_shadow) {
				ShadowMapAtlas.addLight(light);
			}
		}
		// update point light data before rendering
		updatePointLightAtlasData();

		for (atlas in ShadowMapAtlas.shadowMapAtlases) {
			var tilesToRemove = [];
			#if arm_shadowmap_atlas_lod
			var tilesToChangeSize = [];
			#end

			var shadowmap = getShadowMapAtlas(atlas);
			path.setTargetStream(shadowmap);
			path.clearTarget(null, 1.0);

			for (tile in atlas.activeTiles) {
				if (tile.light == null || !tile.light.visible || tile.light.culledLight
					|| !tile.light.data.raw.cast_shadow || tile.light.data.raw.strength == 0) {
					tile.unlockLight = true;
					tilesToRemove.push(tile);
					continue;
				}

				#if arm_shadowmap_atlas_lod
				var newTileSize = atlas.getTileSize(tile.light.shadowMapScale);
				if (newTileSize != tile.size) {
					if (newTileSize == 0) {
						tile.unlockLight = true;
						tilesToRemove.push(tile);
						continue;
					}
					// queue for size change
					tile.newTileSize = newTileSize;
					tilesToChangeSize.push(tile);
				}
				#end
				// set the tile offset for this tile and every linked tile to this one
				var j = 0;
				tile.forEachTileLinked(function (lTile) {
					tile.light.tileOffsetX[j] = lTile.coordsX / atlas.sizew;
					tile.light.tileOffsetY[j] = lTile.coordsY / atlas.sizew;
					tile.light.tileScale[j] = lTile.size / atlas.sizew;
					j++;
				});
				// set shadowmap size for uniform
				tile.light.data.raw.shadowmap_size = atlas.sizew;

				path.light = tile.light;

				var face = 0;
				var faces = ShadowMapTile.tilesLightType(tile.light.data.raw.type);

				#if arm_debug
				beginShadowsRenderProfile();
				#end
				tile.forEachTileLinked(function (lTile) {
					if (faces > 1) {
						#if arm_csm
						switch (tile.light.data.raw.type) {
							case "sun": tile.light.setCascade(iron.Scene.active.camera, face);
							case "point": path.currentFace = face;
						}
						#else
						path.currentFace = face;
						#end
						face++;
					}
					path.setCurrentViewportWithOffset(lTile.size, lTile.size, lTile.coordsX, lTile.coordsY);

					path.drawMeshesStream("shadowmap");
				});
				#if arm_debug
				endShadowsRenderProfile();
				#end

				path.currentFace = -1;
			}
			path.endStream();

			#if arm_shadowmap_atlas_lod
			for (tile in tilesToChangeSize) {
				tilesToRemove.push(tile);

				var newTile = ShadowMapTile.assignTiles(tile.light, atlas, tile);
				if (newTile != null)
					atlas.activeTiles.push(newTile);
			}
			// update point light data after changing size of tiles to avoid render issues
			updatePointLightAtlasData();
			#end

			for (tile in tilesToRemove) {
				atlas.activeTiles.remove(tile);
				tile.freeTile();
			}
		}
		#if arm_debug
		endShadowsLogicProfile();
		#end
		#end //rp_shadowmap
	}

	#else
	public static function bindShadowMap() {
		for (l in iron.Scene.active.lights) {
			if (!l.visible || l.data.raw.type != "sun") continue;
			var n = "shadowMap";
			path.bindTarget(n, n);
			break;
		}
		for (i in 0...pointIndex) {
			var n = "shadowMapPoint[" + i + "]";
			path.bindTarget(n, n);
		}
		for (i in 0...spotIndex) {
			var n = "shadowMapSpot[" + i + "]";
			path.bindTarget(n, n);
		}
	}

	static function shadowMapName(light: LightObject): String {
		switch (light.data.raw.type) {
			case "sun":
				return "shadowMap";
			case "point":
				return "shadowMapPoint[" + pointIndex + "]";
			default:
				return "shadowMapSpot[" + spotIndex + "]";
		}
	}

	static function getShadowMap(l: iron.object.LightObject): String {
		var target = shadowMapName(l);
		var rt = path.renderTargets.get(target);
		// Create shadowmap on the fly
		if (rt == null) {
			if (path.light.data.raw.shadowmap_cube) {
				// Cubemap size
				var size = path.light.data.raw.shadowmap_size;
				var t = new RenderTargetRaw();
				t.name = target;
				t.width = size;
				t.height = size;
				t.format = "DEPTH16";
				t.is_cubemap = true;
				rt = path.createRenderTarget(t);
			}
			else { // Non-cube sm
				var sizew = path.light.data.raw.shadowmap_size;
				var sizeh = sizew;
				#if arm_csm // Cascades - atlas on x axis
				if (l.data.raw.type == "sun") {
					sizew = sizew * iron.object.LightObject.cascadeCount;
				}
				#end
				var t = new RenderTargetRaw();
				t.name = target;
				t.width = sizew;
				t.height = sizeh;
				t.format = "DEPTH16";
				rt = path.createRenderTarget(t);
			}
		}
		return target;
	}

	public static function drawShadowMap() {
		#if (rp_shadowmap)

		#if rp_probes
		// Share shadow map with probe
		if (lastFrame == RenderPath.active.frame) return;
		lastFrame = RenderPath.active.frame;
		#end

		pointIndex = 0;
		spotIndex = 0;
		for (l in iron.Scene.active.lights) {
			if (!l.visible) continue;

			path.light = l;
			var shadowmap = Inc.getShadowMap(l);
			var faces = l.data.raw.shadowmap_cube ? 6 : 1;
			for (i in 0...faces) {
				if (faces > 1) path.currentFace = i;
				path.setTarget(shadowmap);
				path.clearTarget(null, 1.0);
				if (l.data.raw.cast_shadow) {
					path.drawMeshes("shadowmap");
				}
			}
			path.currentFace = -1;

			if (l.data.raw.type == "point") pointIndex++;
			else if (l.data.raw.type == "spot" || l.data.raw.type == "area") spotIndex++;
		}

		#end // rp_shadowmap
	}
	#end

	public static function applyConfig() {
		#if arm_config
		var config = armory.data.Config.raw;
		// Resize shadow map
		var l = path.light;
		if (l.data.raw.type == "sun" && l.data.raw.shadowmap_size != config.rp_shadowmap_cascade) {
			l.data.raw.shadowmap_size = config.rp_shadowmap_cascade;
			var rt = path.renderTargets.get("shadowMap");
			if (rt != null) {
				rt.unload();
				path.renderTargets.remove("shadowMap");
			}
		}
		else if (l.data.raw.shadowmap_size != config.rp_shadowmap_cube) {
			l.data.raw.shadowmap_size = config.rp_shadowmap_cube;
			var rt = path.renderTargets.get("shadowMapCube");
			if (rt != null) {
				rt.unload();
				path.renderTargets.remove("shadowMapCube");
			}
		}
		if (superSample != config.rp_supersample) {
			superSample = config.rp_supersample;
			for (rt in path.renderTargets) {
				if (rt.raw.width == 0 && rt.raw.scale != null) {
					rt.raw.scale = getSuperSampling();
				}
			}
			path.resize();
		}
		// Init voxels
		#if rp_voxels
		if (!voxelsCreated) initGI();
		#end
		#end // arm_config
	}

	#if (rp_translucency)
	public static function initTranslucency() {
		path.createDepthBuffer("main", "DEPTH24");

		var t = new RenderTargetRaw();
		t.name = "accum";
		t.width = 0;
		t.height = 0;
		t.displayp = getDisplayp();
		t.format = "RGBA64";
		t.scale = getSuperSampling();
		t.depth_buffer = "main";
		path.createRenderTarget(t);

		var t = new RenderTargetRaw();
		t.name = "revealage";
		t.width = 0;
		t.height = 0;
		t.displayp = getDisplayp();
		t.format = "R16";
		t.scale = getSuperSampling();
		t.depth_buffer = "main";
		path.createRenderTarget(t);

		path.loadShader("shader_datas/translucent_resolve/translucent_resolve");
	}

	public static function drawTranslucency(target: String) {
		path.setTarget("accum");
		path.clearTarget(0xff000000);
		path.setTarget("revealage");
		path.clearTarget(0xffffffff);
		path.setTarget("accum", ["revealage"]);
		#if rp_shadowmap
		{
			#if arm_shadowmap_atlas
			bindShadowMapAtlas();
			#else
			bindShadowMap();
			#end
		}
		#end
		path.drawMeshes("translucent");
		#if rp_render_to_texture
		{
			path.setTarget(target);
		}
		#else
		{
			path.setTarget("");
		}
		#end
		path.bindTarget("accum", "gbuffer0");
		path.bindTarget("revealage", "gbuffer1");
		path.drawShader("shader_datas/translucent_resolve/translucent_resolve");
	}
	#end

	#if rp_bloom
	public static inline function drawBloom(srcRTName: String, downsampler: Downsampler, upsampler: Upsampler) {
		if (armory.data.Config.raw.rp_bloom != false) {
			// This can result in little jumps in the perceived bloom radius
			// when resizing the window because numMips might change, but
			// all implementations using this approach have the same problem
			// (including Eevee)
			final minDim = Math.min(path.currentW, path.currentH);
			final logMinDim = Math.max(1.0, Helper.log2(minDim) + (Main.bloomRadius - 8.0));
			final numMips = Std.int(logMinDim);

			// Sample scale for upsampling, 0.5 to use half-texel steps,
			// use fraction of logMinDim to make the visual jumps
			// described above less visible
			Postprocess.bloom_uniforms[3] = 0.5 + logMinDim - numMips;

			downsampler.dispatch(srcRTName, numMips);
			upsampler.dispatch(srcRTName, numMips);
		}
	}
	#end

	#if rp_voxels
	public static function initGI(tname = "voxels") {
		var t = new RenderTargetRaw();
		t.name = tname;

		#if (rp_voxels == "Voxel AO")
		{
			t.format = "R8";
		}
		#else
		{
			t.format = "RGBA64";
		}
		#end

		var res = getVoxelRes();
		var resZ =  getVoxelResZ();
		t.width = res;
		t.height = res;
		t.depth = Std.int(res * resZ);
		t.is_image = true;
		t.mipmaps = true;
		path.createRenderTarget(t);

		#if arm_voxelgi_temporal
		{
			var tB = new RenderTargetRaw();
			tB.name = t.name + "B";
			tB.format = t.format;
			tB.width = t.width;
			tB.height = t.height;
			tB.depth = t.depth;
			tB.is_image = t.is_image;
			tB.mipmaps = t.mipmaps;
			path.createRenderTarget(tB);
		}
		#end
	}
	#end

	

	public static inline function getCubeSize(): Int {
		#if (rp_shadowmap_cube == 256)
		return 256;
		#elseif (rp_shadowmap_cube == 512)
		return 512;
		#elseif (rp_shadowmap_cube == 1024)
		return 1024;
		#elseif (rp_shadowmap_cube == 2048)
		return 2048;
		#elseif (rp_shadowmap_cube == 4096)
		return 4096;
		#else
		return 0;
		#end
	}

	public static inline function getCascadeSize(): Int {
		#if (rp_shadowmap_cascade == 256)
		return 256;
		#elseif (rp_shadowmap_cascade == 512)
		return 512;
		#elseif (rp_shadowmap_cascade == 1024)
		return 1024;
		#elseif (rp_shadowmap_cascade == 2048)
		return 2048;
		#elseif (rp_shadowmap_cascade == 4096)
		return 4096;
		#elseif (rp_shadowmap_cascade == 8192)
		return 8192;
		#elseif (rp_shadowmap_cascade == 16384)
		return 16384;
		#else
		return 0;
		#end
	}

	public static inline function getVoxelRes(): Int {
		#if (rp_voxelgi_resolution == 1024)
		return 1024;
		#elseif (rp_voxelgi_resolution == 512)
		return 512;
		#elseif (rp_voxelgi_resolution == 256)
		return 256;
		#elseif (rp_voxelgi_resolution == 128)
		return 128;
		#elseif (rp_voxelgi_resolution == 64)
		return 64;
		#elseif (rp_voxelgi_resolution == 32)
		return 32;
		#else
		return 0;
		#end
	}

	public static inline function getVoxelResZ(): Float {
		#if (rp_voxelgi_resolution_z == 4.0)
		return 4.0;
		#elseif (rp_voxelgi_resolution_z == 2.0)
		return 2.0;
		#elseif (rp_voxelgi_resolution_z == 1.5)
		return 1.5;
		#elseif (rp_voxelgi_resolution_z == 1.0)
		return 1.0;
		#elseif (rp_voxelgi_resolution_z == 0.5)
		return 0.5;
		#elseif (rp_voxelgi_resolution_z == 0.25)
		return 0.25;
		#elseif (rp_voxelgi_resolution_z == 0.125)
		return 0.125;
		#else
		return 0.0;
		#end
	}

	public static inline function getSuperSampling(): Float {
		return superSample;
	}

	public static inline function getHdrFormat(): String {
		#if rp_hdr
		return "RGBA64";
		#else
		return "RGBA32";
		#end
	}

	public static inline function getDisplayp(): Null<Int> {
		#if rp_resolution_filter // Custom resolution set
		return Main.resolutionSize;
		#else
		return null;
		#end
	}
	
	#if arm_debug
	public static var shadowsLogicTime = 0.0;
	public static var shadowsRenderTime = 0.0;
	static var startShadowsLogicTime = 0.0;
	static var startShadowsRenderTime = 0.0;
	static var callBackSetup = false;
	static function setupEndFrameCallback() {
		if (!callBackSetup) {
			callBackSetup = true;
			iron.App.endFrameCallbacks.push(endFrame);
		}
	}
	static function beginShadowsLogicProfile() { setupEndFrameCallback(); startShadowsLogicTime = kha.Scheduler.realTime(); }
	static function beginShadowsRenderProfile() { startShadowsRenderTime = kha.Scheduler.realTime(); }
	static function endShadowsLogicProfile() { shadowsLogicTime += kha.Scheduler.realTime() - startShadowsLogicTime - shadowsRenderTime; }
	static function endShadowsRenderProfile() { shadowsRenderTime += kha.Scheduler.realTime() - startShadowsRenderTime; }
	public static function endFrame() { shadowsLogicTime = 0;  shadowsRenderTime = 0; }
	#end
}

#if arm_shadowmap_atlas
class ShadowMapAtlas {

	public var target: String;
	public var baseTileSizeConst: Int;
	public var maxAtlasSizeConst: Int;

	public var sizew: Int;
	public var sizeh: Int;

	public var currTileOffset = 0;
	public var tiles: Array<ShadowMapTile> = [];
	public var activeTiles: Array<ShadowMapTile> = [];
	public var depth = 1;
	#if arm_shadowmap_atlas_lod
	var tileSizes: Array<Int> = [];
	var tileSizeFactor: Array<Float> = [];
	#end
	public var updateRenderTarget = false;
	public static var shadowMapAtlases:Map<String, ShadowMapAtlas> = new Map(); // map a shadowmap atlas to their light type

	#if arm_debug
	public var lightType: String;
	public var rejectedLights: Array<LightObject> = [];
	#end

	function new(light: LightObject) {

		var maxTileSize = shadowMapAtlasSize(light);
		this.target = shadowMapAtlasName(light.data.raw.type);
		this.sizew = this.sizeh = this.baseTileSizeConst = maxTileSize;
		this.depth = getSubdivisions();
		this.maxAtlasSizeConst = getMaxAtlasSize(light.data.raw.type);

		#if arm_shadowmap_atlas_lod
		computeTileSizes(maxTileSize, depth);
		#end

		#if arm_debug
		#if arm_shadowmap_atlas_single_map
		this.lightType = "any";
		#else
		this.lightType = light.data.raw.type;
		#end
		#end

	}

	/**
	 * Adds a light to an atlas. The atlas is decided based on the type of the light
	 * @param light of type LightObject to be added to an yatlas
	 * @return if the light was added succesfully
	 */
	public static function addLight(light: LightObject) {
		var atlasName = shadowMapAtlasName(light.data.raw.type);
		var atlas = shadowMapAtlases.get(atlasName);
		if (atlas == null) {
			// create a new atlas
			atlas = new ShadowMapAtlas(light);
			shadowMapAtlases.set(atlasName, atlas);
		}

		// find a free tile for this light
		var mainTile = ShadowMapTile.assignTiles(light, atlas, null);
		if (mainTile == null) {
			#if arm_debug
			if (!atlas.rejectedLights.contains(light))
				atlas.rejectedLights.push(light);
			#end
			return;
		}

		atlas.activeTiles.push(mainTile);
		// notify the tile on light remove
		light.tileNotifyOnRemove = mainTile.notifyOnLightRemove;
		// notify atlas when this tile is freed
		mainTile.notifyOnFree = atlas.freeActiveTile;
		// "lock" light to make sure it's not eligible to be added again
		light.lightInAtlas = true;
	}

	static inline function shadowMapAtlasSize(light:LightObject):Int {
		// TODO: this can break because we are changing shadowmap_size elsewhere.
		return light.data.raw.shadowmap_size;
	}

	public function getTileSize(shadowMapScale: Float): Int {
		#if arm_shadowmap_atlas_lod
		// find the first scale factor that is smaller to the shadowmap scale, and then return the previous one.
		var i = 0;
		for (sizeFactor in tileSizeFactor) {
			if (sizeFactor < shadowMapScale) break;
			i++;
		}
		return tileSizes[i - 1];
		#else
		return this.baseTileSizeConst;
		#end
	}

	#if arm_shadowmap_atlas_lod
	function computeTileSizes(maxTileSize: Int, depth: Int): Void {
		// find the highest value based on the calculation done in the cluster code
		var base = LightObject.zToShadowMapScale(0, 16);
		var subdiv = base / depth;
		for(i in 0...depth){
			this.tileSizes.push(Std.int(maxTileSize / Math.pow(2, i)));
			this.tileSizeFactor.push(base);
			base -= subdiv;
		}
		this.tileSizes.push(0);
		this.tileSizeFactor.push(0.0);
	}
	#end

	public inline function atlasLimitReached() {
		// asume square atlas
		return (currTileOffset + 1) * baseTileSizeConst > maxAtlasSizeConst;
	}

	public static inline function shadowMapAtlasName(type: String): String {
		#if arm_shadowmap_atlas_single_map
		return "shadowMapAtlas";
		#else
		switch (type) {
			case "point":
				return "shadowMapAtlasPoint";
			case "sun":
				return "shadowMapAtlasSun";
			default:
				return "shadowMapAtlasSpot";
		}
		#end
	}

	public static inline function getSubdivisions(): Int {
		#if (rp_shadowmap_atlas_lod_subdivisions == 2)
		return 2;
		#elseif (rp_shadowmap_atlas_lod_subdivisions == 3)
		return 3;
		#elseif (rp_shadowmap_atlas_lod_subdivisions == 4)
		return 4;
		#elseif (rp_shadowmap_atlas_lod_subdivisions == 5)
		return 5;
		#elseif (rp_shadowmap_atlas_lod_subdivisions == 6)
		return 6;
		#elseif (rp_shadowmap_atlas_lod_subdivisions == 7)
		return 7;
		#elseif (rp_shadowmap_atlas_lod_subdivisions == 8)
		return 8;
		#elseif (!arm_shadowmap_atlas_lod)
		return 1;
		#end
	}

	public static inline function getMaxAtlasSize(type: String): Int {
		#if arm_shadowmap_atlas_single_map
			#if (rp_shadowmap_atlas_max_size == 512)
			return 512;
			#elseif (rp_shadowmap_atlas_max_size == 1024)
			return 1024;
			#elseif (rp_shadowmap_atlas_max_size == 2048)
			return 2048;
			#elseif (rp_shadowmap_atlas_max_size == 4096)
			return 4096;
			#elseif (rp_shadowmap_atlas_max_size == 8192)
			return 8192;
			#elseif (rp_shadowmap_atlas_max_size == 16384)
			return 16384;
			#end
		#else
		switch (type) {
			case "point": {
				#if (rp_shadowmap_atlas_max_size_point == 1024)
				return 1024;
				#elseif (rp_shadowmap_atlas_max_size_point == 2048)
				return 2048;
				#elseif (rp_shadowmap_atlas_max_size_point == 4096)
				return 4096;
				#elseif (rp_shadowmap_atlas_max_size_point == 8192)
				return 8192;
				#elseif (rp_shadowmap_atlas_max_size_point == 16384)
				return 16384;
				#end
			}
			case "spot": {
				#if (rp_shadowmap_atlas_max_size_spot == 512)
				return 512;
				#elseif (rp_shadowmap_atlas_max_size_spot == 1024)
				return 1024;
				#elseif (rp_shadowmap_atlas_max_size_spot == 2048)
				return 2048;
				#elseif (rp_shadowmap_atlas_max_size_spot == 4096)
				return 4096;
				#elseif (rp_shadowmap_atlas_max_size_spot == 8192)
				return 8192;
				#elseif (rp_shadowmap_atlas_max_size_spot == 16384)
				return 16384;
				#end
			}
			case "sun": {
				#if (rp_shadowmap_atlas_max_size_sun == 512)
				return 512;
				#elseif (rp_shadowmap_atlas_max_size_sun == 1024)
				return 1024;
				#elseif (rp_shadowmap_atlas_max_size_sun == 2048)
				return 2048;
				#elseif (rp_shadowmap_atlas_max_size_sun == 4096)
				return 4096;
				#elseif (rp_shadowmap_atlas_max_size_sun == 8192)
				return 8192;
				#elseif (rp_shadowmap_atlas_max_size_sun == 16384)
				return 16384;
				#end
			}
			default: {
				#if (rp_shadowmap_atlas_max_size == 512)
				return 512;
				#elseif (rp_shadowmap_atlas_max_size == 1024)
				return 1024;
				#elseif (rp_shadowmap_atlas_max_size == 2048)
				return 2048;
				#elseif (rp_shadowmap_atlas_max_size == 4096)
				return 4096;
				#elseif (rp_shadowmap_atlas_max_size == 8192)
				return 8192;
				#elseif (rp_shadowmap_atlas_max_size == 16384)
				return 16384;
				#end
			}

		}
		#end
	}

	function freeActiveTile(tile: ShadowMapTile) {
		activeTiles.remove(tile);
	}
}

class ShadowMapTile {

	public var light:Null<LightObject> = null;
	public var coordsX:Int;
	public var coordsY:Int;
	public var size:Int;
	public var tiles:Array<ShadowMapTile> = [];
	public var linkedTile:ShadowMapTile = null;

	#if arm_shadowmap_atlas_lod
	public var parentTile: ShadowMapTile = null;
	public var activeSubTiles: Int = 0;
	public var newTileSize: Int = -1;

	static var tilePattern = [[0, 0], [1, 0], [0, 1], [1, 1]];
	#end

	function new(coordsX: Int, coordsY: Int, size: Int) {
		this.coordsX = coordsX;
		this.coordsY = coordsY;
		this.size = size;
	}

	public static function assignTiles(light: LightObject, atlas: ShadowMapAtlas, oldTile: ShadowMapTile): ShadowMapTile {
		var tileSize = 0;

		#if arm_shadowmap_atlas_lod
		if (oldTile != null && oldTile.newTileSize != -1) {
			// reuse tilesize instead of computing it again
			tileSize = oldTile.newTileSize;
			oldTile.newTileSize = -1;
		}
		else
		#end
			tileSize = atlas.getTileSize(light.shadowMapScale);

		if (tileSize == 0)
			return null;

		var tiles = [];
		tiles = findCreateTiles(light, oldTile, atlas, tilesLightType(light.data.raw.type), tileSize);

		// lock new tiles with light
		for (tile in tiles)
			tile.lockTile(light);

		return linkTiles(tiles);
	}

	static inline function linkTiles(tiles: Array<ShadowMapTile>): ShadowMapTile  {
		if (tiles.length > 1) {
			var linkedTile = tiles[0];
			for (i in 1...tiles.length) {
				linkedTile.linkedTile = tiles[i];
				linkedTile = tiles[i];
			}
		}
		return tiles[0];
	}

	static inline function findCreateTiles(light: LightObject, oldTile: ShadowMapTile, atlas: ShadowMapAtlas, tilesPerLightType: Int, tileSize: Int): Array<ShadowMapTile> {
		var tilesFound: Array<ShadowMapTile> = [];

		while (tilesFound.length < tilesPerLightType) {
			findTiles(light, oldTile, atlas.tiles, tileSize, tilesPerLightType, tilesFound);

			if (tilesFound.length < tilesPerLightType) {
				tilesFound = []; // empty tilesFound
				// skip creating more tiles if limit has been reached
				if (atlas.atlasLimitReached())
					break;

				createTiles(atlas.tiles, atlas.baseTileSizeConst, atlas.depth, atlas.currTileOffset, atlas.currTileOffset);
				atlas.currTileOffset++;
				// update texture to accomodate new size
				atlas.updateRenderTarget = true;
				atlas.sizew = atlas.sizeh = atlas.currTileOffset * atlas.baseTileSizeConst;
			}
		}
		return tilesFound;
	}

	inline static function findTiles(light:LightObject, oldTile: ShadowMapTile,
		tiles: Array<ShadowMapTile>, size: Int, tilesCount: Int, tilesFound: Array<ShadowMapTile>): Void {
		#if arm_shadowmap_atlas_lod
		if (oldTile != null) {
			// reuse children tiles
			if (size < oldTile.size) {
				oldTile.forEachTileLinked(function(lTile) {
					var childTile = findFreeChildTile(lTile, size);
					tilesFound.push(childTile);
				});
			}
			// reuse parent tiles
			else {
				oldTile.forEachTileLinked(function(lTile) {
					// find out if parents tiles are not occupied
					var parentTile = findFreeParentTile(lTile, size);
					// if parent is free, add it to found tiles
					if (parentTile != null)
						tilesFound.push(parentTile);
				});
				if (tilesFound.length < tilesCount) {
					// find naively the rest of the tiles that couldn't be reused
					findTilesNaive(light, tiles, size, tilesCount, tilesFound);
				}
			}
		}
		else
		#end
			findTilesNaive(light, tiles, size, tilesCount, tilesFound);
	}

	#if arm_shadowmap_atlas_lod
	static inline function findFreeChildTile(tile: ShadowMapTile, size: Int): ShadowMapTile {
		var childrenTile = tile;
		while (size < childrenTile.size) {
			childrenTile = childrenTile.tiles[0];
		}
		return childrenTile;
	}

	static inline function findFreeParentTile(tile: ShadowMapTile, size: Int): ShadowMapTile {
		var parentTile = tile;
		while (size > parentTile.size) {
			parentTile = parentTile.parentTile;
			// stop if parent tile is occupied
			if (parentTile.activeSubTiles > 1) {
				parentTile = null;
				break;
			}
		}
		return parentTile;
	}
	#end

	static function findTilesNaive(light:LightObject, tiles: Array<ShadowMapTile>, size: Int, tilesCount: Int, tilesFound: Array<ShadowMapTile>): Void {
		for (tile in tiles) {
			if (tile.size == size) {
				if (tile.light == null #if arm_shadowmap_atlas_lod && tile.activeSubTiles == 0 #end) {
					tilesFound.push(tile);
					// stop after finding enough tiles
					if (tilesFound.length == tilesCount)
						return;
				}
			}
			else {
				// skip over if end of the tree or tile is occupied
				if (tile.tiles.length == 0 || tile.light != null)
					continue;
				findTilesNaive(light, tile.tiles, size, tilesCount, tilesFound);
				// skip iterating over the rest of the tiles if found enough
				if (tilesFound.length == tilesCount)
					return;
			}
		}
	}

	// create a basic tile and subdivide it if needed
	public static function createTiles(tiles:Array<ShadowMapTile>, size:Int, depth: Int, baseX:Int, baseY:Int) {
		var i = baseX;
		var j = 0;
		var lastTile = tiles.length;
		// assume occupied tiles start from 1 line before the base x
		var occupiedTiles = baseX - 1;

		while (i >= 0) {
			if (i <= occupiedTiles) { // avoid overriding tiles
				j = baseY;
			}
			while (j <= baseY) {
				// create base tile of max-size
				tiles.push(new ShadowMapTile(size * i, size * j, size));
				#if arm_shadowmap_atlas_lod
				tiles[lastTile].tiles = subDivTile(tiles[lastTile], size, size * i, size * j, depth - 1);
				#end
				lastTile++;
				j++;
			}
			i--;
		}
	}

	#if arm_shadowmap_atlas_lod
	static function subDivTile(parent: ShadowMapTile, size: Int, baseCoordsX: Int, baseCoordsY: Int, depth: Int): Array<ShadowMapTile> {
		var tileSize = Std.int(size / 2);

		var tiles = [];

		for (i in 0...4) {
			var coordsX = baseCoordsX + tilePattern[i][0] * tileSize;
			var coordsY = baseCoordsY + tilePattern[i][1] * tileSize;

			var tile = new ShadowMapTile(coordsX, coordsY, tileSize);
			tile.parentTile = parent;

			if (depth > 1)
				tile.tiles = subDivTile(tile, tileSize, coordsX, coordsY, depth - 1);
			tiles.push(tile);
		}

		return tiles;
	}
	#end

	public static inline function tilesLightType(type: String): Int {
		switch (type) {
			case "sun":
				return LightObject.cascadeCount;
			case "point":
				return 6;
			default:
				return 1;
		}
	}

	public function notifyOnLightRemove() {
		unlockLight = true;
		freeTile();
	}

	inline function lockTile(light: LightObject): Void {
		if (this.light != null)
			return;
		this.light = light;
		#if arm_shadowmap_atlas_lod
		// update the count of used tiles for parents
		this.forEachParentTile(function (pTile) {
			pTile.activeSubTiles++;
		});
		#end
	}

	public var unlockLight: Bool = false;
	public var notifyOnFree: ShadowMapTile -> Void;

	public function freeTile(): Void {
		// prevent duplicates
		if (light != null && unlockLight) {
			light.lightInAtlas = false;
			unlockLight = false;
		}

		var linkedTile = this;
		var tempTile = this;
		while (linkedTile != null) {
			linkedTile.light = null;
			#if arm_shadowmap_atlas_lod
			// update the count of used tiles for parents
			linkedTile.forEachParentTile(function (pTile) {
				if (pTile.activeSubTiles > 0)
					pTile.activeSubTiles--;
			});
			#end

			linkedTile = linkedTile.linkedTile;
			// unlink linked tiles
			tempTile.linkedTile = null;
			tempTile = linkedTile;
		}
		// notify atlas that this tile has been freed
		if (notifyOnFree != null) {
			notifyOnFree(this);
			notifyOnFree = null;
		}
	}

	public inline function forEachTileLinked(action: ShadowMapTile->Void): Void {
		var linkedTile = this;
		while (linkedTile != null) {
			action(linkedTile);
			linkedTile = linkedTile.linkedTile;
		}
	}

	#if arm_shadowmap_atlas_lod
	public inline function forEachParentTile(action: ShadowMapTile->Void): Void {
		var parentTile = this.parentTile;
		while (parentTile != null) {
			action(parentTile);
			parentTile = parentTile.parentTile;
		}
	}
	#end
}
#end
