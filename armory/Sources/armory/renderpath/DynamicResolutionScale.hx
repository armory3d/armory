package armory.renderpath;

import iron.RenderPath;

class DynamicResolutionScale {

	public static var dynamicScale = 1.0;

	static var firstFrame = true;
	static inline var startScaleMs = 30;
	static inline var scaleRangeMs = 10;
	static inline var maxScale = 0.6;

	public static function run(path: RenderPath) {
		if (firstFrame) {
			iron.App.notifyOnRender(render);
			firstFrame = false;
			return;
		}

		// TODO: execute once per frame max
		if (frameTimeAvg > startScaleMs && frameTimeAvg < 100) {
			var overTime = Math.min(scaleRangeMs, frameTimeAvg - startScaleMs);
			var scale = 1.0 - (overTime / scaleRangeMs) * (1.0 - maxScale);
			var w = Std.int(iron.App.w() * scale);
			var h = Std.int(iron.App.h() * scale);
			path.setCurrentViewport(w, h);
			path.setCurrentScissor(w, h);
			dynamicScale = scale;
		}
		else dynamicScale = 1.0;
	}

	static var frameTime: Float;
    static var lastTime: Float = 0;
    static var totalTime: Float = 0;
    static var frames = 0;
    static var frameTimeAvg = 0.0;

	public static function render(g: kha.graphics4.Graphics) {
		frameTime = kha.Scheduler.realTime() - lastTime;
        lastTime = kha.Scheduler.realTime();
        totalTime += frameTime;
        frames++;
        if (totalTime >= 1) {
            frameTimeAvg = Std.int(totalTime / frames * 10000) / 10;
            totalTime = 0;
            frames = 0;
        }
	}
}
