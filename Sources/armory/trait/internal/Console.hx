package armory.trait.internal;

import iron.Trait;
#if arm_profile
import kha.Scheduler;
import iron.data.RenderPath;
import iron.object.CameraObject;
import iron.object.MeshObject;
import armui.Armui;
#end

#if arm_profile
@:keep
class ProfilePanel extends Panel {

	var console:Console;

	public function new(console:Console) {
		super();
		this.console = console;
		label = "Profile (ms)";
	}

	public override function draw(layout:Layout) {
		var avg = Math.round(console.frameTimeAvg * 10000) / 10;
		var avgMin = Math.round(console.frameTimeAvgMin * 10000) / 10;
		var avgMax = Math.round(console.frameTimeAvgMax * 10000) / 10;
		layout.label('frame: $avg ($avgMin/$avgMax)');
		var gpuTime = console.frameTimeAvg - console.renderTimeAvg - console.updateTimeAvg;
		if (gpuTime < console.renderTimeAvg) gpuTime = console.renderTimeAvg;
		layout.label("gpu: " + Math.round(gpuTime * 10000) / 10);
		layout.label("render: " + Math.round(console.renderTimeAvg * 10000) / 10);
		layout.label("update: " + Math.round(console.updateTimeAvg * 10000) / 10);
		layout.label("  phys: " + Math.round(console.physTimeAvg * 10000) / 10);
		layout.label("  anim: 0.0");
	}
}

@:keep
class PathPanel extends Panel {

	var console:Console;

	public function new(console:Console) {
		super();
		this.console = console;
		closed = true;
		label = "Render Path";
	}

	public override function draw(layout:Layout) {
		var path = console.path;
		layout.label("draw calls: " + RenderPath.drawCalls);
		layout.label("render targets: " + path.data.pathdata.raw.render_targets.length);
		
		for (i in 0...path.passNames.length) {
			path.passEnabled[i] = layout._bool(path.passNames[i], path.passEnabled[i]);
		}
	}
}

@:keep
class OutlinerPanel extends Panel {

	var console:Console;

	public function new(console:Console) {
		super();
		this.console = console;
		closed = true;
		label = "Outliner";
	}

	public override function draw(layout:Layout) {
		for (o in iron.Scene.active.meshes) {
			o.visible = layout._bool(o.name, o.visible);
		}
		for (o in iron.Scene.active.lamps) {
			o.visible = layout._bool(o.name, o.visible);
		}
		for (o in iron.Scene.active.cameras) {
			o.visible = layout._bool(o.name, o.visible);
		}
		for (o in iron.Scene.active.speakers) {
			o.visible = layout._bool(o.name, o.visible);
		}
	}
}
#end

@:keep
class Console extends Trait {

#if (!arm_profile)
	public function new() { super(); }
#else

	var ui:Armui;
	var area:Area;

	public var path:RenderPath;

	var lastTime = 0.0;
	var frameTime = 0.0;
	var totalTime = 0.0;
	var frames = 0;

	public var frameTimeAvg = 0.0;
	public var frameTimeAvgMin = 0.0;
	public var frameTimeAvgMax = 0.0;
	public var renderTime = 0.0;
	public var renderTimeAvg = 0.0;
	public var updateTime = 0.0;
	public var updateTimeAvg = 0.0;
	public var physTime = 0.0;
	public var physTimeAvg = 0.0;

	public function new() {
		super();

		iron.data.Data.getFont('dejavu.ttf', function(font:kha.Font) {
			ui = new Armui(font);
			area = ui.addArea(0, 0, 160, iron.App.h());
			area.addPanel(new ProfilePanel(this));
			area.addPanel(new PathPanel(this));
			area.addPanel(new OutlinerPanel(this));

			notifyOnInit(init);
			notifyOnRender2D(render2D);
			notifyOnUpdate(update);
		});
	}

	function init() {
		path = cast(object, CameraObject).renderPath;
	}

	function render2D(g:kha.graphics2.Graphics) {
		ui.draw(g);

#if arm_profile
		totalTime += frameTime;
		renderTime += iron.App.renderTime;
		frames++;
		if (totalTime > 1.0) {
			area.tagRedraw();
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
