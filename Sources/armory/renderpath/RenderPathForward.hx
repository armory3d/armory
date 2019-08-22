package armory.renderpath;

import iron.RenderPath;

class RenderPathForward {

	#if (rp_renderer == "Forward")

	static var path:RenderPath;

	#if rp_voxelao
	static var voxels = "voxels";
	static var voxelsLast = "voxels";
	#end

	public static function setTargetMeshes() {
		#if rp_render_to_texture
		{
			#if rp_ssr
			path.setTarget("lbuffer0", ["lbuffer1"]);
			#else
			path.setTarget("lbuffer0");
			#end
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
			RenderPathCreator.setTargetMeshes();
			path.drawSkydome("shader_datas/world_pass/world_pass");
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

	public static function init(_path:RenderPath) {

		path = _path;
		
		#if (rp_background == "World")
		{
			path.loadShader("shader_datas/world_pass/world_pass");
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

			#if ((rp_supersampling == 4) || (rp_antialiasing == "SMAA") || (rp_antialiasing == "TAA"))
			{
				var t = new RenderTargetRaw();
				t.name = "buf";
				t.width = 0;
				t.height = 0;
				t.format = 'RGBA32';
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

		#if rp_voxelao
		{
			Inc.initGI();
		}
		#end

		#if ((rp_antialiasing == "SMAA") || (rp_antialiasing == "TAA") || (rp_ssr && !rp_ssr_half) || (rp_water))
		{
			var t = new RenderTargetRaw();
			t.name = "bufa";
			t.width = 0;
			t.height = 0;
			t.displayp = Inc.getDisplayp();
			t.format = "RGBA32";
			t.scale = Inc.getSuperSampling();
			path.createRenderTarget(t);
		}
		{
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
			{
				var t = new RenderTargetRaw();
				t.name = "singlea";
				t.width = 0;
				t.height = 0;
				t.displayp = Inc.getDisplayp();
				t.format = "R8";
				t.scale = Inc.getSuperSampling();
				path.createRenderTarget(t);
			}
			{
				var t = new RenderTargetRaw();
				t.name = "singleb";
				t.width = 0;
				t.height = 0;
				t.displayp = Inc.getDisplayp();
				t.format = "R8";
				t.scale = Inc.getSuperSampling();
				path.createRenderTarget(t);
			}
		}
		#end

		#if rp_water
		{
			path.loadShader("shader_datas/water_pass/water_pass");
			path.loadShader("shader_datas/copy_pass/copy_pass");
		}
		#end

		#if rp_bloom
		{
			var t = new RenderTargetRaw();
			t.name = "bloomtex";
			t.width = 0;
			t.height = 0;
			t.scale = 0.25;
			t.format = Inc.getHdrFormat();
			path.createRenderTarget(t);
		}

		{
			var t = new RenderTargetRaw();
			t.name = "bloomtex2";
			t.width = 0;
			t.height = 0;
			t.scale = 0.25;
			t.format = Inc.getHdrFormat();
			path.createRenderTarget(t);
		}

		{
			path.loadShader("shader_datas/bloom_pass/bloom_pass");
			path.loadShader("shader_datas/blur_gaus_pass/blur_gaus_pass_x");
			path.loadShader("shader_datas/blur_gaus_pass/blur_gaus_pass_y");
			path.loadShader("shader_datas/blur_gaus_pass/blur_gaus_pass_y_blend");
		}
		#end

		#if (rp_ssr_half || rp_ssgi_half)
		{
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
			}
			{
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
	}

	public static function commands() {

		#if rp_shadowmap
		{
			Inc.drawShadowMap();
		}
		#end

		#if rp_voxelao
		{
			var voxelize = path.voxelize();

			#if arm_voxelgi_temporal
			voxelize = ++RenderPathCreator.voxelFrame % RenderPathCreator.voxelFreq == 0;

			if (voxelize) {
				voxels = voxels == "voxels" ? "voxelsB" : "voxels";
				voxelsLast = voxels == "voxels" ? "voxelsB" : "voxels";
			}
			#end

			if (voxelize) {
				var res = Inc.getVoxelRes();
				var voxtex = voxels;

				path.clearImage(voxtex, 0x00000000);
				path.setTarget("");
				path.setViewport(res, res);
				path.bindTarget(voxtex, "voxels");
				path.drawMeshes("voxel");
				path.generateMipmaps(voxels);
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
			RenderPathCreator.setTargetMeshes();
		}
		#end

		#if rp_shadowmap
		{
			Inc.bindShadowMap();
		}
		#end

		#if rp_voxelao
		{
			path.bindTarget(voxels, "voxels");
			#if arm_voxelgi_temporal
			{
				path.bindTarget(voxelsLast, "voxelsLast");
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
				if (armory.data.Config.raw.rp_bloom != false) {
					path.setTarget("bloomtex");
					path.bindTarget("lbuffer0", "tex");
					path.drawShader("shader_datas/bloom_pass/bloom_pass");

					path.setTarget("bloomtex2");
					path.bindTarget("bloomtex", "tex");
					path.drawShader("shader_datas/blur_gaus_pass/blur_gaus_pass_x");

					path.setTarget("bloomtex");
					path.bindTarget("bloomtex2", "tex");
					path.drawShader("shader_datas/blur_gaus_pass/blur_gaus_pass_y");

					path.setTarget("bloomtex2");
					path.bindTarget("bloomtex", "tex");
					path.drawShader("shader_datas/blur_gaus_pass/blur_gaus_pass_x");

					path.setTarget("bloomtex");
					path.bindTarget("bloomtex2", "tex");
					path.drawShader("shader_datas/blur_gaus_pass/blur_gaus_pass_y");

					path.setTarget("bloomtex2");
					path.bindTarget("bloomtex", "tex");
					path.drawShader("shader_datas/blur_gaus_pass/blur_gaus_pass_x");

					path.setTarget("bloomtex");
					path.bindTarget("bloomtex2", "tex");
					path.drawShader("shader_datas/blur_gaus_pass/blur_gaus_pass_y");

					path.setTarget("bloomtex2");
					path.bindTarget("bloomtex", "tex");
					path.drawShader("shader_datas/blur_gaus_pass/blur_gaus_pass_x");

					path.setTarget("lbuffer0");
					path.bindTarget("bloomtex2", "tex");
					path.drawShader("shader_datas/blur_gaus_pass/blur_gaus_pass_y_blend");
				}
			}
			#end

			#if rp_volumetriclight
			{
				path.setTarget("singlea");
				path.bindTarget("_main", "gbufferD");
				Inc.bindShadowMap();
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
	#end
}
