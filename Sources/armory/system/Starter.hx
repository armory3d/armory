package armory.system;

import kha.WindowOptions;

class Starter {

	static var tasks:Int;
	
	#if arm_loadscreen
	public static var drawLoading:kha.graphics2.Graphics->Int->Int->Void = null;
	public static var numAssets:Int;
	#end

	public static function main(scene:String, mode:Int, resize:Bool, min:Bool, max:Bool, w:Int, h:Int, msaa:Int, vsync:Bool, getRenderPath:Void->iron.RenderPath) {

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
			
			#if (kha_webgl && (!arm_legacy))
			try {
			#end

			kha.System.start({title: Main.projectName, width: c.window_w, height: c.window_h, window: {mode: windowMode, windowFeatures: windowFeatures}, framebuffer: {samplesPerPixel: c.window_msaa, verticalSync: c.window_vsync}}, function(window:kha.Window) {	
				iron.App.init(function() {
					#if arm_loadscreen
					function load(g:kha.graphics2.Graphics) {
	                    if (iron.Scene.active != null && iron.Scene.active.ready) iron.App.removeRender2D(load);
	                    else drawLoading(g, iron.data.Data.assetsLoaded, numAssets);
	                }
	                iron.App.notifyOnRender2D(load);
	                #end
					iron.Scene.setActive(scene, function(object:iron.object.Object) {
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

			#if (kha_webgl && (!arm_legacy))
			}
			catch (e:Dynamic) {
				if (!kha.SystemImpl.gl2) {
					trace("This project was not compiled with legacy shaders flag - please use WebGL 2 capable browser.");
				}
			}
			#end
		}

		#if (js && arm_bullet)
		function loadLibAmmo(name:String) {
			kha.Assets.loadBlobFromPath(name, function(b:kha.Blob) {
				var print = function(s:String) { trace(s); };
				var loaded = function() { tasks--; start(); };
				untyped __js__("(1, eval)({0})", b.toString());
				untyped __js__("Ammo({print:print}).then(loaded)");
			});
		}
		#end

		#if (js && arm_navigation)
		function loadLib(name:String) {
			kha.Assets.loadBlobFromPath(name, function(b:kha.Blob) {
				untyped __js__("(1, eval)({0})", b.toString());
				tasks--;
				start();
			});
		}
		#end

		tasks = 1;
		#if (js && arm_bullet) tasks++; loadLibAmmo("ammo.js"); #end
		#if (js && arm_navigation) tasks++; loadLib("recast.js"); #end
		#if (arm_config) tasks++; armory.data.Config.load(function() { tasks--; start(); }); #end
		tasks--; start();
	}
}
