package armory.trait.internal;

import iron.Trait;
#if WITH_PROFILE
import kha.Scheduler;
import iron.resource.RenderPath;
import iron.node.CameraNode;
import zui.Zui;
import zui.Id;
#end

class Console extends Trait {

#if (!WITH_PROFILE)
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

        var font = kha.Assets.fonts.droid_sans;
        ui = new Zui(font, 17, 16, 0, 1.0, 2.0);

        notifyOnAdd(add);
        notifyOnRender2D(render2D);
        notifyOnUpdate(update);
    }

    function add() {
        path = cast(node, CameraNode).renderPath;
    }

    function render2D(g:kha.graphics2.Graphics) {
        g.end();
        ui.begin(g);
        if (ui.window(Id.window(), 0, 0, 185, iron.App.h)) {
            if (ui.node(Id.node(), "Profile (ms)", 0, true)) {
                var avg = Math.round(frameTimeAvg * 10000) / 10;
                var avgMin = Math.round(frameTimeAvgMin * 10000) / 10;
                var avgMax = Math.round(frameTimeAvgMax * 10000) / 10;
                ui.text('frame: $avg ($avgMin/$avgMax)');
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
            if (ui.node(Id.node(), "Render Path", 0, false)) {
                ui.text("draw calls: " + RenderPath.drawCalls);
                ui.text("render targets: " + path.resource.pipeline.resource.render_targets.length);
                for (i in 0...path.passNames.length) {
                    path.passEnabled[i] = ui.check(Id.nest(Id.check(), i), path.passNames[i], path.passEnabled[i]);
                }
            }
            ui.separator();
            if (ui.node(Id.node(), "Inspector", 0, false)) {
                for (o in iron.node.RootNode.models) {
                    ui.text(o.id + " (" + Std.int(o.transform.absx() * 100) / 100 + ", " + Std.int(o.transform.absy() * 100) / 100 + ", " + Std.int(o.transform.absz() * 100) / 100 + ")");
                }
            }
        }
        ui.end();

        g.begin(false);

#if WITH_PROFILE
        totalTime += frameTime;
        renderTime += iron.App.renderTime;
        frames++;
        if (totalTime > 1.0) {
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
#if WITH_PROFILE
        updateTime += iron.App.updateTime;
        physTime += PhysicsWorld.physTime;
#end
    }
#end
}
