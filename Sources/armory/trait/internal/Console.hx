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

@:keep
class Console extends Trait {

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
	var renderTime = 0.0;
	var renderTimeAvg = 0.0;
	var updateTime = 0.0;
	var updateTimeAvg = 0.0;
	var physTime = 0.0;
	var physTimeAvg = 0.0;

	public function new() {
		super();

		iron.data.Data.getFont('droid_sans.ttf', function(font:kha.Font) {
			ui = new Zui({font: font});
			notifyOnInit(init);
			notifyOnRender2D(render2D);
			notifyOnUpdate(update);
		});
	}

	function init() {
		path = cast(object, CameraObject).renderPath;
	}

	function render2D(g:kha.graphics2.Graphics) {
		g.end();
		ui.begin(g);
		var hwin = Id.handle();
		if (ui.window(hwin, 0, 0, 250, iron.App.h(), true)) {
			if (ui.panel(Id.handle({selected: true}), "Profile (ms)")) {
				var avg = Math.round(frameTimeAvg * 10000) / 10;
				var avgMin = Math.round(frameTimeAvgMin * 10000) / 10;
				var avgMax = Math.round(frameTimeAvgMax * 10000) / 10;
				ui.text('frame: $avg ($avgMin/$avgMax)');
				var fpsAvg = avg > 0 ? Math.round(1000 / avg) : 0;
				var fpsAvgMin = avgMin > 0 ? Math.round(1000 / avgMin) : 0;
				var fpsAvgMax = avgMax > 0 ? Math.round(1000 / avgMax) : 0;
				ui.text('fps: $fpsAvg ($fpsAvgMin/$fpsAvgMax)');
				var gpuTime = frameTimeAvg - renderTimeAvg - updateTimeAvg;
				if (gpuTime < renderTimeAvg) gpuTime = renderTimeAvg;
				ui.text("gpu: " + Math.round(gpuTime * 10000) / 10);
				ui.text("render: " + Math.round(renderTimeAvg * 10000) / 10);
				ui.text("update: " + Math.round(updateTimeAvg * 10000) / 10);
				ui.indent();
				ui.text("phys: " + Math.round(physTimeAvg * 10000) / 10);
				ui.text("anim: 0.0");
				ui.unindent();
			}
			ui.separator();

			if (ui.panel(Id.handle(), "Render Path")) {
				ui.text("draw calls: " + RenderPath.drawCalls);
				ui.text("batch calls: " + RenderPath.batchCalls);
				ui.text("batch buckets: " + RenderPath.batchBuckets);
				ui.text("render targets: " + path.data.pathdata.raw.render_targets.length);
			}
			ui.separator();

			if (ui.panel(Id.handle(), "Inspector")) {	
				function drawList(h:Handle, objs:Array<iron.object.Object>) {
					for (i in 0...objs.length) {
						var o = objs[i];
						var text = o.name + " (" + Std.int(o.transform.absx() * 100) / 100 + ", " + Std.int(o.transform.absy() * 100) / 100 + ", " + Std.int(o.transform.absz() * 100) / 100 + ")";
						if (Std.is(o, MeshObject)) text += " - " + Std.int(cast(o, MeshObject).screenSize * 100) / 100;
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
		renderTime += iron.App.renderTime;
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
			renderTimeAvg = renderTime / frames;
			updateTimeAvg = updateTime / frames;
			physTimeAvg = physTime / frames;
			
			totalTime = 0;
			renderTime = 0;
			updateTime = 0;
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
	#if arm_physics
		physTime += PhysicsWorld.physTime;
	#end
#end
	}
#end
}
