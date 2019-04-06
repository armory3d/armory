package armory.renderpath;

import iron.RenderPath;

class Inc {

	static var path:RenderPath;
	public static var superSample = 1.0;

	static var pointIndex = 0;
	static var spotIndex = 0;
	static var lastFrame = -1;

	#if (rp_voxelao && arm_config)
	static var voxelsCreated = false;
	#end

	public static function init(_path:RenderPath) {
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

	public static function bindShadowMap() {
		for (l in iron.Scene.active.lights) {
			if (!l.visible || !l.data.raw.cast_shadow || l.data.raw.type != "sun") continue;
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

	static function shadowMapName(l:iron.object.LightObject):String {
		if (l.data.raw.type == "sun") return "shadowMap";
		if (l.data.raw.type == "point") return "shadowMapPoint[" + pointIndex + "]";
		else return "shadowMapSpot[" + spotIndex + "]"; 
	}

	static function getShadowMap(l:iron.object.LightObject):String {
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
			if (!l.visible || !l.data.raw.cast_shadow) continue;
			path.light = l;
			var shadowmap = Inc.getShadowMap(l);
			var faces = l.data.raw.shadowmap_cube ? 6 : 1;
			for (i in 0...faces) {
				if (faces > 1) path.currentFace = i;
				path.setTarget(shadowmap);
				path.clearTarget(null, 1.0);
				path.drawMeshes("shadowmap");
			}
			path.currentFace = -1;

			if (l.data.raw.type == "point") pointIndex++;
			else if (l.data.raw.type == "spot" || l.data.raw.type == "area") spotIndex++;
		}
		
		#end // rp_shadowmap
	}
	
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
		#if rp_voxelao
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

	public static function drawTranslucency(target:String) {
		path.setTarget("accum");
		path.clearTarget(0xff000000);
		path.setTarget("revealage");
		path.clearTarget(0xffffffff);
		path.setTarget("accum", ["revealage"]);
		#if rp_shadowmap
		{
			bindShadowMap();
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

	#if rp_voxelao
	public static function initGI(tname = "voxels") {
		#if arm_config
		var config = armory.data.Config.raw;
		if (config.rp_gi != true || voxelsCreated) return;
		voxelsCreated = true;
		#end

		var t = new RenderTargetRaw();
		t.name = tname;
		t.format = "R8";
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

	public static inline function getCubeSize():Int {
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

	public static inline function getCascadeSize():Int {
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

	public static inline function getVoxelRes():Int {
		#if (rp_voxelgi_resolution == 512)
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

	public static inline function getVoxelResZ():Float {
		#if (rp_voxelgi_resolution_z == 1.0)
		return 1.0;
		#elseif (rp_voxelgi_resolution_z == 0.5)
		return 0.5;
		#elseif (rp_voxelgi_resolution_z == 0.25)
		return 0.25;
		#else
		return 0.0;
		#end
	}

	public static inline function getSuperSampling():Float {
		return superSample;
	}

	public static inline function getHdrFormat():String {
		#if rp_hdr
		return "RGBA64";
		#else
		return "RGBA32";
		#end
	}

	public static inline function getDisplayp():Null<Int> {
		#if rp_resolution_filter // Custom resolution set
		return Main.resolutionSize;
		#else
		return null;
		#end
	}
}
