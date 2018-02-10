package armory.renderpath;

import iron.RenderPath;

class Inc {

	static var path:RenderPath;

	public static function init(_path:RenderPath) {
		path = _path;
	}

	public static function bindShadowMap() {
		var target = shadowMapName();
		if (target == "shadowMapCube") {
			#if kha_webgl
			// Bind empty map to non-cubemap sampler to keep webgl happy
			path.bindTarget("arm_empty", "shadowMap");
			#end
			path.bindTarget("shadowMapCube", "shadowMapCube");
		}
		else {
			#if kha_webgl
			// Bind empty map to cubemap sampler
			if (!path.lampIsSun()) path.bindTarget("arm_empty_cube", "shadowMapCube");
			#end
			path.bindTarget("shadowMap", "shadowMap");
		}
	}

	public static function shadowMapName():String {
		return path.getLamp(path.currentLampIndex).data.raw.shadowmap_cube ? "shadowMapCube" : "shadowMap";
	}

	public static function getShadowMap():String {
		var target = shadowMapName();
		var rt = path.renderTargets.get(target);
		// Create shadowmap on the fly
		if (rt == null) {
			if (path.getLamp(path.currentLampIndex).data.raw.shadowmap_cube) {
				// Cubemap size
				var size = Std.int(path.getLamp(path.currentLampIndex).data.raw.shadowmap_size);
				var t = new RenderTargetRaw();
				t.name = target;
				t.width = size;
				t.height = size;
				t.format = "DEPTH16";
				t.is_cubemap = true;
				rt = path.createRenderTarget(t);
			}
			else { // Non-cube sm
				var sizew = path.getLamp(path.currentLampIndex).data.raw.shadowmap_size;
				var sizeh = sizew;
				#if arm_csm // Cascades - atlas on x axis
				sizew = sizeh * iron.object.LampObject.cascadeCount;
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

	#if (rp_shadowmap && kha_webgl)
	public static function initEmpty() {
		// Bind empty when requested target is not found
		var tempty = new RenderTargetRaw();
		tempty.name = "arm_empty";
		tempty.width = 1;
		tempty.height = 1;
		tempty.format = "DEPTH16";
		path.createRenderTarget(tempty);
		var temptyCube = new RenderTargetRaw();
		temptyCube.name = "arm_empty_cube";
		temptyCube.width = 1;
		temptyCube.height = 1;
		temptyCube.format = "DEPTH16";
		temptyCube.is_cubemap = true;
		path.createRenderTarget(temptyCube);
	}
	#end

	#if (rp_translucency)
	public static function initTranslucency() {
		path.createDepthBuffer("main", "DEPTH24");

		var t = new RenderTargetRaw();
		t.name = "accum";
		t.width = 0;
		t.height = 0;
		t.displayp = getDisplayp();
		t.format = "RGBA64";
		var ss = getSuperSampling();
		if (ss != 1) t.scale = ss;
		t.depth_buffer = "main";
		path.createRenderTarget(t);

		var t = new RenderTargetRaw();
		t.name = "revealage";
		t.width = 0;
		t.height = 0;
		t.displayp = getDisplayp();
		t.format = "RGBA64";
		var ss = getSuperSampling();
		if (ss != 1) t.scale = ss;
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

	#if (rp_gi != "Off")
	public static function initGI(tname = "voxels") {
		var t = new RenderTargetRaw();
		t.name = tname;
		#if (rp_gi == "Voxel AO")
		{
			t.format = "R8";
		}
		#elseif (rp_voxelgi_hdr)
		{
			t.format = "RGBA64";
		}
		#else
		{
			t.format = "RGBA32";
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
	}
	#end

	public static inline function getShadowmapSize():Int {
		#if (rp_shadowmap_size == 512)
		return 512;
		#elseif (rp_shadowmap_size == 1024)
		return 1024;
		#elseif (rp_shadowmap_size == 2048)
		return 2048;
		#elseif (rp_shadowmap_size == 4096)
		return 4096;
		#elseif (rp_shadowmap_size == 8192)
		return 8192;
		#elseif (rp_shadowmap_size == 16384)
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
		#if (rp_supersampling == 1.5)
		return 1.5;
		#elseif (rp_supersampling == 2)
		return 2;
		#elseif (rp_supersampling == 4)
		return 4;
		#else
		return 1;
		#end
	}

	public static inline function getHdrFormat():String {
		#if rp_hdr
		return "RGBA64";
		#else
		return "RGBA32";
		#end
	}

	public static inline function getDisplayp():Null<Int> {
		#if (rp_resolution == 480)
		return 480;
		#elseif (rp_resolution == 720)
		return 720;
		#elseif (rp_resolution == 1080)
		return 1080;
		#elseif (rp_resolution == 1440)
		return 1440;
		#elseif (rp_resolution == 2160)
		return 2160;
		#else
		return null;
		#end
	}

	public static inline function getRenderCaptureFormat():String {
		#if (rp_rendercapture_format == "8bit")
		return "RGBA32";
		#elseif (rp_rendercapture_format == "16bit")
		return "RGBA64";
		#elseif (rp_rendercapture_format == "32bit")
		return "RGBA128";
		#else
		return "RGBA32";
		#end
	}
}
