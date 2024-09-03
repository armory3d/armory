package armory.renderpath;

import iron.RenderPath;
import iron.Scene;
import iron.object.Clipmap;

class RenderPathForward {

	#if (rp_renderer == "Forward")

	static var path: RenderPath;

	#if (rp_voxels != "Off")
	static var res_pre_clear = true;
	#end

	#if rp_bloom
	static var bloomDownsampler: Downsampler;
	static var bloomUpsampler: Upsampler;
	#end

	public static function setTargetMeshes() {
		#if rp_render_to_texture
		{
			path.setTarget("lbuffer0", [
				#if (rp_ssr || rp_ssrefr) "lbuffer1",  #end
				#if rp_ssrefr "gbuffer_refraction" #end]
			);
		}
		#else
		{
			path.setTarget("");
		}
		#end
	}

	public static function drawMeshes() {
		path.drawMeshes("mesh");

		#if (rp_background == "World")
		{
			if (Scene.active.raw.world_ref != null) {
				RenderPathCreator.setTargetMeshes();
				path.drawSkydome("shader_datas/World_" + Scene.active.raw.world_ref + "/World_" + Scene.active.raw.world_ref);
			}
		}
		#end

		#if rp_blending
		{
			RenderPathCreator.setTargetMeshes();
			path.drawMeshes("blend");
		}
		#end

		#if (rp_translucency && !rp_ssrefr)
		{
			RenderPathCreator.setTargetMeshes();
			Inc.drawTranslucency("lbuffer0");
		}
		#end
	}

	public static function applyConfig() {
		Inc.applyConfig();
	}

	public static function init(_path: RenderPath) {

		path = _path;

		#if kha_metal
		{
			path.loadShader("shader_datas/clear_color_depth_pass/clear_color_depth_pass");
			path.loadShader("shader_datas/clear_color_pass/clear_color_pass");
			path.loadShader("shader_datas/clear_depth_pass/clear_depth_pass");
			path.clearShader = "shader_datas/clear_color_depth_pass/clear_color_depth_pass";
		}
		#end

		#if rp_depth_texture
		{
			var t = new RenderTargetRaw();
			t.name = "depthtex";
			t.width = 0;
			t.height = 0;
			t.displayp = Inc.getDisplayp();
			t.format = "R32";
			t.scale = Inc.getSuperSampling();
			path.createRenderTarget(t);
		}
		#end

		#if (rp_render_to_texture)
		{
			path.createDepthBuffer("main", "DEPTH24");

			var t = new RenderTargetRaw();
			t.name = "lbuffer0";
			t.width = 0;
			t.height = 0;
			t.format = Inc.getHdrFormat();
			t.displayp = Inc.getDisplayp();
			t.scale = Inc.getSuperSampling();
			t.depth_buffer = "main";
			path.createRenderTarget(t);

			#if rp_ssr
			{
				var t = new RenderTargetRaw();
				t.name = "lbuffer1";
				t.width = 0;
				t.height = 0;
				t.format = Inc.getHdrFormat();
				t.displayp = Inc.getDisplayp();
				t.scale = Inc.getSuperSampling();
				path.createRenderTarget(t);
			}
			#end

			#if rp_ssrefr
			{
				var t = new RenderTargetRaw();
				t.name = "gbuffer_refraction";
				t.width = 0;
				t.height = 0;
				t.displayp = Inc.getDisplayp();
				t.format = "RGBA64";
				t.scale = Inc.getSuperSampling();
				t.depth_buffer = "main";
				path.createRenderTarget(t);

				//holds colors before refractive meshes are drawn
				var t = new RenderTargetRaw();
				t.name = "refr";
				t.width = 0;
				t.height = 0;
				t.displayp = Inc.getDisplayp();
				t.format = "RGBA64";
				t.scale = Inc.getSuperSampling();
				path.createRenderTarget(t);

				//holds background depth
				var t = new RenderTargetRaw();
				t.name = "gbufferD1";
				t.width = 0;
				t.height = 0;
				t.displayp = Inc.getDisplayp();
				t.format = "R32";
				t.scale = Inc.getSuperSampling();
				path.createRenderTarget(t);
			}
			#end

			#if rp_compositornodes
			{
				path.loadShader("shader_datas/compositor_pass/compositor_pass");
			}
			#else
			{
				path.loadShader("shader_datas/copy_pass/copy_pass");
			}
			#end

			#if ((rp_supersampling == 4) || (rp_antialiasing == "SMAA") || (rp_antialiasing == "TAA") || (rp_depth_texture))
			{
				var t = new RenderTargetRaw();
				t.name = "buf";
				t.width = 0;
				t.height = 0;
				t.format = "RGBA32";
				t.displayp = Inc.getDisplayp();
				t.scale = Inc.getSuperSampling();
				t.depth_buffer = "main";
				path.createRenderTarget(t);
			}
			#end

			#if (rp_supersampling == 4)
			{
				path.loadShader("shader_datas/supersample_resolve/supersample_resolve");
			}
			#end
		}
		#end

		#if (rp_translucency && !rp_ssrefr)
		{
			Inc.initTranslucency();
		}
		#end

		#if (rp_voxels != "Off")
		{
			Inc.initGI("voxels");
			Inc.initGI("voxelsOut");
			Inc.initGI("voxelsOutB");
			#if (arm_voxelgi_shadows || (rp_voxels == "Voxel GI"))
			Inc.initGI("voxelsSDF");
			Inc.initGI("voxelsSDFtmp");
			#end
			#if arm_voxelgi_shadows
			Inc.initGI("voxels_shadows");
			#end
			#if (rp_voxels == "Voxel GI")
			Inc.initGI("voxelsLight");
			Inc.initGI("voxels_diffuse");
			Inc.initGI("voxels_specular");
			#else
			Inc.initGI("voxels_ao");
			#end
			iron.RenderPath.clipmaps = new Array<Clipmap>();
			for (i in 0...Main.voxelgiClipmapCount) {
				var clipmap = new iron.object.Clipmap();
				clipmap.voxelSize = Main.voxelgiVoxelSize * Math.pow(2.0, i);
				clipmap.extents = new iron.math.Vec3(0.0);
				clipmap.center = new iron.math.Vec3(0.0);
				clipmap.offset_prev = new iron.math.Vec3(0.0);
				iron.RenderPath.clipmaps.push(clipmap);
			}
		}
		#end

		#if ((rp_antialiasing == "SMAA") || (rp_antialiasing == "TAA") || (rp_ssr && !rp_ssr_half) || (rp_water) || (rp_depth_texture))
		{
			var t = new RenderTargetRaw();
			t.name = "bufa";
			t.width = 0;
			t.height = 0;
			t.displayp = Inc.getDisplayp();
			t.format = "RGBA32";
			t.scale = Inc.getSuperSampling();
			path.createRenderTarget(t);

			var t = new RenderTargetRaw();
			t.name = "bufb";
			t.width = 0;
			t.height = 0;
			t.displayp = Inc.getDisplayp();
			t.format = "RGBA32";
			t.scale = Inc.getSuperSampling();
			path.createRenderTarget(t);
		}
		#end

		#if ((rp_antialiasing == "SMAA") || (rp_antialiasing == "TAA"))
			path.loadShader("shader_datas/smaa_edge_detect/smaa_edge_detect");
			path.loadShader("shader_datas/smaa_blend_weight/smaa_blend_weight");
			path.loadShader("shader_datas/smaa_neighborhood_blend/smaa_neighborhood_blend");

			#if (rp_antialiasing == "TAA")
			{
				path.loadShader("shader_datas/taa_pass/taa_pass");
			}
			#end
		#end

		#if rp_volumetriclight
		{
			path.loadShader("shader_datas/volumetric_light/volumetric_light");
			path.loadShader("shader_datas/blur_bilat_pass/blur_bilat_pass_x");
			path.loadShader("shader_datas/blur_bilat_blend_pass/blur_bilat_blend_pass_y");

			var t = new RenderTargetRaw();
			t.name = "singlea";
			t.width = 0;
			t.height = 0;
			t.displayp = Inc.getDisplayp();
			t.format = "R8";
			t.scale = Inc.getSuperSampling();
			path.createRenderTarget(t);

			var t = new RenderTargetRaw();
			t.name = "singleb";
			t.width = 0;
			t.height = 0;
			t.displayp = Inc.getDisplayp();
			t.format = "R8";
			t.scale = Inc.getSuperSampling();
			path.createRenderTarget(t);
		}
		#end

		#if rp_water
		{
			path.loadShader("shader_datas/water_pass/water_pass");
			path.loadShader("shader_datas/copy_pass/copy_pass");
		}
		#end

		#if rp_depth_texture
		{
			path.loadShader("shader_datas/copy_pass/copy_pass");
		}
		#end

		#if rp_bloom
		{
			bloomDownsampler = Downsampler.create(path, "shader_datas/bloom_pass/downsample_pass", "bloom");
			bloomUpsampler = Upsampler.create(path, "shader_datas/bloom_pass/upsample_pass", bloomDownsampler.getMipmaps());
		}
		#end

		#if (rp_ssr_half || rp_ssgi_half || (rp_voxels != "Off"))
		{
			path.loadShader("shader_datas/downsample_depth/downsample_depth");
			var t = new RenderTargetRaw();
			t.name = "half";
			t.width = 0;
			t.height = 0;
			t.scale = Inc.getSuperSampling() * 0.5;
			t.format = "R32"; // R16
			path.createRenderTarget(t);
		}
		#end

		#if rp_ssrefr
		{
			path.loadShader("shader_datas/ssrefr_pass/ssrefr_pass");
			path.loadShader("shader_datas/copy_pass/copy_pass");
		}
		#end

		#if rp_ssr
		{
			path.loadShader("shader_datas/ssr_pass/ssr_pass");
			path.loadShader("shader_datas/blur_adaptive_pass/blur_adaptive_pass_x");
			path.loadShader("shader_datas/blur_adaptive_pass/blur_adaptive_pass_y3_blend");

			#if rp_ssr_half
			{
				var t = new RenderTargetRaw();
				t.name = "ssra";
				t.width = 0;
				t.height = 0;
				t.scale = Inc.getSuperSampling() * 0.5;
				t.format = Inc.getHdrFormat();
				path.createRenderTarget(t);

				var t = new RenderTargetRaw();
				t.name = "ssrb";
				t.width = 0;
				t.height = 0;
				t.scale = Inc.getSuperSampling() * 0.5;
				t.format = Inc.getHdrFormat();
				path.createRenderTarget(t);
			}
			#end
		}
		#end

		#if rp_chromatic_aberration
		{
			path.loadShader("shader_datas/chromatic_aberration_pass/chromatic_aberration_pass");
			path.loadShader("shader_datas/copy_pass/copy_pass");
		}
		#end
	}

	public static function commands() {
		#if rp_shadowmap
		{
			#if arm_shadowmap_atlas
			Inc.drawShadowMapAtlas();
			#else
			Inc.drawShadowMap();
			#end
		}
		#end

		// Voxels
		#if (rp_voxels != 'Off')
		if (armory.data.Config.raw.rp_gi != false)
		{
			var path = RenderPath.active;

			Inc.computeVoxelsBegin();

			if (iron.RenderPath.pre_clear == true)
			{
				#if (rp_voxels == "Voxel GI")
				path.clearImage("voxelsLight", 0x00000000);
				#end
				path.clearImage("voxels", 0x00000000);
				path.clearImage("voxelsOut", 0x00000000);
				path.clearImage("voxelsOutB", 0x00000000);
				#if (arm_voxelgi_shadows || (rp_voxels == "Voxel GI"))
				path.clearImage("voxelsSDF", 0x00000000);
				path.clearImage("voxelsSDFtmp", 0x00000000);
				#end
				iron.RenderPath.pre_clear = false;
			}
			else
			{
				#if (rp_voxels == "Voxel GI")
				path.clearImage("voxelsLight", 0x00000000);
				#end
				path.clearImage("voxels", 0x00000000);
				Inc.computeVoxelsOffsetPrev();
			}

			path.setTarget("");
			var res = iron.RenderPath.getVoxelRes();
			path.setViewport(res, res);

			path.bindTarget("voxels", "voxels");
			path.drawMeshes("voxel");

			#if (rp_voxels == "Voxel GI")
			Inc.computeVoxelsLight();
			#end
			Inc.computeVoxelsTemporal();

			#if (arm_voxelgi_shadows || (rp_voxels == "Voxel GI"))
			Inc.computeVoxelsSDF();
			#end

			if (iron.RenderPath.res_pre_clear == true)
			{
				iron.RenderPath.res_pre_clear = false;
				#if (rp_voxels == "Voxel GI")
				path.clearImage("voxels_diffuse", 0x00000000);
				path.clearImage("voxels_specular", 0x00000000);
				#else
				path.clearImage("voxels_ao", 0x00000000);
				#end
				#if arm_voxelgi_shadows
				path.clearImage("voxels_shadows", 0x00000000);
				#end
			}
		}
		#end

		RenderPathCreator.setTargetMeshes();

		#if (rp_background == "Clear")
		{
			path.clearTarget(-1, 1.0);
		}
		#else
		{
			path.clearTarget(null, 1.0);
		}
		#end

		#if rp_depthprepass
		{
			path.drawMeshes("depth");
		}
		#end

		RenderPathCreator.setTargetMeshes();

		#if rp_shadowmap
		{
			#if arm_shadowmap_atlas
			Inc.bindShadowMapAtlas();
			#else
			Inc.bindShadowMap();
			#end
		}
		#end


		#if (rp_voxels != "Off")
		if (armory.data.Config.raw.rp_gi != false)
		{
			#if (rp_voxels == "Voxel AO")
			Inc.resolveAO();
			path.bindTarget("voxels_ao", "voxels_ao");
			#else
			Inc.resolveDiffuse();
			Inc.resolveSpecular();
			path.bindTarget("voxels_diffuse", "voxels_diffuse");
			path.bindTarget("voxels_specular", "voxels_specular");
			#end
			#if arm_voxelgi_shadows
			Inc.resolveShadows();
			path.bindTarget("voxels_shadows", "voxels_shadows");
			#end
		}
		#end

		#if rp_stereo
		{
			path.drawStereo(drawMeshes);
		}
		#else
		{
			RenderPathCreator.drawMeshes();
		}
		#end

		#if (rp_render_to_texture || rp_voxels != "Off")
		{
			#if (rp_ssr_half || rp_ssgi_half || rp_voxels != "Off")
			path.setTarget("half");
			path.bindTarget("_main", "texdepth");
			path.drawShader("shader_datas/downsample_depth/downsample_depth");
			#end

			#if rp_ssrefr
			{
				if (armory.data.Config.raw.rp_ssrefr != false)
				{
					path.setTarget("gbufferD1");
					path.bindTarget("_main", "tex");
					path.drawShader("shader_datas/copy_pass/copy_pass");

					path.setTarget("refr");
					path.bindTarget("lbuffer0", "tex");
					path.drawShader("shader_datas/copy_pass/copy_pass");

					path.setTarget("lbuffer0", ["lbuffer1", "gbuffer_refraction"]);

					#if (rp_voxels != "Off")
					path.bindTarget("voxelsOut", "voxels");
					path.bindTarget("voxelsSDF", "voxelsSDF");
					#end

					path.drawMeshes("refraction");

					path.setTarget("lbuffer0");
					path.bindTarget("refr", "tex1");
					path.bindTarget("lbuffer0", "tex");
					path.bindTarget("_main", "gbufferD");
					path.bindTarget("gbufferD1", "gbufferD1");
					path.bindTarget("lbuffer1", "gbuffer0");
					path.bindTarget("gbuffer_refraction", "gbuffer_refraction");
					path.drawShader("shader_datas/ssrefr_pass/ssrefr_pass");
				}
			}
			#end

			#if rp_ssr
			{
				if (armory.data.Config.raw.rp_ssr != false) {
					#if rp_ssr_half
					var targeta = "ssra";
					var targetb = "ssrb";
					#else
					var targeta = "bufa";
					var targetb = "bufb";
					#end

					path.setTarget(targeta);
					path.bindTarget("lbuffer0", "tex");
					#if rp_ssr_half
					path.bindTarget("half", "gbufferD");
					#else
					path.bindTarget("_main", "gbufferD");
					#end
					path.bindTarget("lbuffer1", "gbuffer0");
					path.bindTarget("lbuffer0", "gbuffer1");
					path.drawShader("shader_datas/ssr_pass/ssr_pass");

					path.setTarget(targetb);
					path.bindTarget(targeta, "tex");
					path.bindTarget("lbuffer1", "gbuffer0");
					path.drawShader("shader_datas/blur_adaptive_pass/blur_adaptive_pass_x");

					path.setTarget("lbuffer0");
					path.bindTarget(targetb, "tex");
					path.bindTarget("lbuffer1", "gbuffer0");
					path.drawShader("shader_datas/blur_adaptive_pass/blur_adaptive_pass_y3_blend");
				}
			}
			#end

			#if rp_bloom
			{
				inline Inc.drawBloom("lbuffer0", bloomDownsampler, bloomUpsampler);
			}
			#end

			#if rp_volumetriclight
			{
				path.setTarget("singlea");
				path.bindTarget("_main", "gbufferD");
				#if arm_shadowmap_atlas
				Inc.bindShadowMapAtlas();
				#else
				Inc.bindShadowMap();
				#end
				path.drawShader("shader_datas/volumetric_light/volumetric_light");

				path.setTarget("singleb");
				path.bindTarget("singlea", "tex");
				path.drawShader("shader_datas/blur_bilat_pass/blur_bilat_pass_x");

				path.setTarget("lbuffer0");
				path.bindTarget("singleb", "tex");
				path.drawShader("shader_datas/blur_bilat_blend_pass/blur_bilat_blend_pass_y");
			}
			#end

			#if rp_water
			{
				path.setDepthFrom("lbuffer0", "bufa"); // Unbind depth so we can read it
				path.depthToRenderTarget.set("main", path.renderTargets.get("buf"));

				path.setTarget("bufa");
				path.bindTarget("lbuffer0", "tex");
				path.drawShader("shader_datas/copy_pass/copy_pass");

				path.setTarget("lbuffer0");
				path.bindTarget("_main", "gbufferD");
				path.bindTarget("bufa", "tex");
				path.drawShader("shader_datas/water_pass/water_pass");

				path.setDepthFrom("lbuffer0", "buf"); // Re-bind depth
				path.depthToRenderTarget.set("main", path.renderTargets.get("lbuffer0"));
			}
			#end

			#if rp_chromatic_aberration
			{
				path.setTarget("bufa");
				path.bindTarget("lbuffer0", "tex");
				path.drawShader("shader_datas/chromatic_aberration_pass/chromatic_aberration_pass");

				path.setTarget("lbuffer0");
				path.bindTarget("bufa", "tex");
				path.drawShader("shader_datas/copy_pass/copy_pass");
			}
			#end

			#if (rp_supersampling == 4)
			var framebuffer = "buf";
			#else
			var framebuffer = "";
			#end

			#if ((rp_antialiasing == "Off") || (rp_antialiasing == "FXAA"))
			{
				RenderPathCreator.finalTarget = path.currentTarget;
				path.setTarget(framebuffer);
			}
			#else
			{
				path.setTarget("buf");
				RenderPathCreator.finalTarget = path.currentTarget;
			}
			#end

			#if rp_compositordepth
			{
				path.bindTarget("_main", "gbufferD");
			}
			#end

			#if rp_compositornodes
			{
				path.bindTarget("lbuffer0", "tex");
				path.drawShader("shader_datas/compositor_pass/compositor_pass");
			}
			#else
			{
				path.bindTarget("lbuffer0", "tex");
				path.drawShader("shader_datas/copy_pass/copy_pass");
			}
			#end

			#if ((rp_antialiasing == "SMAA") || (rp_antialiasing == "TAA"))
			{
				path.setTarget("bufa");
				path.clearTarget(0x00000000);
				path.bindTarget("buf", "colorTex");
				path.drawShader("shader_datas/smaa_edge_detect/smaa_edge_detect");

				path.setTarget("bufb");
				path.clearTarget(0x00000000);
				path.bindTarget("bufa", "edgesTex");
				path.drawShader("shader_datas/smaa_blend_weight/smaa_blend_weight");

				path.setTarget(framebuffer);
				path.bindTarget("buf", "colorTex");
				path.bindTarget("bufb", "blendTex");
				path.drawShader("shader_datas/smaa_neighborhood_blend/smaa_neighborhood_blend");
			}
			#end

			#if (rp_supersampling == 4)
			{
				var finalTarget = "";
				path.setTarget(finalTarget);
				path.bindTarget(framebuffer, "tex");
				path.drawShader("shader_datas/supersample_resolve/supersample_resolve");
			}
			#end
		}
		#end

		#if rp_overlays
		{
			path.clearTarget(null, 1.0);
			path.drawMeshes("overlay");
		}
		#end
	}

	public static function setupDepthTexture() {
		// When render to texture is off, lbuffer0 does not exist, so for
		// now do nothing then and pass an empty uniform to the shader
		#if rp_render_to_texture
			#if (!kha_opengl)
			path.setDepthFrom("lbuffer0", "bufa"); // Unbind depth so we can read it
			path.depthToRenderTarget.set("main", path.renderTargets.get("buf"));
			#end

			// Copy the depth buffer to the depth texture
			path.setTarget("depthtex");
			path.bindTarget("_main", "tex");
			path.drawShader("shader_datas/copy_pass/copy_pass");

			#if (!kha_opengl)
			path.setDepthFrom("lbuffer0", "buf"); // Re-bind depth
			path.depthToRenderTarget.set("main", path.renderTargets.get("lbuffer0"));
			#end
		#end // rp_render_to_texture

		setTargetMeshes();
		path.bindTarget("depthtex", "depthtex");
	}
	#end
}
