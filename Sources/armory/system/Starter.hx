package armory.system;

import kha.WindowOptions;

class Starter {

	#if arm_loadscreen
	public static var drawLoading: kha.graphics2.Graphics->Int->Int->Void = null;
	public static var numAssets: Int;
	#end

	public static function main(scene: String, mode: Int, resize: Bool, min: Bool, max: Bool, w: Int, h: Int, msaa: Int, vsync: Bool, getRenderPath: Void->iron.RenderPath) {

		var tasks = 0;

		function start() {
			if (tasks > 0) return;

			if (armory.data.Config.raw == null) armory.data.Config.raw = {};
			var c = armory.data.Config.raw;

			if (c.window_mode == null) c.window_mode = mode;
			if (c.window_resizable == null) c.window_resizable = resize;
			if (c.window_minimizable == null) c.window_minimizable = min;
			if (c.window_maximizable == null) c.window_maximizable = max;
			if (c.window_w == null) c.window_w = w;
			if (c.window_h == null) c.window_h = h;
			if (c.window_scale == null) c.window_scale = 1.0;
			if (c.window_msaa == null) c.window_msaa = msaa;
			if (c.window_vsync == null) c.window_vsync = vsync;

			armory.object.Uniforms.register();

			var windowMode = c.window_mode == 0 ? kha.WindowMode.Windowed : kha.WindowMode.Fullscreen;
			var windowFeatures = None;
			if (c.window_resizable) windowFeatures |= FeatureResizable;
			if (c.window_maximizable) windowFeatures |= FeatureMaximizable;
			if (c.window_minimizable) windowFeatures |= FeatureMinimizable;

			#if (kha_webgl && (!arm_legacy) && (!kha_node))
			try {
			#end

			kha.System.start({title: Main.projectName, width: c.window_w, height: c.window_h, window: {mode: windowMode, windowFeatures: windowFeatures}, framebuffer: {samplesPerPixel: c.window_msaa, verticalSync: c.window_vsync}}, function(window: kha.Window) {

				iron.App.init(function() {
					#if arm_loadscreen
					function load(g: kha.graphics2.Graphics) {
						if (iron.Scene.active != null && iron.Scene.active.ready) iron.App.removeRender2D(load);
						else drawLoading(g, iron.data.Data.assetsLoaded, numAssets);
					}
					iron.App.notifyOnRender2D(load);
					#end
					iron.Scene.setActive(scene, function(object: iron.object.Object) {
						iron.RenderPath.setActive(getRenderPath());
						#if arm_patch
						iron.Scene.getRenderPath = getRenderPath;
						#end
						#if arm_draworder_shader
						iron.RenderPath.active.drawOrder = iron.RenderPath.DrawOrder.Shader;
						#end // else Distance
					});
				});
			});

			#if (kha_webgl && (!arm_legacy) && (!kha_node))
			}
			catch (e: Dynamic) {
				if (!kha.SystemImpl.gl2) {
					trace("This project was not compiled with legacy shaders flag - please use WebGL 2 capable browser.");
				}
			}
			#end
		}

		#if (js && arm_bullet)
		function loadLibAmmo(name: String) {
			kha.Assets.loadBlobFromPath(name, function(b: kha.Blob) {
				js.Syntax.code("(1,eval)({0})", b.toString());
				#if kha_krom
				js.Syntax.code("Ammo({print:function(s){iron.log(s);},instantiateWasm:function(imports,successCallback) {
					var wasmbin = Krom.loadBlob('ammo.wasm.wasm');
					var module = new WebAssembly.Module(wasmbin);
					var inst = new WebAssembly.Instance(module,imports);
					successCallback(inst);
					return inst.exports;
				}}).then(function(){ tasks--; start();})");
				#else
				js.Syntax.code("Ammo({print:function(s){iron.log(s);}}).then(function(){ tasks--; start();})");
				#end
			});
		}
		#end

		#if (js && arm_navigation)
		function loadLib(name: String) {
			kha.Assets.loadBlobFromPath(name, function(b: kha.Blob) {
				js.Syntax.code("(1, eval)({0})", b.toString());
				#if kha_krom
				js.Syntax.code("Recast({print:function(s){iron.log(s);},instantiateWasm:function(imports,successCallback) {
					var wasmbin = Krom.loadBlob('recast.wasm.wasm');
					var module = new WebAssembly.Module(wasmbin);
					var inst = new WebAssembly.Instance(module,imports);
					successCallback(inst);
					return inst.exports;
				}}).then(function(){ tasks--; start();})");
				#else
				js.Syntax.code("Recast({print:function(s){iron.log(s);}}).then(function(){ tasks--; start();})");
				#end
			});
		}
		#end

		tasks = 1;

		#if (js && arm_bullet)
		tasks++;
		#if kha_krom
		loadLibAmmo("ammo.wasm.js");
		#else
		loadLibAmmo("ammo.js");
		#end
		#end

		#if (js && arm_navigation)
		tasks++;
		#if kha_krom
		loadLib("recast.wasm.js");
		#else
		loadLib("recast.js");
		#end
		#end

		#if (arm_config)
		tasks++;
		armory.data.Config.load(function() { tasks--; start(); });
		#end

		tasks--; start();
	}
}
