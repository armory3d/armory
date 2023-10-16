package armory.renderpath;

import iron.RenderPath;
import iron.Scene;

class RenderPathForward {

	#if (rp_renderer == "Forward")

	static var path: RenderPath;

	#if (rp_voxels != "Off")
	static var voxels = "voxels";
	static var voxelsLast = "voxels";
	static var voxelsBounce = "voxelsBounce";
	static var voxelsBounceLast = "voxelsBounce";
	#end

	#if rp_bloom
	static var bloomDownsampler: Downsampler;
	static var bloomUpsampler: Upsampler;
	#end

	public static function setTargetMeshes() {
		#if rp_render_to_texture
		{
			path.setTarget("lbuffer0", [
			#if rp_ssr "lbuffer1", #end
			#if (rp_voxels != "Off") "gbuffer_voxpos", #end
			]);
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

		#if rp_translucency
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

		#if rp_render_to_texture
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
				t.format = "RGBA64";
				t.displayp = Inc.getDisplayp();
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

		#if (rp_translucency)
		{
			Inc.initTranslucency();
		}
		#end

		#if (rp_voxels != 'Off')
		{
			Inc.initGI();

			var t = new RenderTargetRaw();
			t.name = "gbuffer_voxpos";
			t.width = 0;
			t.height = 0;
			t.displayp = Inc.getDisplayp();
			t.format = "RGBA64";
			t.scale = Inc.getSuperSampling();
			path.createRenderTarget(t);
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

		#if (rp_ssr_half || rp_ssgi_half)
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

			path.clearImage(voxels, 0x00000000);

			#if arm_voxelgi_temporal
			if(++armory.renderpath.RenderPathCreator.voxelFrame % armory.renderpath.RenderPathCreator.voxelFreq == 0) {
				voxels = voxels == "voxels" ? "voxelsB" : "voxels";
				voxelsLast = voxels == "voxels" ? "voxelsB" : "voxels";
			}
			#end

			path.setTarget("", ["gbuffer_voxpos"]);
			path.bindTarget(voxels, "voxels");

			var res = Inc.getVoxelRes();
			path.setViewport(res, res);

			#if (rp_voxels == "Voxel GI")
			#if rp_shadowmap
			{
				#if arm_shadowmap_atlas
				Inc.bindShadowMapAtlas();
				#else
				Inc.bindShadowMap();
				#end
			}
			#end
			#end

			path.drawMeshes("voxel");
			path.generateMipmaps(voxels);

			#if (arm_voxelgi_bounces != 1)
			path.clearImage(voxelsBounce, 0x00000000);

			path.setTarget("");
			var res = Inc.getVoxelRes();
			path.setViewport(res, res);

			path.bindTarget(voxels, "voxels");
			path.bindTarget(voxelsBounce, "voxelsBounce");
			#if rp_voxelgi_refract
			path.bindTarget("gbuffer_refraction", "gbuffer_refraction");
			#end
			path.bindTarget("gbuffer0", "gbuffer0");
			path.bindTarget("gbuffer1", "gbuffer1");
			path.bindTarget("_main", "gbufferD");
			path.drawMeshes("voxelbounce");
			path.generateMipmaps(voxelsBounce);
			#else
			path.generateMipmaps(voxels);
			#end
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
			RenderPathCreator.setTargetMeshes();
		}
		#end

		#if rp_shadowmap
		{
			#if arm_shadowmap_atlas
			Inc.bindShadowMapAtlas();
			#else
			Inc.bindShadowMap();
			#end
		}
		#end


		#if (rp_voxels != 'Off')
		if (armory.data.Config.raw.rp_gi != false)
		{
			#if (arm_voxelgi_bounces != 1)
			path.bindTarget(voxelsBounce, "voxels");
			#else
			path.bindTarget(voxels, "voxels");
			#end

			#if arm_voxelgi_temporal
			{
				#if (arm_voxelgi_bounces != 1)
				path.bindTarget(voxelsBounceLast, "voxelsLast");
				#else
				path.bindTarget(voxelsLast, "voxelsLast");
				#end
			}
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

		#if rp_render_to_texture
		{
			#if (rp_ssr_half || rp_ssgi_half)
			path.setTarget("half");
			path.bindTarget("_main", "texdepth");
			path.drawShader("shader_datas/downsample_depth/downsample_depth");
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
