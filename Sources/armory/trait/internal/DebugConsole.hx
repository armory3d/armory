package armory.trait.internal;

import iron.Trait;
#if arm_profile
import kha.Scheduler;
import iron.data.RenderPath;
import iron.object.CameraObject;
import iron.object.MeshObject;
import zui.Zui;
import zui.Id;
#end

class DebugConsole extends Trait {

#if (!arm_profile)
	public function new() { super(); }
#else

	var ui:Zui;
	var path:RenderPath;

	var lastTime = 0.0;
	var frameTime = 0.0;
	var totalTime = 0.0;
	var frames = 0;

	var frameTimeAvg = 0.0;
	var frameTimeAvgMin = 0.0;
	var frameTimeAvgMax = 0.0;
	var renderPathTime = 0.0;
	var renderPathTimeAvg = 0.0;
	var updateTime = 0.0;
	var updateTimeAvg = 0.0;
	var animTime = 0.0;
	var animTimeAvg = 0.0;
	var physTime = 0.0;
	var physTimeAvg = 0.0;

	public function new() {
		super();

		iron.data.Data.getFont('droid_sans.ttf', function(font:kha.Font) {
			var theme = Reflect.copy(zui.Themes.dark);
			theme.WINDOW_BG_COL = 0xee111111;
			ui = new Zui({font: font, theme: theme});
			notifyOnInit(init);
			notifyOnRender2D(render2D);
			notifyOnUpdate(update);
			haxeTrace = haxe.Log.trace;
			haxe.Log.trace = consoleTrace;
		});
	}

	static var haxeTrace:Dynamic->haxe.PosInfos->Void;
	static var lastTrace = '';
	static function consoleTrace(v:Dynamic, ?inf:haxe.PosInfos) {
		lastTrace = Std.string(v);
		haxeTrace(v, inf);
    }

	function init() {
		path = cast(object, CameraObject).renderPath;
	}

	function render2D(g:kha.graphics2.Graphics) {
		g.end();
		ui.begin(g);
		var hwin = Id.handle();
		if (ui.window(hwin, 0, 0, 250, iron.App.h(), true)) {
			ui.text('Console ' + lastTrace);
			var avg = Math.round(frameTimeAvg * 10000) / 10;
			var fpsAvg = avg > 0 ? Math.round(1000 / avg) : 0;
			if (ui.panel(Id.handle(), 'Profile ($avg ms / $fpsAvg fps)')) {
				var avgMin = Math.round(frameTimeAvgMin * 10000) / 10;
				var avgMax = Math.round(frameTimeAvgMax * 10000) / 10;
				ui.text('frame (min/max): $avgMin/$avgMax');
				var fpsAvgMin = avgMin > 0 ? Math.round(1000 / avgMin) : 0;
				var fpsAvgMax = avgMax > 0 ? Math.round(1000 / avgMax) : 0;
				ui.text('fps (min/max): $fpsAvgMin/$fpsAvgMax');
				ui.text('rpath: ' + Math.round(renderPathTimeAvg * 10000) / 10);
				ui.text('update: ' + Math.round(updateTimeAvg * 10000) / 10);
				ui.indent();
				ui.text('- phys: ' + Math.round(physTimeAvg * 10000) / 10);
				ui.text('- anim: ' + Math.round(animTimeAvg * 10000) / 10);
				// ui.text('mem: ' + Std.int(getMem() / 1024 / 1024));
				ui.unindent();
			}
			ui.separator();

			var dcalls = RenderPath.drawCalls;
			var numObjects = iron.Scene.active.meshes.length;
			if (ui.panel(Id.handle(), 'Render Path ($dcalls draw calls)')) {
				ui.text('tris mesh: ' + RenderPath.numTrisMesh);
				ui.text('tris shadow: ' + RenderPath.numTrisShadow);
				#if arm_batch
				ui.text('batch calls: ' + RenderPath.batchCalls);
				ui.text('batch buckets: ' + RenderPath.batchBuckets);
				#end
				ui.text('culled: ' + RenderPath.culled + ' / ' + numObjects * 2); // Assumes shadow context for all meshes
				#if arm_stream
				var total = iron.Scene.active.sceneStream.sceneTotal();
				ui.text('streamed: $numObjects / $total');
				#end
				var rts = path.data.pathdata.raw.render_targets;
				ui.text('render targets: ' + (rts != null ? rts.length : 0));
			}
			ui.separator();

			if (ui.panel(Id.handle(), 'Inspector ($numObjects meshes)')) {	
				ui.text('name (pos) - screen size');
				function drawList(h:Handle, objs:Array<iron.object.Object>) {
					for (i in 0...objs.length) {
						var o = objs[i];
						var text = o.name + ' (' + Std.int(o.transform.worldx() * 100) / 100 + ', ' + Std.int(o.transform.worldy() * 100) / 100 + ', ' + Std.int(o.transform.worldz() * 100) / 100 + ')';
						if (Std.is(o, MeshObject)) text += ' - ' + Std.int(cast(o, MeshObject).screenSize * 100) / 100;
						o.visible = ui.check(h.nest(i, {selected: o.visible}), text);
					}
				}
				drawList(Id.handle(), cast iron.Scene.active.meshes);
				drawList(Id.handle(), cast iron.Scene.active.lamps);
				drawList(Id.handle(), cast iron.Scene.active.cameras);
				drawList(Id.handle(), cast iron.Scene.active.speakers);
			}
		}
		ui.end();

		g.begin(false);

#if arm_profile
		totalTime += frameTime;
		renderPathTime += iron.App.renderPathTime;
		frames++;
		if (totalTime > 1.0) {
			hwin.redraws = 1;
			var t = totalTime / frames;
			// Second frame
			if (frameTimeAvg > 0) {
				if (t < frameTimeAvgMin || frameTimeAvgMin == 0) frameTimeAvgMin = t;
				if (t > frameTimeAvgMax || frameTimeAvgMax == 0) frameTimeAvgMax = t;
			}

			frameTimeAvg = t;
			renderPathTimeAvg = renderPathTime / frames;
			updateTimeAvg = updateTime / frames;
			animTimeAvg = animTime / frames;
			physTimeAvg = physTime / frames;
			
			totalTime = 0;
			renderPathTime = 0;
			updateTime = 0;
			animTime = 0;
			physTime = 0;
			frames = 0;
		}
		frameTime = Scheduler.realTime() - lastTime;
		lastTime = Scheduler.realTime();
#end
	}

	function update() {
#if arm_profile
		updateTime += iron.App.updateTime;
		animTime += iron.object.Animation.animTime;
	#if arm_physics
		physTime += PhysicsWorld.physTime;
	#end
#end
	}

	// function getMem():Int {
	// 	#if cpp
	// 	return untyped __global__.__hxcpp_gc_used_bytes();
	// 	#elseif kha_webgl
	// 	return untyped __js__("(window.performance && window.performance.memory) ? window.performance.memory.usedJSHeapSize : 0");
	// 	#else
	// 	return 0;
	// 	#end
	// }

	// function rungc() {
	// 	#if cpp
	// 	return cpp.vm.Gc.run(true);	
	// 	#end
	// }

#end
}
