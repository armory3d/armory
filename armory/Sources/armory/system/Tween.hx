package armory.system;

import iron.App;
import iron.system.Time;
import iron.math.Vec4;

class Tween {
	public var paused: Bool = true;
	public var elapsed: Float = 0.0;
	public var duration: Float = 1.0;
	public var ease: Ease = Linear;

	var type: TweenType = TweenType.None;

	var fromFloat: Float = 0.0;
	var toFloat: Float = 0.0;

	var fromVec: Vec4 = null;
	var toVec: Vec4 = null;
	var tempVec: Vec4 = new Vec4();

	// TODO: Add support for more types (Vec2, Quat, etc.) and more properties (color, rotation, etc.)

	var onUpdateFloat: Float->Void = null;
	var onUpdateVec: Vec4->Void = null;
	var onDone: Void->Void = null;

	public function new() {}

	public function float(from: Float, to: Float, duration: Float, ?onUpdate: Float->Void, ?onDone: Void->Void, ?ease: Ease): Tween {
		this.fromFloat = from;
		this.toFloat = to;
		this.duration = duration;
		this.onUpdateFloat = onUpdate;
		this.onDone = onDone;
		this.ease = ease != null ? ease : Linear;
		this.type = TweenType.Float;
		return this;
	}

	public function vec4(from: Vec4, to: Vec4, duration: Float, ?onUpdate: Vec4->Void, ?onDone: Void->Void, ?ease: Ease): Tween {
		this.fromVec = from;
		this.toVec = to;
		this.duration = duration;
		this.onUpdateVec = onUpdate;
		this.onDone = onDone;
		this.ease = ease != null ? ease : Linear;
		this.type = TweenType.Vec4;
		return this;
	}

	public function delay(duration: Float, ?onDone: Void->Void): Tween {
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

	public function resume() {
		if (!isStopped()) paused = false;
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
					tempVec.set(
						fromVec.x + (toVec.x - fromVec.x) * e,
						fromVec.y + (toVec.y - fromVec.y) * e,
						fromVec.z + (toVec.z - fromVec.z) * e
					);
					onUpdateVec(tempVec);
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

			case SineIn: 1 - Math.cos(t * Math.PI / 2);
			case SineOut: Math.sin(t * Math.PI / 2);
			case SineInOut: -(Math.cos(Math.PI * t) - 1) / 2;

			case QuadIn: t * t;
			case QuadOut: t * (2 - t);
			case QuadInOut: t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;

			case CubicIn: t * t * t;
			case CubicOut: (t - 1) * (t - 1) * (t - 1) + 1;
			case CubicInOut: t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;

			case QuartIn: t * t * t * t;
			case QuartOut: 1 - Math.pow(1 - t, 4);
			case QuartInOut: t < 0.5 ? 8 * t * t * t * t : 1 - 8 * Math.pow(1 - t, 4);

			case QuintIn: t * t * t * t * t;
			case QuintOut: 1 + Math.pow(t - 1, 5);
			case QuintInOut: t < 0.5 ? 16 * t * t * t * t * t : 1 + 16 * Math.pow(t - 1, 5);

			case ExpoIn: t == 0 ? 0 : Math.pow(2, 10 * (t - 1));
			case ExpoOut: t == 1 ? 1 : 1 - Math.pow(2, -10 * t);
			case ExpoInOut:
				t == 0 ? 0 :
				t == 1 ? 1 :
				t < 0.5 ? Math.pow(2, 20 * t - 10) / 2 :
				(2 - Math.pow(2, -20 * t + 10)) / 2;

			case CircIn: 1 - Math.sqrt(1 - t * t);
			case CircOut: Math.sqrt(1 - Math.pow(t - 1, 2));
			case CircInOut:
				t < 0.5
					? (1 - Math.sqrt(1 - 4 * t * t)) / 2
					: (Math.sqrt(1 - Math.pow(-2 * t + 2, 2)) + 1) / 2;

			case BackIn:
				var c1 = 1.70158;
				var c3 = c1 + 1;
				c3 * t * t * t - c1 * t * t;

			case BackOut:
				var c1 = 1.70158;
				var c3 = c1 + 1;
				1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);

			case BackInOut:
				var c1 = 1.70158;
				var c2 = c1 * 1.525;
				t < 0.5
					? (Math.pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
					: (Math.pow(2 * t - 2, 2) * ((c2 + 1) * (2 * t - 2) + c2) + 2) / 2;

			case BounceIn: 1 - applyBounceOut(1 - t);
			case BounceOut: applyBounceOut(t);
			case BounceInOut:
				t < 0.5
					? (1 - applyBounceOut(1 - 2 * t)) / 2
					: (1 + applyBounceOut(2 * t - 1)) / 2;

			case ElasticIn:
				t == 0 ? 0 :
				t == 1 ? 1 :
				-Math.pow(2, 10 * t - 10) * Math.sin((t * 10 - 10.75) * ((2 * Math.PI) / 3));

			case ElasticOut:
				t == 0 ? 0 :
				t == 1 ? 1 :
				Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * ((2 * Math.PI) / 3)) + 1;

			case ElasticInOut:
				t == 0 ? 0 :
				t == 1 ? 1 :
				t < 0.5
					? -(Math.pow(2, 20 * t - 10) * Math.sin((20 * t - 11.125) * ((2 * Math.PI) / 4.5))) / 2
					: (Math.pow(2, -20 * t + 10) * Math.sin((20 * t - 11.125) * ((2 * Math.PI) / 4.5))) / 2 + 1;
		}
	}

	inline function applyBounceOut(t: Float): Float {
		var n1 = 7.5625;
		var d1 = 2.75;

		return if (t < 1 / d1) {
			n1 * t * t;
		}
		else if (t < 2 / d1) {
			var tt = t - (1.5 / d1);
			n1 * tt * tt + 0.75;
		}
		else if (t < 2.5 / d1) {
			var tt = t - (2.25 / d1);
			n1 * tt * tt + 0.9375;
		}
		else {
			var tt = t - (2.625 / d1);
			n1 * tt * tt + 0.984375;
		}
	}
}

enum abstract Ease(Int) to Int {
	var Linear = 0;
	var SineIn = 1;
	var SineOut = 2;
	var SineInOut = 3;
	var QuadIn = 4;
	var QuadOut = 5;
	var QuadInOut = 6;
	var CubicIn = 7;
	var CubicOut = 8;
	var CubicInOut = 9;
	var QuartIn = 10;
	var QuartOut = 11;
	var QuartInOut = 12;
	var QuintIn = 13;
	var QuintOut = 14;
	var QuintInOut = 15;
	var ExpoIn = 16;
	var ExpoOut = 17;
	var ExpoInOut = 18;
	var CircIn = 19;
	var CircOut = 20;
	var CircInOut = 21;
	var BackIn = 22;
	var BackOut = 23;
	var BackInOut = 24;
	var BounceIn = 25;
	var BounceOut = 26;
	var BounceInOut = 27;
	var ElasticIn = 28;
	var ElasticOut = 29;
	var ElasticInOut = 30;
}

enum abstract TweenType(Int) to Int {
	var None = 0;
	var Float = 1;
	var Vec4 = 2;
	var Delay = 3;
}
