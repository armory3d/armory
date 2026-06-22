package armory.system;

import iron.App;
import iron.system.Time;
import iron.math.Vec4;

class Tween {
	public var paused: Bool = true;
	public var elapsed: Float = 0.0;
	public var duration: Float = 1.0;
	public var ease: Ease = Linear;

	var fromFloat: Float = 0.0;
	var toFloat: Float = 0.0;
	var fromVec: Vec4 = null;
	var toVec: Vec4 = null;
	var onUpdateFloat: (Float) -> Void = null;
	var onUpdateVec: (Vec4) -> Void = null;
	var onDone: () -> Void = null;
	var type: TweenType = TweenType.None;

	public function new() {}

	public function float(from: Float, to: Float, duration: Float, ?onUpdate: (Float) -> Void, ?onDone: () -> Void, ?ease: Ease): Tween {
		this.fromFloat = from;
		this.toFloat = to;
		this.duration = duration;
		this.onUpdateFloat = onUpdate;
		this.onDone = onDone;
		this.ease = ease != null ? ease : Linear;
		this.type = TweenType.Float;
		return this;
	}

	public function vec4(from: Vec4, to: Vec4, duration: Float, ?onUpdate: (Vec4) -> Void, ?onDone: () -> Void, ?ease: Ease): Tween {
		this.fromVec = from;
		this.toVec = to;
		this.duration = duration;
		this.onUpdateVec = onUpdate;
		this.onDone = onDone;
		this.ease = ease != null ? ease : Linear;
		this.type = TweenType.Vec4;
		return this;
	}

	public function delay(duration: Float, ?onDone: () -> Void): Tween {
		this.duration = duration;
		this.onDone = onDone;
		this.type = TweenType.Delay;
		return this;
	}

	public function start(): Tween {
		if (isStopped()) App.notifyOnUpdate(update);
		elapsed = 0.0;
		paused = false;
		return this;
	}

	public function pause() {
		paused = true;
	}

	public function stop() {
		if (!isStopped()) App.removeUpdate(update);
		paused = true;
		elapsed = 0.0;
	}

	public function isStopped(): Bool {
		return paused && elapsed == 0.0;
	}

	function update() {
		if (paused) return;

		elapsed += Time.delta;
		var t = duration > 0 ? elapsed / duration : 1.0;
		if (t > 1.0) t = 1.0;

		var e = applyEase(t);

		switch (type) {
			case TweenType.Float:
				if (onUpdateFloat != null) onUpdateFloat(fromFloat + (toFloat - fromFloat) * e);
			case TweenType.Vec4:
				if (onUpdateVec != null && fromVec != null && toVec != null) {
					onUpdateVec(new Vec4(
						fromVec.x + (toVec.x - fromVec.x) * e,
						fromVec.y + (toVec.y - fromVec.y) * e,
						fromVec.z + (toVec.z - fromVec.z) * e
					));
				}
			case TweenType.Delay, TweenType.None:
		}

		if (t >= 1.0) {
			paused = true;
			elapsed = 0.0;
			App.removeUpdate(update);
			if (onDone != null) onDone();
		}
	}

	function applyEase(t: Float): Float {
		return switch (ease) {
			case Linear: t;
			case QuadIn: t * t;
			case QuadOut: t * (2 - t);
			case QuadInOut: t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
			case CubicIn: t * t * t;
			case CubicOut: (t - 1) * (t - 1) * (t - 1) + 1;
			case CubicInOut: t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
			case SineIn: 1 - Math.cos(t * Math.PI / 2);
			case SineOut: Math.sin(t * Math.PI / 2);
			case SineInOut: -(Math.cos(Math.PI * t) - 1) / 2;
		}
	}
}

enum abstract Ease(Int) to Int {
	var Linear = 0;
	var QuadIn = 1;
	var QuadOut = 2;
	var QuadInOut = 3;
	var CubicIn = 4;
	var CubicOut = 5;
	var CubicInOut = 6;
	var SineIn = 7;
	var SineOut = 8;
	var SineInOut = 9;
}

enum abstract TweenType(Int) to Int {
	var None = 0;
	var Float = 1;
	var Vec4 = 2;
	var Delay = 3;
}
