package armory.trait.internal;

import iron.Trait;
#if WITH_PROFILE
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

    public function new() {
        super();

        var font = kha.Assets.fonts.droid_sans;
        ui = new Zui(font, 17, 16, 0, 1.0);

        notifyOnAdd(add);
        notifyOnRender2D(render2D);
    }

    function add() {
        path = cast(node, CameraNode).renderPath;
    }

    function render2D(g:kha.graphics2.Graphics) {
        g.end();

        ui.begin(g);
        if (ui.window(Id.window(), 0, 0, 200, 200)) {
        // ui.window(Id.window(), 0, 0, 200, 200);
            ui.text("frame ms: " + Math.round(RenderPath.frameTimeAvg * 10000) / 10);
            ui.text("phys ms: " + Math.round(PhysicsWorld.physTimeAvg * 10000) / 10);
            // ui.text("game ms: " + Math.round(App.updateTimeAvg * 10000) / 10);
            // ui.text("anim ms: " + Math.round(Animation.animTimeAvg * 10000) / 10);
            ui.text("draw calls: " + RenderPath.drawCalls);
            // ui.text("delta: " + RenderPath.frameDeltaAvg);
        }
        ui.end();

        g.begin(false);
    }
#end
}
