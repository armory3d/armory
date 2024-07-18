package armory.renderpath;

import iron.RenderPath;
import iron.object.LightObject;

import armory.math.Helper;
import kha.arrays.Float32Array;

class Inc {
	static var path: RenderPath;
	public static var superSample = 1.0;

	static var pointIndex = 0;
	static var spotIndex = 0;
	static var lastFrame = -1;

	#if ((rp_voxels != 'Off') && arm_config)
	static var voxelsCreated = false;
	#end

	#if (rp_voxels != "Off")
	static var voxel_sh0:kha.compute.Shader = null;
	static var voxel_sh1:kha.compute.Shader = null;
	static var voxel_ta0:kha.compute.TextureUnit;
	static var voxel_tb0:kha.compute.TextureUnit;
	static var voxel_ca0:kha.compute.ConstantLocation;
	static var voxel_cb0:kha.compute.ConstantLocation;
	static var voxel_ta1:kha.compute.TextureUnit;
	static var voxel_tb1:kha.compute.TextureUnit;
	static var voxel_tc1:kha.compute.TextureUnit;
	static var m = iron.math.Mat4.identity();
	static var voxel_ca1:kha.compute.ConstantLocation;
	static var voxel_cb1:kha.compute.ConstantLocation;
	#if (rp_voxels == "Voxel GI")
	static var voxel_td1:kha.compute.TextureUnit;
	static var voxel_te1:kha.compute.TextureUnit;
	static var voxel_tf1:kha.compute.TextureUnit;
	static var voxel_tg1:kha.compute.TextureUnit;
	static var voxel_th1:kha.compute.TextureUnit;
	#if (rp_gbuffer2 && arm_deferred)
	static var voxel_ti1:kha.compute.TextureUnit;
	#end
	#if arm_brdf
	static var voxel_tj1:kha.compute.TextureUnit;
	#end
	#if arm_radiance
	static var voxel_tk1:kha.compute.TextureUnit;
	static var voxel_ce1:kha.compute.ConstantLocation;
	#end
	#if arm_irradiance
	static var voxel_cc1:kha.compute.ConstantLocation;
	#end
	static var voxel_cd1:kha.compute.ConstantLocation;
	#if arm_envldr
	static var voxel_cf1:kha.compute.ConstantLocation;
	#end
	static var voxel_cg1:kha.compute.ConstantLocation;
	#else
	#if arm_voxelgi_shadows
	static var voxel_tf1:kha.compute.TextureUnit;
	#end
	#end
	#if (arm_voxelgi_shadows || rp_voxels == "Voxel GI")
	static var voxel_sh2:kha.compute.Shader = null;
	static var voxel_ta2:kha.compute.TextureUnit;
	static var voxel_tb2:kha.compute.TextureUnit;
	static var voxel_ca2:kha.compute.ConstantLocation;
	static var voxel_cb2:kha.compute.ConstantLocation;
	static var voxel_cc2:kha.compute.ConstantLocation;
	#end
	#if arm_deferred
	static var voxel_sh3:kha.compute.Shader = null;
	static var voxel_ta3:kha.compute.TextureUnit;
	static var voxel_tb3:kha.compute.TextureUnit;
	static var voxel_tc3:kha.compute.TextureUnit;
	static var voxel_td3:kha.compute.TextureUnit;
	static var voxel_ca3:kha.compute.ConstantLocation;
	static var voxel_cb3:kha.compute.ConstantLocation;
	static var voxel_cc3:kha.compute.ConstantLocation;
	static var voxel_cd3:kha.compute.ConstantLocation;
	static var voxel_ce3:kha.compute.ConstantLocation;
	static var voxel_cf3:kha.compute.ConstantLocation;
	#if (rp_voxels == "Voxel GI")
	static var voxel_sh4:kha.compute.Shader = null;
	static var voxel_ta4:kha.compute.TextureUnit;
	static var voxel_tb4:kha.compute.TextureUnit;
	static var voxel_tc4:kha.compute.TextureUnit;
	static var voxel_td4:kha.compute.TextureUnit;
	static var voxel_te4:kha.compute.TextureUnit;
	static var voxel_ca4:kha.compute.ConstantLocation;
	static var voxel_cb4:kha.compute.ConstantLocation;
	static var voxel_cc4:kha.compute.ConstantLocation;
	static var voxel_cd4:kha.compute.ConstantLocation;
	static var voxel_ce4:kha.compute.ConstantLocation;
	static var voxel_cf4:kha.compute.ConstantLocation;
	#end
	#end
	#if (rp_voxels == "Voxel GI")
	static var voxel_sh5:kha.compute.Shader = null;
	static var voxel_ta5:kha.compute.TextureUnit;
	static var voxel_ca5:kha.compute.ConstantLocation;
	static var voxel_cb5:kha.compute.ConstantLocation;
	static var voxel_cc5:kha.compute.ConstantLocation;
	static var voxel_cd5:kha.compute.ConstantLocation;
	static var voxel_ce5:kha.compute.ConstantLocation;
	static var voxel_cf5:kha.compute.ConstantLocation;
	static var voxel_cg5:kha.compute.ConstantLocation;
	#if rp_shadowmap
	static var voxel_tb5:kha.compute.TextureUnit;
	static var voxel_tc5:kha.compute.TextureUnit;
	static var voxel_td5:kha.compute.TextureUnit;
	static var voxel_te5:kha.compute.TextureUnit;
	static var voxel_tf5:kha.compute.TextureUnit;
	static var voxel_tg5:kha.compute.TextureUnit;
	static var voxel_th5:kha.compute.TextureUnit;
	static var voxel_ch5:kha.compute.ConstantLocation;
	static var voxel_ci5:kha.compute.ConstantLocation;
	static var voxel_cj5:kha.compute.ConstantLocation;
	static var voxel_ck5:kha.compute.ConstantLocation;
	static var voxel_cl5:kha.compute.ConstantLocation;
	static var voxel_cm5:kha.compute.ConstantLocation;
	#if arm_shadowmap_atlas
	static var m2 = iron.math.Mat4.identity();
	#end
	#end
	#end
	#end //rp_voxels

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
	public static function updatePointLightAtlasData(transparent: Bool): Void {
		var atlas = ShadowMapAtlas.shadowMapAtlases.get(ShadowMapAtlas.shadowMapAtlasName("point", transparent));
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

	static function getShadowMapAtlas(atlas:ShadowMapAtlas, transparent: Bool):String {
		inline function createDepthTarget(name: String, size: Int) {
			var t = new RenderTargetRaw();
			t.name = name;
			t.width = t.height = size;
			t.format = transparent ? "RGBA64" : "DEPTH16";
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
				ShadowMapAtlas.addLight(light, false);
				ShadowMapAtlas.addLight(light, true);
			}
		}
		// update point light data before rendering
		updatePointLightAtlasData(false);
		updatePointLightAtlasData(true);

		for (atlas in ShadowMapAtlas.shadowMapAtlases) {
			var tilesToRemove = [];
			#if arm_shadowmap_atlas_lod
			var tilesToChangeSize = [];
			#end

			var transparent = StringTools.endsWith(atlas.target, "Transparent");
			var shadowmap = getShadowMapAtlas(atlas, transparent);
			path.setTargetStream(shadowmap);

			if (transparent)
				path.clearTarget(0xffffff, 0.0);
			else
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

					if (transparent)
						path.drawMeshesStream("shadowmap_transparent");
					else
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
			updatePointLightAtlasData(transparent);
			#end

			for (tile in tilesToRemove) {
				atlas.activeTiles.remove(tile);
				tile.freeTile();
			}
		}
		#if arm_debug
		endShadowsLogicProfile();
		#end
		#end // rp_shadowmap
	}
	#else
	public static function bindShadowMap() {
		for (l in iron.Scene.active.lights) {
			if (!l.visible || l.data.raw.type != "sun") continue;
			var n = "shadowMap";
			path.bindTarget(n, n);
			var n = "shadowMapTransparent";
			path.bindTarget(n, n);
			break;
		}
		for (i in 0...pointIndex) {
			var n = "shadowMapPoint[" + i + "]";
			path.bindTarget(n, n);
			var n = "shadowMapPointTransparent[" + i + "]";
			path.bindTarget(n, n);
		}
		for (i in 0...spotIndex) {
			var n = "shadowMapSpot[" + i + "]";
			path.bindTarget(n, n);
			var n = "shadowMapSpotTransparent[" + i + "]";
			path.bindTarget(n, n);
		}
	}

	static function shadowMapName(light: LightObject, transparent: Bool): String {
		switch (light.data.raw.type) {
			case "sun":
				return transparent ? "shadowMapTransparent" : "shadowMap";
			case "point":
				return transparent ? "shadowMapPointTransparent[" + pointIndex + "]" : "shadowMapPoint[" + pointIndex + "]";
			default:
				return transparent ? "shadowMapSpotTransparent[" + spotIndex + "]" : "shadowMapSpot[" + spotIndex + "]";
		}
	}

	static function getShadowMap(l: iron.object.LightObject, transparent: Bool): String {
		var target = shadowMapName(l, transparent);
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
				t.format = transparent ? "RGBA64" : "DEPTH16";
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
				t.format = transparent ? "RGBA64" : "DEPTH16";
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
			var faces = l.data.raw.shadowmap_cube ? 6 : 1;
			var shadowmap = Inc.getShadowMap(l, false);
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

		pointIndex = 0;
		spotIndex = 0;
		for (l in iron.Scene.active.lights) {
			if (!l.visible) continue;

			path.light = l;
			var faces = l.data.raw.shadowmap_cube ? 6 : 1;
			var shadowmap = Inc.getShadowMap(l, true);
			for (i in 0...faces) {
				if (faces > 1) path.currentFace = i;
				path.setTarget(shadowmap);
				path.clearTarget(0xffffff, 0.0);
				if (l.data.raw.cast_shadow) {
					path.drawMeshes("shadowmap_transparent");
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
		#if (rp_voxels != 'Off')
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
		#if (rp_voxels != "Off")
		path.bindTarget("voxelsOut", "voxels");
		#if (rp_voxels == "Voxel GI")
		path.bindTarget("voxelsSDF", "voxelsSDF");
		#end
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

	#if (rp_voxels != 'Off')
	public static function initGI(tname = "voxels") {
		var t = new RenderTargetRaw();
		t.name = tname;
		
		#if arm_config
		var config = armory.data.Config.raw;
		if (config.rp_voxels != true || voxelsCreated) return;
		voxelsCreated = true;
		#end

		var res = iron.RenderPath.getVoxelRes();
		var resZ =  iron.RenderPath.getVoxelResZ();

		if (t.name == "voxels_diffuse" || t.name == "voxels_specular" || t.name == "voxels_ao") {
			t.width = 0;
			t.height = 0;
			t.displayp = getDisplayp();
			t.scale = getSuperSampling();
			t.format = t.name == "voxels_ao" ? "R8" : "RGBA32";
		}
		else {
			if (t.name == "voxelsSDF" || t.name == "voxelsSDFtmp") {
				t.format = "R16";
				t.width = res;
				t.height = res * Main.voxelgiClipmapCount;
				t.depth = res;
			}
			else {
				#if (rp_voxels == "Voxel AO")
				{
					if (t.name == "voxelsOut" || t.name == "voxelsOutB") {
						t.format = "R16";
						t.width = res * (6 + 16);
						t.height = res * Main.voxelgiClipmapCount;
						t.depth = res;
					}
					else {
						t.format = "R32";
						t.width = res * 6;
						t.height = res;
						t.depth = res;
					}
				}
				#else
				{
					if (t.name == "voxelsOut" || t.name == "voxelsOutB") {
						t.format = "RGBA64";
						t.width = res * (6 + 16);
						t.height = res * Main.voxelgiClipmapCount;
						t.depth = res;
					}
					else if (t.name == "voxelsLight") {
						t.format = "R32";
						t.width = res;
						t.height = res;
						t.depth = res * 3;
					}
					else {
						t.format = "R32";
						t.width = res * 6;
						t.height = res;
						t.depth = res * 10;//basecol, emission, normal, transparency flag
					}
				}
				#end
			}
		}
		t.is_image = true;
		t.mipmaps = true;
		path.createRenderTarget(t);
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

	#if (rp_voxels != "Off")
	public static function computeVoxelsBegin() {
		if (voxel_sh0 == null)
		{
			voxel_sh0 = path.getComputeShader("voxel_offsetprev");

			voxel_ta0 = voxel_sh0.getTextureUnit("voxelsB");
			voxel_tb0 = voxel_sh0.getTextureUnit("voxelsOut");

	 		voxel_ca0 = voxel_sh0.getConstantLocation("clipmaps");
	 		voxel_cb0 = voxel_sh0.getConstantLocation("clipmapLevel");
		}
		if (voxel_sh1 == null)
		{
			voxel_sh1 = path.getComputeShader("voxel_temporal");
			voxel_ta1 = voxel_sh1.getTextureUnit("voxels");
			voxel_tb1 = voxel_sh1.getTextureUnit("voxelsB");
			voxel_tc1 = voxel_sh1.getTextureUnit("voxelsOut");

	 		voxel_ca1 = voxel_sh1.getConstantLocation("clipmaps");
	 		voxel_cb1 = voxel_sh1.getConstantLocation("clipmapLevel");

			#if (rp_voxels == "Voxel GI")
			voxel_td1 = voxel_sh1.getTextureUnit("voxelsSampler");
			voxel_te1 = voxel_sh1.getTextureUnit("voxelsLight");
			voxel_tf1 = voxel_sh1.getTextureUnit("SDF");

			voxel_tg1 = voxel_sh1.getTextureUnit("gbuffer0");
			voxel_th1 = voxel_sh1.getTextureUnit("gbuffer1");
			#if (rp_gbuffer2 && arm_deferred)
			voxel_ti1 = voxel_sh1.getTextureUnit("gbuffer2");
			#end
			#if arm_brdf
			voxel_tj1 = voxel_sh1.getTextureUnit("senvmapBrdf");
			#end
			#if arm_radiance
			voxel_tk1 = voxel_sh1.getTextureUnit("senvmapRadiance");
			voxel_ce1 = voxel_sh1.getConstantLocation("envmapNumMipmaps");
			#end
			#if arm_irradiance
			voxel_cc1 = voxel_sh1.getConstantLocation("shirr");
			#end
			voxel_cd1 = voxel_sh1.getConstantLocation("envmapStrength");
			#if arm_envldr
			voxel_cf1 = voxel_sh1.getConstantLocation("backgroundCol");
			#end
			voxel_cg1 = voxel_sh1.getConstantLocation("eye");
			#else
			#if arm_voxelgi_shadows
			voxel_tf1 = voxel_sh1.getTextureUnit("SDF");
			#end
			#end
		}
		#if (arm_voxelgi_shadows || rp_voxels == "Voxel GI")
		if (voxel_sh2 == null)
		{
			voxel_sh2 = path.getComputeShader("voxel_sdf_jumpflood");
			voxel_ta2 = voxel_sh2.getTextureUnit("voxelsSDF");
			voxel_tb2 = voxel_sh2.getTextureUnit("voxelsSDFtmp");

	 		voxel_ca2 = voxel_sh2.getConstantLocation("clipmaps");
			voxel_cb2 = voxel_sh2.getConstantLocation("clipmapLevel");
			voxel_cc2 = voxel_sh2.getConstantLocation("jump_size");
		}
		#end
		#if arm_deferred
		if (voxel_sh3 == null)
		{
			#if (rp_voxels == "Voxel AO")
			voxel_sh3 = path.getComputeShader("voxel_resolve_ao");
			#else
			voxel_sh3 = path.getComputeShader("voxel_resolve_diffuse");
			#end
			voxel_ta3 = voxel_sh3.getTextureUnit("voxels");
			voxel_tb3 = voxel_sh3.getTextureUnit("gbufferD");
			voxel_tc3 = voxel_sh3.getTextureUnit("gbuffer0");
			#if (rp_voxels == "Voxel AO")
			voxel_td3 = voxel_sh3.getTextureUnit("voxels_ao");
			#else
			voxel_td3 = voxel_sh3.getTextureUnit("voxels_diffuse");
			#end
	 		voxel_ca3 = voxel_sh3.getConstantLocation("clipmaps");
	 		voxel_cb3 = voxel_sh3.getConstantLocation("InvVP");
	 		voxel_cc3 = voxel_sh3.getConstantLocation("cameraProj");
	 		voxel_cd3 = voxel_sh3.getConstantLocation("eye");
	 		voxel_ce3 = voxel_sh3.getConstantLocation("eyeLook");
	 		voxel_cf3 = voxel_sh3.getConstantLocation("postprocess_resolution");
		}
		#if (rp_voxels == "Voxel GI")
		if (voxel_sh4 == null)
		{
			voxel_sh4 = path.getComputeShader("voxel_resolve_specular");
			voxel_ta4 = voxel_sh4.getTextureUnit("voxels");
			voxel_tb4 = voxel_sh4.getTextureUnit("gbufferD");
			voxel_tc4 = voxel_sh4.getTextureUnit("gbuffer0");
			voxel_td4 = voxel_sh4.getTextureUnit("voxelsSDF");
			voxel_te4 = voxel_sh4.getTextureUnit("voxels_specular");

	 		voxel_ca4 = voxel_sh4.getConstantLocation("clipmaps");
	 		voxel_cb4 = voxel_sh4.getConstantLocation("InvVP");
	 		voxel_cc4 = voxel_sh4.getConstantLocation("cameraProj");
	 		voxel_cd4 = voxel_sh4.getConstantLocation("eye");
	 		voxel_ce4 = voxel_sh4.getConstantLocation("eyeLook");
	 		voxel_cf4 = voxel_sh4.getConstantLocation("postprocess_resolution");
		}
		#end
		#end // arm_deferred
		#if (rp_voxels == "Voxel GI")
		if (voxel_sh5 == null) {
			voxel_sh5 = path.getComputeShader("voxel_light");
			voxel_ta5 = voxel_sh5.getTextureUnit("voxelsLight");
			voxel_th5 = voxel_sh5.getTextureUnit("voxels");

	 		voxel_ca5 = voxel_sh5.getConstantLocation("clipmaps");
			voxel_cb5 = voxel_sh5.getConstantLocation("clipmapLevel");

	 		voxel_cc5 = voxel_sh5.getConstantLocation("lightPos");
	 		voxel_cd5 = voxel_sh5.getConstantLocation("lightColor");
	 		voxel_ce5 = voxel_sh5.getConstantLocation("lightType");
	 		voxel_cf5 = voxel_sh5.getConstantLocation("lightDir");
	 		voxel_cg5 = voxel_sh5.getConstantLocation("spotData");
	 		#if rp_shadowmap
	 		voxel_tb5 = voxel_sh5.getTextureUnit("shadowMap");
	 		voxel_te5 = voxel_sh5.getTextureUnit("shadowMapTransparent");
	 		voxel_tc5 = voxel_sh5.getTextureUnit("shadowMapSpot");
	 		voxel_tf5 = voxel_sh5.getTextureUnit("shadowMapSpotTransparent");
	 		voxel_td5 = voxel_sh5.getTextureUnit("shadowMapPoint");
	 		voxel_tg5 = voxel_sh5.getTextureUnit("shadowMapPointTransparent");

	 		voxel_ch5 = voxel_sh5.getConstantLocation("lightShadow");
	 		voxel_ci5 = voxel_sh5.getConstantLocation("lightProj");
	 		voxel_cj5 = voxel_sh5.getConstantLocation("LVP");
	 		voxel_ck5 = voxel_sh5.getConstantLocation("shadowsBias");
	 		#if arm_shadowmap_atlas
	 		voxel_cl5 = voxel_sh5.getConstantLocation("index");
	 		voxel_cm5 = voxel_sh5.getConstantLocation("pointLightDataArray");
	 		#end
	 		#end
		}
		#end
	}

	public static function computeVoxelsOffsetPrev() {
		var rts = path.renderTargets;
	 	var res = iron.RenderPath.getVoxelRes();
	 	var clipmaps = iron.RenderPath.clipmaps;
	 	var clipmap = clipmaps[iron.RenderPath.clipmapLevel];

		kha.compute.Compute.setShader(voxel_sh0);

		kha.compute.Compute.setTexture(voxel_ta0, rts.get("voxelsOut").image, kha.compute.Access.Read);
		kha.compute.Compute.setTexture(voxel_tb0, rts.get("voxelsOutB").image, kha.compute.Access.Write);

		var fa:Float32Array = new Float32Array(Main.voxelgiClipmapCount * 10);
		for (i in 0...Main.voxelgiClipmapCount) {
			fa[i * 10] = clipmaps[i].voxelSize;
			fa[i * 10 + 1] = clipmaps[i].extents.x;
			fa[i * 10 + 2] = clipmaps[i].extents.y;
			fa[i * 10 + 3] = clipmaps[i].extents.z;
			fa[i * 10 + 4] = clipmaps[i].center.x;
			fa[i * 10 + 5] = clipmaps[i].center.y;
			fa[i * 10 + 6] = clipmaps[i].center.z;
			fa[i * 10 + 7] = clipmaps[i].offset_prev.x;
			fa[i * 10 + 8] = clipmaps[i].offset_prev.y;
			fa[i * 10 + 9] = clipmaps[i].offset_prev.z;
		}

		kha.compute.Compute.setFloats(voxel_ca0, fa);

		kha.compute.Compute.setInt(voxel_cb0, iron.RenderPath.clipmapLevel);

		kha.compute.Compute.compute(Std.int(res / 8), Std.int(res / 8), Std.int(res / 8));
	}

	public static function computeVoxelsTemporal() {
		var rts = path.renderTargets;
	 	var res = iron.RenderPath.getVoxelRes();
	 	var camera = iron.Scene.active.camera;
	 	var clipmaps = iron.RenderPath.clipmaps;
	 	var clipmap = clipmaps[iron.RenderPath.clipmapLevel];

		kha.compute.Compute.setShader(voxel_sh1);

		kha.compute.Compute.setTexture(voxel_ta1, rts.get("voxels").image, kha.compute.Access.Read);
		kha.compute.Compute.setTexture(voxel_tb1, rts.get("voxelsOutB").image, kha.compute.Access.Read);
		kha.compute.Compute.setTexture(voxel_tc1, rts.get("voxelsOut").image, kha.compute.Access.Write);
		#if (rp_voxels == "Voxel GI")
		kha.compute.Compute.setSampledTexture(voxel_td1, rts.get("voxelsOutB").image);
		kha.compute.Compute.setTexture(voxel_te1, rts.get("voxelsLight").image, kha.compute.Access.Read);
		kha.compute.Compute.setTexture(voxel_tf1, rts.get("voxelsSDF").image, kha.compute.Access.Write);
		#else
		#if arm_voxelgi_shadows
		kha.compute.Compute.setTexture(voxel_tf1, rts.get("voxelsSDF").image, kha.compute.Access.Write);
		#end
		#end

		var fa:Float32Array = new Float32Array(Main.voxelgiClipmapCount * 10);
		for (i in 0...Main.voxelgiClipmapCount) {
			fa[i * 10] = clipmaps[i].voxelSize;
			fa[i * 10 + 1] = clipmaps[i].extents.x;
			fa[i * 10 + 2] = clipmaps[i].extents.y;
			fa[i * 10 + 3] = clipmaps[i].extents.z;
			fa[i * 10 + 4] = clipmaps[i].center.x;
			fa[i * 10 + 5] = clipmaps[i].center.y;
			fa[i * 10 + 6] = clipmaps[i].center.z;
			fa[i * 10 + 7] = clipmaps[i].offset_prev.x;
			fa[i * 10 + 8] = clipmaps[i].offset_prev.y;
			fa[i * 10 + 9] = clipmaps[i].offset_prev.z;
		}

		kha.compute.Compute.setFloats(voxel_ca1, fa);

		kha.compute.Compute.setInt(voxel_cb1, iron.RenderPath.clipmapLevel);

		#if (rp_voxels == "Voxel GI" && arm_deferred)
		kha.compute.Compute.setSampledTexture(voxel_tg1, rts.get("gbuffer0").image);
		kha.compute.Compute.setSampledTexture(voxel_th1, rts.get("gbuffer1").image);
		#if rp_gbuffer2
		kha.compute.Compute.setSampledTexture(voxel_ti1, rts.get("gbuffer2").image);
		#end
		#if arm_brdf
		kha.compute.Compute.setSampledTexture(voxel_tj1, iron.Scene.active.embedded.get("brdf.png"));
		#end
		#if arm_radiance
		kha.compute.Compute.setSampledTexture(voxel_tk1, iron.Scene.active.world.probe.radiance);
		var w = iron.Scene.active.world;
		var i = w != null ? w.probe.raw.radiance_mipmaps + 1 - 2 : 1;
		kha.compute.Compute.setFloat(voxel_ce1, i);
		#end
		#if arm_irradiance
		fa = iron.Scene.active.world == null ? iron.data.WorldData.getEmptyIrradiance() : iron.Scene.active.world.probe.irradiance;
		kha.compute.Compute.setFloats(voxel_cc1, fa);
		#end
		kha.compute.Compute.setFloat(voxel_cd1, iron.Scene.active.world == null ? 0.0 : iron.Scene.active.world.probe.raw.strength);

		#if arm_envldr
		var envCol:iron.math.Vec3;
		if (camera.data.raw.clear_color != null)
			envCol = new iron.math.Vec3(camera.data.raw.clear_color[0], camera.data.raw.clear_color[1], camera.data.raw.clear_color[2]);
		else
			envCol = new iron.math.Vec3(0.0);
		kha.compute.Compute.setFloat3(voxel_cf1, envCol.x, envCol.y, envCol.z);
		#end
		kha.compute.Compute.setFloat3(voxel_cg1, camera.transform.worldx(), camera.transform.worldy(), camera.transform.worldz());
		#end

		kha.compute.Compute.compute(Std.int(res / 8), Std.int(res / 8), Std.int(res / 8));
	}

	#if (arm_voxelgi_shadows || rp_voxels == "Voxel GI")
	public static function computeVoxelsSDF() {
		var rts = path.renderTargets;
	 	var res = iron.RenderPath.getVoxelRes();
	 	var clipmaps = iron.RenderPath.clipmaps;
	 	var clipmap = clipmaps[iron.RenderPath.clipmapLevel];

		var read_sdf = "voxelsSDF";
		var write_sdf = "voxelsSDFtmp";

	 	var passcount = Std.int(Math.ceil(Math.log(res) / Math.log(2.0)));

	 	for (i in 0...passcount) {
			kha.compute.Compute.setShader(voxel_sh2);

			kha.compute.Compute.setTexture(voxel_ta2, rts.get(read_sdf).image, kha.compute.Access.Read);
			kha.compute.Compute.setTexture(voxel_tb2, rts.get(write_sdf).image, kha.compute.Access.Write);

			var fa:Float32Array = new Float32Array(Main.voxelgiClipmapCount * 10);
			for (i in 0...Main.voxelgiClipmapCount) {
				fa[i * 10] = clipmaps[i].voxelSize;
				fa[i * 10 + 1] = clipmaps[i].extents.x;
				fa[i * 10 + 2] = clipmaps[i].extents.y;
				fa[i * 10 + 3] = clipmaps[i].extents.z;
				fa[i * 10 + 4] = clipmaps[i].center.x;
				fa[i * 10 + 5] = clipmaps[i].center.y;
				fa[i * 10 + 6] = clipmaps[i].center.z;
				fa[i * 10 + 7] = clipmaps[i].offset_prev.x;
				fa[i * 10 + 8] = clipmaps[i].offset_prev.y;
				fa[i * 10 + 9] = clipmaps[i].offset_prev.z;
			}

			kha.compute.Compute.setFloats(voxel_ca2, fa);

			kha.compute.Compute.setInt(voxel_cb2, iron.RenderPath.clipmapLevel);

			var jump_size = Math.pow(2.0, passcount - i - 1);
			kha.compute.Compute.setFloat(voxel_cc2, jump_size);

			kha.compute.Compute.compute(Std.int(res / 8), Std.int(res / 8), Std.int(res / 8));

			if (i < passcount - 1)
			{
				read_sdf = read_sdf == "voxelsSDF" ? "voxelsSDFtmp" : "voxelsSDF";
				write_sdf = write_sdf == "voxelsSDF" ? "voxelsSDFtmp" : "voxelsSDF";
			}
		}
	}
	#end

	#if arm_deferred
	#if (rp_voxels == "Voxel AO")
	public static function resolveAO() {
		var rts = path.renderTargets;
	 	var res = iron.RenderPath.getVoxelRes();
	 	var camera = iron.Scene.active.camera;
	 	var clipmaps = iron.RenderPath.clipmaps;
	 	var clipmap = clipmaps[iron.RenderPath.clipmapLevel];

		kha.compute.Compute.setShader(voxel_sh3);

		kha.compute.Compute.setSampledTexture(voxel_ta3, rts.get("voxelsOut").image);
		kha.compute.Compute.setSampledTexture(voxel_tb3, rts.get("half").image);
		kha.compute.Compute.setSampledTexture(voxel_tc3, rts.get("gbuffer0").image);
		kha.compute.Compute.setTexture(voxel_td3, rts.get("voxels_ao").image, kha.compute.Access.Write);

		var fa:Float32Array = new Float32Array(Main.voxelgiClipmapCount * 10);
		for (i in 0...Main.voxelgiClipmapCount) {
			fa[i * 10] = clipmaps[i].voxelSize;
			fa[i * 10 + 1] = clipmaps[i].extents.x;
			fa[i * 10 + 2] = clipmaps[i].extents.y;
			fa[i * 10 + 3] = clipmaps[i].extents.z;
			fa[i * 10 + 4] = clipmaps[i].center.x;
			fa[i * 10 + 5] = clipmaps[i].center.y;
			fa[i * 10 + 6] = clipmaps[i].center.z;
			fa[i * 10 + 7] = clipmaps[i].offset_prev.x;
			fa[i * 10 + 8] = clipmaps[i].offset_prev.y;
			fa[i * 10 + 9] = clipmaps[i].offset_prev.z;
		}

		kha.compute.Compute.setFloats(voxel_ca3, fa);

		#if arm_centerworld
		m.setFrom(vmat(camera.V));
		#else
		m.setFrom(camera.V);
		#end
		m.multmat(camera.P);
		m.getInverse(m);

		kha.compute.Compute.setMatrix(voxel_cb3, m.self);

		var near = camera.data.raw.near_plane;
		var far = camera.data.raw.far_plane;
		var v = new iron.math.Vec2();
		v.x = far / (far - near);
		v.y = (-far * near) / (far - near);

		kha.compute.Compute.setFloat2(voxel_cc3, v.x, v.y);


		kha.compute.Compute.setFloat3(voxel_cd3, camera.transform.worldx(), camera.transform.worldy(), camera.transform.worldz());
		var eyeLook = camera.lookWorld().normalize();
		kha.compute.Compute.setFloat3(voxel_ce3, eyeLook.x, eyeLook.y, eyeLook.z);

		var width = iron.App.w();
		var height = iron.App.h();
		var dp = getDisplayp();
		if (dp != null) { // 1080p/..
			if (width > height) {
				width = Std.int(width * (dp / height));
				height = dp;
			}
			else {
				height = Std.int(height * (dp / width));
				width = dp;
			}
		}
		kha.compute.Compute.setFloat2(voxel_cf3, width, height);

		kha.compute.Compute.compute(Std.int((width + 7) / 8), Std.int((height + 7) / 8), 1);
	}

	#else
	public static function resolveDiffuse() {
		var rts = path.renderTargets;
	 	var res = iron.RenderPath.getVoxelRes();
	 	var camera = iron.Scene.active.camera;
	 	var clipmaps = iron.RenderPath.clipmaps;
	 	var clipmap = clipmaps[iron.RenderPath.clipmapLevel];

		kha.compute.Compute.setShader(voxel_sh3);

		kha.compute.Compute.setSampledTexture(voxel_ta3, rts.get("voxelsOut").image);
		kha.compute.Compute.setSampledTexture(voxel_tb3, rts.get("half").image); // we should use path.depthToRenderTarget.get("main").image but it doesn't work
		kha.compute.Compute.setSampledTexture(voxel_tc3, rts.get("gbuffer0").image);
		kha.compute.Compute.setTexture(voxel_td3, rts.get("voxels_diffuse").image, kha.compute.Access.Write);

		var fa:Float32Array = new Float32Array(Main.voxelgiClipmapCount * 10);
		for (i in 0...Main.voxelgiClipmapCount) {
			fa[i * 10] = clipmaps[i].voxelSize;
			fa[i * 10 + 1] = clipmaps[i].extents.x;
			fa[i * 10 + 2] = clipmaps[i].extents.y;
			fa[i * 10 + 3] = clipmaps[i].extents.z;
			fa[i * 10 + 4] = clipmaps[i].center.x;
			fa[i * 10 + 5] = clipmaps[i].center.y;
			fa[i * 10 + 6] = clipmaps[i].center.z;
			fa[i * 10 + 7] = clipmaps[i].offset_prev.x;
			fa[i * 10 + 8] = clipmaps[i].offset_prev.y;
			fa[i * 10 + 9] = clipmaps[i].offset_prev.z;
		}

		kha.compute.Compute.setFloats(voxel_ca3, fa);

		#if arm_centerworld
		m.setFrom(vmat(camera.V));
		#else
		m.setFrom(camera.V);
		#end
		m.multmat(camera.P);
		m.getInverse(m);

		kha.compute.Compute.setMatrix(voxel_cb3, m.self);

		var near = camera.data.raw.near_plane;
		var far = camera.data.raw.far_plane;
		var v = new iron.math.Vec2();
		v.x = far / (far - near);
		v.y = (-far * near) / (far - near);

		kha.compute.Compute.setFloat2(voxel_cc3, v.x, v.y);


		kha.compute.Compute.setFloat3(voxel_cd3, camera.transform.worldx(), camera.transform.worldy(), camera.transform.worldz());
		var eyeLook = camera.lookWorld().normalize();
		kha.compute.Compute.setFloat3(voxel_ce3, eyeLook.x, eyeLook.y, eyeLook.z);

		var width = iron.App.w();
		var height = iron.App.h();
		var dp = getDisplayp();
		if (dp != null) { // 1080p/..
			if (width > height) {
				width = Std.int(width * (dp / height));
				height = dp;
			}
			else {
				height = Std.int(height * (dp / width));
				width = dp;
			}
		}
		kha.compute.Compute.setFloat2(voxel_cf3, width, height);

		kha.compute.Compute.compute(Std.int((width + 7) / 8), Std.int((height + 7) / 8), 1);
	}

	public static function resolveSpecular() {
		var rts = path.renderTargets;
	 	var res = iron.RenderPath.getVoxelRes();
	 	var camera = iron.Scene.active.camera;
	 	var clipmaps = iron.RenderPath.clipmaps;
	 	var clipmap = clipmaps[iron.RenderPath.clipmapLevel];

		kha.compute.Compute.setShader(voxel_sh4);

		kha.compute.Compute.setSampledTexture(voxel_ta4, rts.get("voxelsOut").image);
		kha.compute.Compute.setSampledTexture(voxel_tb4, rts.get("half").image);
		kha.compute.Compute.setSampledTexture(voxel_tc4, rts.get("gbuffer0").image);
		kha.compute.Compute.setSampledTexture(voxel_td4, rts.get("voxelsSDF").image);
		kha.compute.Compute.setTexture(voxel_te4, rts.get("voxels_specular").image, kha.compute.Access.Write);

		var fa:Float32Array = new Float32Array(Main.voxelgiClipmapCount * 10);
		for (i in 0...Main.voxelgiClipmapCount) {
			fa[i * 10] = clipmaps[i].voxelSize;
			fa[i * 10 + 1] = clipmaps[i].extents.x;
			fa[i * 10 + 2] = clipmaps[i].extents.y;
			fa[i * 10 + 3] = clipmaps[i].extents.z;
			fa[i * 10 + 4] = clipmaps[i].center.x;
			fa[i * 10 + 5] = clipmaps[i].center.y;
			fa[i * 10 + 6] = clipmaps[i].center.z;
			fa[i * 10 + 7] = clipmaps[i].offset_prev.x;
			fa[i * 10 + 8] = clipmaps[i].offset_prev.y;
			fa[i * 10 + 9] = clipmaps[i].offset_prev.z;
		}

		kha.compute.Compute.setFloats(voxel_ca4, fa);

		#if arm_centerworld
		m.setFrom(vmat(camera.V));
		#else
		m.setFrom(camera.V);
		#end
		m.multmat(camera.P);
		m.getInverse(m);

		kha.compute.Compute.setMatrix(voxel_cb4, m.self);

		var near = camera.data.raw.near_plane;
		var far = camera.data.raw.far_plane;
		var v = new iron.math.Vec2();
		v.x = far / (far - near);
		v.y = (-far * near) / (far - near);

		kha.compute.Compute.setFloat2(voxel_cc4, v.x, v.y);


		kha.compute.Compute.setFloat3(voxel_cd4, camera.transform.worldx(), camera.transform.worldy(), camera.transform.worldz());
		var eyeLook = camera.lookWorld().normalize();
		kha.compute.Compute.setFloat3(voxel_ce4, eyeLook.x, eyeLook.y, eyeLook.z);

		var width = iron.App.w();
		var height = iron.App.h();
		var dp = getDisplayp();
		if (dp != null) { // 1080p/..
			if (width > height) {
				width = Std.int(width * (dp / height));
				height = dp;
			}
			else {
				height = Std.int(height * (dp / width));
				width = dp;
			}
		}
		kha.compute.Compute.setFloat2(voxel_cf4, width, height);

		kha.compute.Compute.compute(Std.int((width + 7) / 8), Std.int((height + 7) / 8), 1);
	}
	#end // voxel ao
	#end // deferred

	#if (rp_voxels == "Voxel GI")
	public static function computeVoxelsLight() {
		var rts = path.renderTargets;
	 	var res = iron.RenderPath.getVoxelRes();
	 	var camera = iron.Scene.active.camera;
	 	var clipmaps = iron.RenderPath.clipmaps;
	 	var clipmap = clipmaps[iron.RenderPath.clipmapLevel];
		var lights = iron.Scene.active.lights;

	 	pointIndex = spotIndex = 0;
	 	for (i in 0...lights.length) {
	 		var l = lights[i];
	 		if (!l.visible) continue;
	 		path.light = l;

	 		kha.compute.Compute.setShader(voxel_sh5);

			kha.compute.Compute.setTexture(voxel_ta5, rts.get("voxelsLight").image, kha.compute.Access.Write);
			kha.compute.Compute.setTexture(voxel_th5, rts.get("voxels").image, kha.compute.Access.Read);

			var fa:Float32Array = new Float32Array(Main.voxelgiClipmapCount * 10);
			for (i in 0...Main.voxelgiClipmapCount) {
				fa[i * 10] = clipmaps[i].voxelSize;
				fa[i * 10 + 1] = clipmaps[i].extents.x;
				fa[i * 10 + 2] = clipmaps[i].extents.y;
				fa[i * 10 + 3] = clipmaps[i].extents.z;
				fa[i * 10 + 4] = clipmaps[i].center.x;
				fa[i * 10 + 5] = clipmaps[i].center.y;
				fa[i * 10 + 6] = clipmaps[i].center.z;
				fa[i * 10 + 7] = clipmaps[i].offset_prev.x;
				fa[i * 10 + 8] = clipmaps[i].offset_prev.y;
				fa[i * 10 + 9] = clipmaps[i].offset_prev.z;
			}

			kha.compute.Compute.setFloats(voxel_ca5, fa);

			kha.compute.Compute.setInt(voxel_cb5, iron.RenderPath.clipmapLevel);

	 		#if rp_shadowmap
	 		if (l.data.raw.type == "sun") {
				#if arm_shadowmap_atlas
	 			kha.compute.Compute.setSampledTexture(voxel_tb5, rts.get("shadowMapAtlasSun").image);
	 			kha.compute.Compute.setSampledTexture(voxel_te5, rts.get("shadowMapAtlasSunTransparent").image);
	 			#else
	 			kha.compute.Compute.setSampledTexture(voxel_tb5, rts.get("shadowMap").image);
	 			kha.compute.Compute.setSampledTexture(voxel_te5, rts.get("shadowMapTransparent").image);
	 			#end
	 			kha.compute.Compute.setInt(voxel_ch5, 1); // lightShadow
	 		}
	 		else if (l.data.raw.type == "spot" || l.data.raw.type == "area") {
				#if arm_shadowmap_atlas
	 			kha.compute.Compute.setSampledTexture(voxel_tc5, rts.get("shadowMapAtlasSpot").image);
	 			kha.compute.Compute.setSampledTexture(voxel_tf5, rts.get("shadowMapAtlasSpotTransparent").image);
	 			#else
	 			kha.compute.Compute.setSampledTexture(voxel_tc5, rts.get("shadowMapSpot[" + spotIndex + "]").image);
	 			kha.compute.Compute.setSampledTexture(voxel_tf5, rts.get("shadowMapSpotTransparent[" + spotIndex + "]").image);
	 			spotIndex++;
	 			#end
	 			kha.compute.Compute.setInt(voxel_ch5, 2);
	 		}
	 		else {
				#if arm_shadowmap_atlas
				kha.compute.Compute.setSampledTexture(voxel_td5, rts.get("shadowMapAtlasPoint").image);
				kha.compute.Compute.setSampledTexture(voxel_tg5, rts.get("shadowMapAtlasPointTransparent").image);
				kha.compute.Compute.setInt(voxel_cl5, i);
				kha.compute.Compute.setFloats(voxel_cm5, iron.object.LightObject.pointLightsData);
				#else
	 			kha.compute.Compute.setSampledCubeMap(voxel_td5, rts.get("shadowMapPoint[" + pointIndex + "]").cubeMap);
	 			kha.compute.Compute.setSampledCubeMap(voxel_tg5, rts.get("shadowMapPointTransparent[" + pointIndex + "]").cubeMap);
	 			pointIndex++;
	 			#end
	 			kha.compute.Compute.setInt(voxel_ch5, 3);
	 		}

	 		// lightProj
	 		var near = l.data.raw.near_plane;
	 		var far = l.data.raw.far_plane;
	 		var a:kha.FastFloat = far + near;
	 		var b:kha.FastFloat = far - near;
	 		var f2:kha.FastFloat = 2.0;
	 		var c:kha.FastFloat = f2 * far * near;
	 		var vx:kha.FastFloat = a / b;
	 		var vy:kha.FastFloat = c / b;
	 		kha.compute.Compute.setFloat2(voxel_ci5, vx, vy);
	 		// LVP
	 		m.setFrom(l.VP);
	 		m.multmat(iron.object.Uniforms.biasMat);
	 		/*
	 		#if arm_shadowmap_atlas
			if (l.data.raw.type == "sun")
			{
				// tile matrix
				m.setIdentity();
				// scale [0-1] coords to [0-tilescale]
				m2._00 = l.tileScale[0];
				m2._11 = l.tileScale[0];
				// offset coordinate start from [0, 0] to [tile-start-x, tile-start-y]
				m2._30 = l.tileOffsetX[0];
				m2._31 = l.tileOffsetY[0];
				m.multmat(m2);
				#if (!kha_opengl)
				m2.setIdentity();
				m2._11 = -1.0;
				m2._31 = 1.0;
				m.multmat(m2);
				#end
			}
			#end
			*/
	 		kha.compute.Compute.setMatrix(voxel_cj5, m.self);
	 		// shadowsBias
	 		kha.compute.Compute.setFloat(voxel_ck5, l.data.raw.shadows_bias);
			#end // rp_shadowmap

	 		// lightPos
	 		kha.compute.Compute.setFloat3(voxel_cc5, l.transform.worldx(), l.transform.worldy(), l.transform.worldz());
	 		// lightCol
	 		var f = l.data.raw.strength;
	 		kha.compute.Compute.setFloat3(voxel_cd5, l.data.raw.color[0] * f, l.data.raw.color[1] * f, l.data.raw.color[2] * f);
	 		// lightType
	 		kha.compute.Compute.setInt(voxel_ce5, iron.data.LightData.typeToInt(l.data.raw.type));
	 		// lightDir
	 		var v = l.look();
	 		kha.compute.Compute.setFloat3(voxel_cf5, v.x, v.y, v.z);
	 		// spotData
	 		if (l.data.raw.type == "spot") {
	 			var vx = l.data.raw.spot_size;
	 			var vy = vx - l.data.raw.spot_blend;
	 			kha.compute.Compute.setFloat2(voxel_cg5, vx, vy);
	 		}

	 		kha.compute.Compute.compute(Std.int(res / 8), Std.int(res / 8), Std.int(res / 8));
		}
	}
	#end // GI
	#end // Voxels
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

	function new(light: LightObject, transparent: Bool) {

		var maxTileSize = shadowMapAtlasSize(light);
		this.target = shadowMapAtlasName(light.data.raw.type, transparent);
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
	public static function addLight(light: LightObject, transparent: Bool) {
		var atlasName = shadowMapAtlasName(light.data.raw.type, transparent);
		var atlas = shadowMapAtlases.get(atlasName);
		if (atlas == null) {
			// create a new atlas
			atlas = new ShadowMapAtlas(light, transparent);
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

	public static inline function shadowMapAtlasName(type: String, transparent: Bool): String {
		#if arm_shadowmap_atlas_single_map
		return transparent ? "shadowMapAtlasTranparent" : "shadowMapAtlas";
		#else
		switch (type) {
			case "point":
				return transparent ? "shadowMapAtlasPointTransparent" : "shadowMapAtlasPoint";
			case "sun":
				return transparent ? "shadowMapAtlasSunTransparent" : "shadowMapAtlasSun";
			default:
				return transparent ? "shadowMapAtlasSpotTransparent" : "shadowMapAtlasSpot";
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
			#elseif (rp_shadowmap_atlas_max_size == 32768)
			return 32768;
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
				#elseif (rp_shadowmap_atlas_max_size_point == 32768)
				return 32768;
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
				#elseif (rp_shadowmap_atlas_max_size_spot == 32768)
				return 32768;
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
				#elseif (rp_shadowmap_atlas_max_size_sun == 32768)
				return 32768;
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
				#elseif (rp_shadowmap_atlas_max_size == 32768)
				return 32768;
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
