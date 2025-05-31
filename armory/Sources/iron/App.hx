package iron;

class App {

	public static dynamic function w(): Int { return kha.System.windowWidth(); }
	public static dynamic function h(): Int { return kha.System.windowHeight(); }
	public static dynamic function x(): Int { return 0; }
	public static dynamic function y(): Int { return 0; }

	static var onResets: Array<Void->Void> = null;
	static var onEndFrames: Array<Void->Void> = null;
	static var traitInits: Array<Void->Void> = [];
	static var traitUpdates: Array<Void->Void> = [];
	static var traitLateUpdates: Array<Void->Void> = [];
	static var traitFixedUpdates: Array<Void->Void> = [];
	static var traitRenders: Array<kha.graphics4.Graphics->Void> = [];
	static var traitRenders2D: Array<kha.graphics2.Graphics->Void> = [];
	public static var framebuffer: kha.Framebuffer;
	public static var pauseUpdates = false;

	#if arm_debug
	static var startTime: Float;
	public static var updateTime: Float;
	public static var renderPathTime: Float;
	public static var endFrameCallbacks: Array<Void->Void> = [];
	#end
	static var last = 0.0;
	static var time = 0.0;
	static var lastw = -1;
	static var lasth = -1;
	public static var onResize: Void->Void = null;

	public static function init(done: Void->Void) {
		new App(done);
	}

	function new(done: Void->Void) {
		done();
		kha.System.notifyOnFrames(render);
		kha.Scheduler.addTimeTask(update, 0, iron.system.Time.step);
	}

	public static function reset() {
		traitInits = [];
		traitUpdates = [];
		traitLateUpdates = [];
		traitFixedUpdates = [];
		traitRenders = [];
		traitRenders2D = [];
		if (onResets != null) for (f in onResets) f();
	}

	static function update() {
		if (Scene.active == null || !Scene.active.ready) return;
		if (pauseUpdates) return;

		iron.system.Time.update();

		#if arm_debug
		startTime = kha.Scheduler.realTime();
		#end

		Scene.active.updateFrame();

		time += iron.system.Time.delta;

		while (time >= iron.system.Time.fixedStep) {
			for (f in traitFixedUpdates) f();
			time -= iron.system.Time.fixedStep;
		}

		var i = 0;
		var l = traitUpdates.length;
		while (i < l) {
			if (traitInits.length > 0) {
				for (f in traitInits) {
					traitInits.length > 0 ? f() : break;
				}
				traitInits.splice(0, traitInits.length);
			}
			traitUpdates[i]();
			// Account for removed traits
			l <= traitUpdates.length ? i++ : l = traitUpdates.length;
		}

		i = 0;
		l = traitLateUpdates.length;
		while (i < l) {
			traitLateUpdates[i]();
			l <= traitLateUpdates.length ? i++ : l = traitLateUpdates.length;
		}

		if (onEndFrames != null) for (f in onEndFrames) f();

		#if arm_debug
		iron.object.Animation.endFrame();
		for (cb in endFrameCallbacks) cb();
		updateTime = kha.Scheduler.realTime() - startTime;
		#end

		// Rebuild projection on window resize
		if (lastw == -1) {
			lastw = App.w();
			lasth = App.h();
		}
		if (lastw != App.w() || lasth != App.h()) {
			if (onResize != null) onResize();
			else {
				if (Scene.active != null && Scene.active.camera != null) {
					Scene.active.camera.buildProjection();
				}
			}
		}
		lastw = App.w();
		lasth = App.h();
	}

	static function render(frames: Array<kha.Framebuffer>) {
		var frame = frames[0];
		framebuffer = frame;

		iron.system.Time.render();

		if (Scene.active == null || !Scene.active.ready) {
			render2D(frame);
			return;
		}

		#if arm_debug
		startTime = kha.Scheduler.realTime();
		#end

		if (traitInits.length > 0) {
			for (f in traitInits) {
				traitInits.length > 0 ? f() : break;
			}
			traitInits.splice(0, traitInits.length);
		}

		Scene.active.renderFrame(frame.g4);

		for (f in traitRenders) {
			traitRenders.length > 0 ? f(frame.g4) : break;
		}

		render2D(frame);

		#if arm_debug
		renderPathTime = kha.Scheduler.realTime() - startTime;
		#end
	}

	static function render2D(frame: kha.Framebuffer) {
		if (traitRenders2D.length > 0) {
			frame.g2.begin(false);
			for (f in traitRenders2D) {
				traitRenders2D.length > 0 ? f(frame.g2) : break;
			}
			frame.g2.end();
		}
	}

	// Hooks
	public static function notifyOnInit(f: Void->Void) {
		traitInits.push(f);
	}

	public static function removeInit(f: Void->Void) {
		traitInits.remove(f);
	}

	public static function notifyOnUpdate(f: Void->Void) {
		traitUpdates.push(f);
	}

	public static function removeUpdate(f: Void->Void) {
		traitUpdates.remove(f);
	}

	public static function notifyOnLateUpdate(f: Void->Void) {
		traitLateUpdates.push(f);
	}

	public static function removeLateUpdate(f: Void->Void) {
		traitLateUpdates.remove(f);
	}

	public static function notifyOnFixedUpdate(f: Void->Void) {
		traitFixedUpdates.push(f);
	}

	public static function removeFixedUpdate(f: Void->Void) {
		traitFixedUpdates.remove(f);
	}

	public static function notifyOnRender(f: kha.graphics4.Graphics->Void) {
		traitRenders.push(f);
	}

	public static function removeRender(f: kha.graphics4.Graphics->Void) {
		traitRenders.remove(f);
	}

	public static function notifyOnRender2D(f: kha.graphics2.Graphics->Void) {
		traitRenders2D.push(f);
	}

	public static function removeRender2D(f: kha.graphics2.Graphics->Void) {
		traitRenders2D.remove(f);
	}

	public static function notifyOnReset(f: Void->Void) {
		if (onResets == null) onResets = [];
		onResets.push(f);
	}

	public static function removeReset(f: Void->Void) {
		onResets.remove(f);
	}

	public static function notifyOnEndFrame(f: Void->Void) {
		if (onEndFrames == null) onEndFrames = [];
		onEndFrames.push(f);
	}

	public static function removeEndFrame(f: Void->Void) {
		onEndFrames.remove(f);
	}
}
