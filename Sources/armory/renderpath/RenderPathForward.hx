package armory.renderpath;

import iron.RenderPath;

class RenderPathForward {

	#if (rp_renderer == "Forward")

	static var path:RenderPath;

	#if (rp_gi != "Off")
	static var voxels = "voxels";
	static var voxelsLast = "voxels";
	#end

	public static function drawMeshes() {
		path.drawMeshes("mesh");

		#if (rp_background == "World")
		{
			path.drawSkydome("shader_datas/world_pass/world_pass");
		}
		#end

		#if rp_blending
		{
			path.drawMeshes("blend");
		}
		#end

		#if rp_translucency
		{
			var hasLight = iron.Scene.active.lights.length > 0;
			if (hasLight) Inc.drawTranslucency("lbuf");
		}
		#end
	}

	public static function applyConfig() {
		Inc.applyConfig();
	}

	public static function init(_path:RenderPath) {

		path = _path;

		#if (rp_shadowmap && kha_webgl)
		Inc.initEmpty();
		#end
		
		#if (rp_background == "World")
		{
			path.loadShader("shader_datas/world_pass/world_pass");
		}
		#end

		#if rp_render_to_texture
		{
			path.createDepthBuffer("main", "DEPTH24");

			var t = new RenderTargetRaw();
			t.name = "lbuf";
			t.width = 0;
			t.height = 0;
			t.format = Inc.getHdrFormat();
			t.displayp = Inc.getDisplayp();
			t.scale = Inc.getSuperSampling();
			t.depth_buffer = "main";
			path.createRenderTarget(t);

			#if rp_compositornodes
			{
				path.loadShader("shader_datas/compositor_pass/compositor_pass");
			}
			#else
			{
				path.loadShader("shader_datas/copy_pass/copy_pass");
			}
			#end

			// #if rp_rendercapture
			// {
			// 	var t = new RenderTargetRaw();
			// 	t.name = "capture";
			// 	t.width = 0;
			// 	t.height = 0;
			// 	t.format = Inc.getRenderCaptureFormat();
			// 	path.createRenderTarget(t);
			// 	#if rp_compositornodes
			// 	path.loadShader("shader_datas/copy_pass/copy_pass");
			// 	#end
			// }
			// #end

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

		#if (rp_gi != "Off")
		{
			Inc.initGI();
			#if arm_voxelgi_temporal
			{
				Inc.initGI("voxelsB");
			}
			#end
			#if (rp_gi == "Voxel GI")
			{
				Inc.initGI("voxelsOpac");
				Inc.initGI("voxelsNor");
				#if (rp_gi_bounces)
				Inc.initGI("voxelsBounce");
				#end
			}
			#end
		}
		#end

		#if ((rp_antialiasing == "SMAA") || (rp_antialiasing == "TAA"))
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
			path.loadShader("shader_datas/volumetric_light_quad/volumetric_light_quad");
			path.loadShader("shader_datas/volumetric_light/volumetric_light");
			path.loadShader("shader_datas/blur_bilat_pass/blur_bilat_pass_x");
			path.loadShader("shader_datas/blur_bilat_blend_pass/blur_bilat_blend_pass_y");
			{
				var t = new RenderTargetRaw();
				t.name = "bufvola";
				t.width = 0;
				t.height = 0;
				t.displayp = Inc.getDisplayp();
				t.format = "R8";
				t.scale = Inc.getSuperSampling();
				path.createRenderTarget(t);
			}
			{
				var t = new RenderTargetRaw();
				t.name = "bufvolb";
				t.width = 0;
				t.height = 0;
				t.displayp = Inc.getDisplayp();
				t.format = "R8";
				t.scale = Inc.getSuperSampling();
				path.createRenderTarget(t);
			}
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
	}

	public static function commands() {

		var hasLight = iron.Scene.active.lights.length > 0;

		#if rp_shadowmap
		{
			if (hasLight) {
				Inc.drawShadowMap(iron.Scene.active.lights[0]);
			}
		}
		#end

		#if (rp_gi != "Off")
		{
			var voxelize = path.voxelize();

			#if arm_voxelgi_temporal
			voxelize = ++RenderPathCreator.voxelFrame % RenderPathCreator.voxelFreq == 0;

			if (voxelize) {
				voxels = voxels == "voxels" ? "voxelsB" : "voxels";
				voxelsLast = voxels == "voxels" ? "voxelsB" : "voxels";
			}
			#end

			var relight = false;
			if (voxelize) {
				var res = Inc.getVoxelRes();

				#if (rp_gi == "Voxel GI")
				var voxtex = "voxelsOpac";
				#else
				var voxtex = voxels;
				#end

				path.clearImage(voxtex, 0x00000000);
				path.setTarget("");
				path.setViewport(res, res);
				path.bindTarget(voxtex, "voxels");
				path.drawMeshes("voxel");

				relight = true;
			}

			#if ((rp_gi == "Voxel GI") && (rp_voxelgi_relight))
			// Relight if light was moved
			for (light in iron.Scene.active.lights) {
				if (light.transform.diff()) { relight = true; break; }
			}
			#end

			if (relight) {
				#if (rp_gi == "Voxel GI")
					Inc.computeVoxelsBegin();
					Inc.computeVoxels(0);
					Inc.computeVoxelsEnd();
					#if (rp_gi_bounces)
					voxels = "voxelsBounce";
					#end
				#else
				path.generateMipmaps(voxels); // AO
				#end
			}
		}
		#end

		#if rp_render_to_texture
		{
			path.setTarget("lbuf");
		}
		#else
		{
			path.setTarget("");
		}
		#end

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

		#if rp_shadowmap
		{
			if (hasLight) Inc.bindShadowMap();
		}
		#end

		#if (rp_gi != "Off")
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
			#if rp_volumetriclight
			{
				path.setTarget("bufvola");
				path.bindTarget("_main", "gbufferD");
				Inc.bindShadowMap();
				if (path.lightIsSun()) {
					path.drawShader("shader_datas/volumetric_light_quad/volumetric_light_quad");
				}
				else {
					path.drawLightVolume("shader_datas/volumetric_light/volumetric_light");
				}

				path.setTarget("bufvolb");
				path.bindTarget("bufvola", "tex");
				path.drawShader("shader_datas/blur_bilat_pass/blur_bilat_pass_x");

				path.setTarget("lbuf");
				path.bindTarget("bufvolb", "tex");
				path.drawShader("shader_datas/blur_bilat_blend_pass/blur_bilat_blend_pass_y");
			}
			#end
			
			#if rp_bloom
			{
				if (armory.data.Config.raw.rp_ssr != false) {
					path.setTarget("bloomtex");
					path.bindTarget("lbuf", "tex");
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

					path.setTarget("lbuf");
					path.bindTarget("bloomtex2", "tex");
					path.drawShader("shader_datas/blur_gaus_pass/blur_gaus_pass_y_blend");
				}
			}
			#end

			#if ((rp_supersampling == 4) || (rp_rendercapture))
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

			path.bindTarget("lbuf", "tex");

			#if rp_compositordepth
			{
				path.bindTarget("_main", "gbufferD");
			}
			#end

			#if rp_compositornodes
			{
				path.drawShader("shader_datas/compositor_pass/compositor_pass");
			}
			#else
			{
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

				// #if (rp_antialiasing == "TAA")
				// path.setTarget("bufa");
				// #else
				path.setTarget(framebuffer);
				// #end
				path.bindTarget("buf", "colorTex");
				path.bindTarget("bufb", "blendTex");
				// #if (rp_antialiasing == "TAA")
				// {
					// path.bindTarget("gbuffer2", "sveloc");
				// }
				// #end
				path.drawShader("shader_datas/smaa_neighborhood_blend/smaa_neighborhood_blend");

				// #if (rp_antialiasing == "TAA")
				// {
				// 	path.setTarget(framebuffer);
				// 	path.bindTarget("bufa", "tex");
				// 	path.bindTarget("taa", "tex2");
				// 	path.bindTarget("gbuffer2", "sveloc");
				// 	path.drawShader("shader_datas/taa_pass/taa_pass");

				// 	path.setTarget("taa");
				// 	path.bindTarget("bufa", "tex");
				// 	path.drawShader("shader_datas/copy_pass/copy_pass");
				// }
				// #end
			}
			#end

			#if (rp_supersampling == 4)
			{
				// #if rp_rendercapture
				// var finalTarget = "capture";
				// #else
				var finalTarget = "";
				// #end
				path.setTarget(finalTarget);
				path.bindTarget(framebuffer, "tex");
				path.drawShader("shader_datas/supersample_resolve/supersample_resolve");
			}
			// #elseif (rp_rendercapture)
			// {
			// 	path.setTarget("capture");
			// 	path.bindTarget(framebuffer, "tex");
			// 	path.drawShader("shader_datas/copy_pass/copy_pass");
			// }
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
