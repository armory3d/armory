package armory.renderpath;

import iron.RenderPath;

class Inc {

	static var path:RenderPath;

	#if (rp_gi == "Voxel GI")
	static var voxel_sh:kha.compute.Shader = null;
	static var voxel_ta:kha.compute.TextureUnit;
	static var voxel_tb:kha.compute.TextureUnit;
	static var voxel_tc:kha.compute.TextureUnit;
	static var voxel_td:kha.compute.TextureUnit;
	static var voxel_te:kha.compute.TextureUnit;
	static var voxel_ca:kha.compute.ConstantLocation;
	static var voxel_cb:kha.compute.ConstantLocation;
	static var voxel_cc:kha.compute.ConstantLocation;
	static var voxel_cd:kha.compute.ConstantLocation;
	static var voxel_ce:kha.compute.ConstantLocation;
	static var voxel_cf:kha.compute.ConstantLocation;
	static var voxel_cg:kha.compute.ConstantLocation;
	static var voxel_ch:kha.compute.ConstantLocation;
	static var voxel_ci:kha.compute.ConstantLocation;
	static var m = iron.math.Mat4.identity();
	#end
	#if (rp_gi_bounces)
	static var bounce_sh:kha.compute.Shader = null;
	static var bounce_ta:kha.compute.TextureUnit;
	static var bounce_tb:kha.compute.TextureUnit;
	static var bounce_tc:kha.compute.TextureUnit;
	#end

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

	#if (rp_gi == "Voxel GI")
	public static function computeVoxels() {
		if (voxel_sh == null) {
			voxel_sh = path.getComputeShader("voxel_light");
			voxel_ta = voxel_sh.getTextureUnit("voxelsOpac");
			voxel_tb = voxel_sh.getTextureUnit("voxelsNor");
			voxel_tc = voxel_sh.getTextureUnit("voxels");
			voxel_td = voxel_sh.getTextureUnit("shadowMap");
			voxel_te = voxel_sh.getTextureUnit("shadowMapCube");
			
			voxel_ca = voxel_sh.getConstantLocation("lightPos");
			voxel_cb = voxel_sh.getConstantLocation("lightColor");
			voxel_cc = voxel_sh.getConstantLocation("lightType");
			voxel_cd = voxel_sh.getConstantLocation("lightDir");
			voxel_ce = voxel_sh.getConstantLocation("lightShadow");
			voxel_cf = voxel_sh.getConstantLocation("lightProj");
			voxel_cg = voxel_sh.getConstantLocation("LVP");
			voxel_ch = voxel_sh.getConstantLocation("shadowsBias");
			voxel_ci = voxel_sh.getConstantLocation("spotData");
		}

		var rts = path.renderTargets;
		var res = Inc.getVoxelRes();

		path.clearImage("voxels", 0x00000000);

		var lamps = iron.Scene.active.lamps;
		for (i in 0...lamps.length) {
			var l = lamps[i];
			if (!l.visible) continue;
			path.currentLampIndex = i;

			#if ((rp_shadowmap))
			{
				// TODO: merge with direct, drawing shadowmaps twice!
				if (path.lampCastShadow()) {
					drawShadowMap(l);
				}
			}
			#end

			kha.compute.Compute.setShader(voxel_sh);
			kha.compute.Compute.setTexture(voxel_ta, rts.get("voxelsOpac").image, kha.compute.Access.Read);
			kha.compute.Compute.setTexture(voxel_tb, rts.get("voxelsNor").image, kha.compute.Access.Read);
			kha.compute.Compute.setTexture(voxel_tc, rts.get("voxels").image, kha.compute.Access.Write);

			#if (rp_shadowmap)
			if (Inc.shadowMapName() == "shadowMapCube") {
				// shadowMapCube
				kha.compute.Compute.setSampledCubeMap(voxel_te, rts.get("shadowMapCube").cubeMap);
			}
			else {
				// shadowMap
				kha.compute.Compute.setSampledTexture(voxel_td, rts.get("shadowMap").image);
			}
			#end

			// lightPos
			kha.compute.Compute.setFloat3(voxel_ca, l.transform.worldx(), l.transform.worldy(), l.transform.worldz());
			// lightCol
			var f = l.data.raw.strength;
			kha.compute.Compute.setFloat3(voxel_cb, l.data.raw.color[0] * f, l.data.raw.color[1] * f, l.data.raw.color[2] * f);
			// lightType
			kha.compute.Compute.setInt(voxel_cc, iron.data.LampData.typeToInt(l.data.raw.type));
			// lightDir
			var v = l.look();
			kha.compute.Compute.setFloat3(voxel_cd, v.x, v.y, v.z);
			// lightShadow
			var i = l.data.raw.shadowmap_cube ? 2 : 1;
			kha.compute.Compute.setInt(voxel_ce, i);
			// lightProj
			var near = l.data.raw.near_plane;
			var far = l.data.raw.far_plane;
			var a = far + near;
			var b = far - near;
			var c = 2.0 * far * near;
			var vx = a / b;
			var vy = c / b;
			kha.compute.Compute.setFloat2(voxel_cf, vx, vy);
			// LVP
			m.setFrom(l.VP);
			m.multmat2(iron.object.Uniforms.biasMat);
			kha.compute.Compute.setMatrix(voxel_cg, m.self);
			// shadowsBias
			kha.compute.Compute.setFloat(voxel_ch, l.data.raw.shadows_bias);
			// spotData
			if (l.data.raw.type == "spot") {
				var vx = l.data.raw.spot_size;
				var vy = vx - l.data.raw.spot_blend;
				kha.compute.Compute.setFloat2(voxel_ci, vx, vy);
			}

			kha.compute.Compute.compute(res, res, res);
		}
		path.currentLampIndex = 0;

		path.generateMipmaps("voxels");

		#if (rp_gi_bounces)
		if (bounce_sh == null) {
			bounce_sh = path.getComputeShader("voxel_bounce");
			bounce_ta = bounce_sh.getTextureUnit("voxelsNor");
			bounce_tb = bounce_sh.getTextureUnit("voxelsFrom");
			bounce_tc = bounce_sh.getTextureUnit("voxelsTo");
		}
		// path.clearImage("voxelsOpac", 0x00000000);
		// path.currentG;
		kha.compute.Compute.setShader(bounce_sh);
		kha.compute.Compute.setTexture(bounce_ta, rts.get("voxelsNor").image, kha.compute.Access.Read);
		kha.compute.Compute.setTexture3DParameters(bounce_tb, kha.graphics4.TextureAddressing.Clamp, kha.graphics4.TextureAddressing.Clamp, kha.graphics4.TextureAddressing.Clamp, kha.graphics4.TextureFilter.LinearFilter, kha.graphics4.TextureFilter.PointFilter, kha.graphics4.MipMapFilter.LinearMipFilter);
		kha.compute.Compute.setSampledTexture(bounce_tb, rts.get("voxels").image);
		kha.compute.Compute.setTexture(bounce_tc, rts.get("voxelsOpac").image, kha.compute.Access.Write);
		kha.compute.Compute.compute(res, res, res);
		path.generateMipmaps("voxelsOpac");
		#end
	}
	#end

	#if (rp_renderer == "Forward")
	public static function drawShadowMap(l:iron.object.LampObject) {
		#if (rp_shadowmap)
		var faces = path.getLamp(path.currentLampIndex).data.raw.shadowmap_cube ? 6 : 1;
		for (i in 0...faces) {
			if (faces > 1) path.currentFace = i;
			path.setTarget(Inc.getShadowMap());
			path.clearTarget(null, 1.0);
			path.drawMeshes("shadowmap");
		}
		path.currentFace = -1;
		#end
	}
	#else
	public static function drawShadowMap(l:iron.object.LampObject) {
		#if (rp_shadowmap)
		var faces = l.data.raw.shadowmap_cube ? 6 : 1;
		for (j in 0...faces) {
			if (faces > 1) path.currentFace = j;
			path.setTarget(Inc.getShadowMap());
			path.clearTarget(null, 1.0);
			path.drawMeshes("shadowmap");
		}
		path.currentFace = -1;

		// One lamp at a time for now, precompute all lamps for tiled
		#if rp_soft_shadows

		if (l.raw.type != "point") {
			path.setTarget("visa"); // Merge using min blend
			Inc.bindShadowMap();
			path.drawShader("shader_datas/dilate_pass/dilate_pass_x");

			path.setTarget("visb");
			path.bindTarget("visa", "shadowMap");
			path.drawShader("shader_datas/dilate_pass/dilate_pass_y");
		}

		path.setTarget("visa", ["dist"]);
		//if (i == 0) path.clearTarget(0x00000000);
		if (l.raw.type != "point") path.bindTarget("visb", "dilate");
		Inc.bindShadowMap();
		//path.bindTarget("_main", "gbufferD");
		path.bindTarget("gbuffer0", "gbuffer0");
		path.drawShader("shader_datas/visibility_pass/visibility_pass");
		
		path.setTarget("visb");
		path.bindTarget("visa", "tex");
		path.bindTarget("gbuffer0", "gbuffer0");
		path.bindTarget("dist", "dist");
		path.drawShader("shader_datas/blur_shadow_pass/blur_shadow_pass_x");

		path.setTarget("visa");
		path.bindTarget("visb", "tex");
		path.bindTarget("gbuffer0", "gbuffer0");
		path.bindTarget("dist", "dist");
		path.drawShader("shader_datas/blur_shadow_pass/blur_shadow_pass_y");
		#end

		#end
	}
	#end
}
