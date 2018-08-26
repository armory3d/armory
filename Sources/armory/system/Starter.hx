package armory.system;

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
			var config = armory.data.Config.raw;
			if (config.window_mode == null) config.window_mode = mode;
			if (config.window_resizable == null) config.window_resizable = resize;
			if (config.window_minimizable == null) config.window_minimizable = min;
			if (config.window_maximizable == null) config.window_maximizable = max;
			if (config.window_w == null) config.window_w = w;
			if (config.window_h == null) config.window_h = h;
			if (config.window_msaa == null) config.window_msaa = msaa;
			if (config.window_vsync == null) config.window_vsync = vsync;
			
			armory.object.Uniforms.register();
			
			var windowMode = config.window_mode == 0 ? kha.WindowMode.Window : kha.WindowMode.Fullscreen;
			#if (kha_version < 1807) // TODO: deprecated
			if (windowMode == kha.WindowMode.Fullscreen) { windowMode = kha.WindowMode.BorderlessWindow; config.window_w = kha.Display.width(0); config.window_h = kha.Display.height(0); }
			kha.System.init({title: Main.projectName, width: config.window_w, height: config.window_h, samplesPerPixel: config.window_msaa, vSync: config.window_vsync, windowMode: windowMode, resizable: config.window_resizable, maximizable: config.window_maximizable, minimizable: config.window_minimizable}, function() {
			#else
			var windowFeatures = 0;
			if (config.window_resizable) windowFeatures |= kha.WindowOptions.FeatureResizable;
			if (config.window_maximizable) windowFeatures |= kha.WindowOptions.FeatureMaximizable;
			if (config.window_minimizable) windowFeatures |= kha.WindowOptions.FeatureMinimizable;
			kha.System.start({title: Main.projectName, width: config.window_w, height: config.window_h, window: {mode: windowMode, windowFeatures: windowFeatures}, framebuffer: {samplesPerPixel: config.window_msaa, verticalSync: config.window_vsync}}, function(window:kha.Window) {
			#end
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
					});
				});
			});
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
