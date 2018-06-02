package armory.trait.internal;

import iron.math.Math;
import iron.Trait;
#if arm_debug
import kha.Scheduler;
import iron.object.CameraObject;
import iron.object.MeshObject;
import zui.Zui;
import zui.Id;
#end

@:access(zui.Zui)
class DebugConsole extends Trait {

#if (!arm_debug)
	public function new() { super(); }
#else

	var ui:Zui;
	var show = true;

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
			notifyOnRender2D(render2D);
			notifyOnUpdate(update);
			if (haxeTrace == null) {
				haxeTrace = haxe.Log.trace;
				haxe.Log.trace = consoleTrace;
			}
			// Toggle console
			kha.input.Keyboard.get().notify(null, null, function(char: String) {
				if (char == "~") show = !show;
			});
		});
	}

	static var haxeTrace:Dynamic->haxe.PosInfos->Void = null;
	static var lastTrace = '';
	static function consoleTrace(v:Dynamic, ?inf:haxe.PosInfos) {
		lastTrace = Std.string(v);
		haxeTrace(v, inf);
	}

	static var lrow = [1/2, 1/2];
	function render2D(g:kha.graphics2.Graphics) {
		if (!show) return;
		g.end();
		ui.begin(g);
		var hwin = Id.handle();
		if (ui.window(hwin, 0, 0, 280, iron.App.h(), true)) {

			var htab = Id.handle({position: 0});
			if (ui.tab(htab, '')) {}
			if (ui.tab(htab, lastTrace == '' ? 'Inspector' : lastTrace.substr(0, 20))) {
				var i = 0;
				function drawList(h:Handle, o:iron.object.Object) {
					ui.row(lrow);
					var b = false;
					if (o.children.length > 0) {
						b = ui.panel(h.nest(i, {selected: true}), o.name, 0, true);
					}
					else {
						ui._x += 18; // Sign offset
						ui.text(o.name);
						ui._x -= 18;
					}
					ui.text('(' + Math.roundfp(o.transform.worldx()) + ', ' + Math.roundfp(o.transform.worldy()) + ', ' + Math.roundfp(o.transform.worldz()) + ')', Align.Right);
					i++;
					if (b) {
						for (c in o.children) {
							ui.indent();
							drawList(h, c);
							ui.unindent();
						}
					}
				}
				for (c in iron.Scene.active.root.children) {
					drawList(Id.handle(), c);
				}
			}

			var avg = Math.round(frameTimeAvg * 10000) / 10;
			var fpsAvg = avg > 0 ? Math.round(1000 / avg) : 0;
			if (ui.tab(htab, '$avg ms')) {
				// ui.check(Id.handle(), "Show empties");
				ui.text('$fpsAvg fps');
				var numObjects = iron.Scene.active.meshes.length;
				ui.text("meshes: " + numObjects);
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

				ui.text('draw calls: ' + iron.RenderPath.drawCalls);
				ui.text('tris mesh: ' + iron.RenderPath.numTrisMesh);
				ui.text('tris shadow: ' + iron.RenderPath.numTrisShadow);
				#if arm_batch
				ui.text('batch calls: ' + iron.RenderPath.batchCalls);
				ui.text('batch buckets: ' + iron.RenderPath.batchBuckets);
				#end
				ui.text('culled: ' + iron.RenderPath.culled + ' / ' + numObjects * 2); // Assumes shadow context for all meshes
				#if arm_stream
				var total = iron.Scene.active.sceneStream.sceneTotal();
				ui.text('streamed: $numObjects / $total');
				#end
				ui.text('render targets: ');
				for (rt in iron.RenderPath.active.renderTargets) {
					ui.text(rt.raw.name);
				}
			}
			ui.separator();
		}
		ui.end();

		g.begin(false);

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

		// var rp = pathdata.renderTargets.get("shadowMap");
		// g.drawScaledImage(rp.image, 0, 0, 256, 256);
	}

	function update() {
		armory.trait.WalkNavigation.enabled = !(ui.isScrolling || (ui.currentWindow != null && ui.currentWindow.dragging));
		updateTime += iron.App.updateTime;
		animTime += iron.object.Animation.animationTime;
	#if arm_physics
		physTime += armory.trait.physics.PhysicsWorld.physTime;
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
