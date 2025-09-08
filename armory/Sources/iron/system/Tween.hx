package iron.system;

class Tween {

	static inline var DEFAULT_OVERSHOOT: Float = 1.70158;

	static var eases: Array<Float->Float> = [
		easeLinear,
		easeSineIn, easeSineOut, easeSineInOut,
		easeQuadIn, easeQuadOut, easeQuadInOut,
		easeCubicIn, easeCubicOut, easeCubicInOut,
		easeQuartIn, easeQuartOut, easeQuartInOut,
		easeQuintIn, easeQuintOut, easeQuintInOut,
		easeExpoIn, easeExpoOut, easeExpoInOut,
		easeCircIn, easeCircOut, easeCircInOut,
		easeBackIn, easeBackOut, easeBackInOut,
		easeBounceIn, easeBounceOut, easeBounceInOut,
		easeElasticIn, easeElasticOut, easeElasticInOut
	];

	static var anims: Array<TAnim> = [];

	static var registered = false;
	static inline function register() {
		registered = true;
		App.notifyOnUpdate(update);
		App.notifyOnReset(function() { App.notifyOnUpdate(update); reset(); });
	}

	public static function to(anim: TAnim): TAnim {
		if (!registered) register();
		anim._time = 0;
		anim.isPlaying = (anim.delay != null && anim.delay > 0.0) ? false : true;

		if (anim.ease == null) anim.ease = Ease.Linear;

		if (anim.target != null && anim.props != null) {

			anim._comps = []; anim._x = []; anim._y = []; anim._z = []; anim._w = []; anim._normalize = [];
			for (p in Reflect.fields(anim.props)) {
				var val: Dynamic = Reflect.getProperty(anim.target, p);
				if (Std.isOfType(val, iron.math.Vec4) || Std.isOfType(val, iron.math.Quat)) {
					anim._comps.push(4);
					anim._x.push(val.x);
					anim._y.push(val.y);
					anim._z.push(val.z);
					anim._w.push(val.w);
					anim._normalize.push(Std.isOfType(val, iron.math.Quat));
				}
				else {
					anim._comps.push(1);
					anim._x.push(val);
					anim._y.push(0);
					anim._z.push(0);
					anim._w.push(0);
				}
			}
		}

		anims.push(anim);
		return anim;
	}

	public static function timer(delay: Float, done: Void->Void): TAnim {
		return to({ target: null, props: null, duration: 0, delay: delay, done: done });
	}

	public static function stop(anim: TAnim) {
		anim.isPlaying = false;
		anims.remove(anim);
	}

	public static function reset() {
		anims = [];
	}

	public static function update() {
		var d = Time.delta;
		var i = anims.length;
		while (i-- > 0 && anims.length > 0) {
			var a = anims[i];

			if (a.delay > 0) { // Delay
				a.delay -= d;
				if (a.delay > 0) continue;
			}

			a._time += d;
			a.isPlaying = a._time < a.duration;

			if (a.target != null) {

				if (Std.isOfType(a.target, iron.object.Transform)) a.target.dirty = true;

				// Way too much Reflect trickery..
				var ps = Reflect.fields(a.props);
				for (j in 0...ps.length) {
					var p = ps[j];
					var k = a._time / a.duration;
					if (k > 1) k = 1;

					if (a._comps[j] == 1) {
						var fromVal: Float = a._x[j];
						var toVal: Float = Reflect.getProperty(a.props, p);
						var val: Float = fromVal + (toVal - fromVal) * eases[a.ease](k);
						Reflect.setProperty(a.target, p, val);
					}
					else { // _comps[j] == 4
						var obj = Reflect.getProperty(a.props, p);
						var toX: Float = Reflect.getProperty(obj, "x");
						var toY: Float = Reflect.getProperty(obj, "y");
						var toZ: Float = Reflect.getProperty(obj, "z");
						var toW: Float = Reflect.getProperty(obj, "w");
						if (a._normalize[j]) {
							var qdot = (a._x[j] * toX) + (a._y[j] * toY) + (a._z[j] * toZ) + (a._w[j] * toW);
							if (qdot < 0.0) {
								toX = -toX; toY = -toY; toZ = -toZ; toW = -toW;
							}
						}
						var x: Float = a._x[j] + (toX - a._x[j]) * eases[a.ease](k);
						var y: Float = a._y[j] + (toY - a._y[j]) * eases[a.ease](k);
						var z: Float = a._z[j] + (toZ - a._z[j]) * eases[a.ease](k);
						var w: Float = a._w[j] + (toW - a._w[j]) * eases[a.ease](k);
						if (a._normalize[j]) {
							var l = Math.sqrt(x * x + y * y + z * z + w * w);
							if (l > 0.0) {
								l = 1.0 / l;
								x *= l; y *= l; z *= l; w *= l;
							}
						}
						var t = Reflect.getProperty(a.target, p);
						Reflect.setProperty(t, "x", x);
						Reflect.setProperty(t, "y", y);
						Reflect.setProperty(t, "z", z);
						Reflect.setProperty(t, "w", w);
					}
				}
			}

			if (a.isPlaying) {
				if (a.tick != null) a.tick();
			}
			else {
				anims.splice(i, 1);
				i--;
				a.isPlaying = false;
				if (a.done != null) a.done();
			}
		}
	}

	public static function easeLinear(k: Float): Float { return k; }
	public static function easeSineIn(k: Float): Float { if (k == 0) { return 0; } else if (k == 1) { return 1; } else { return 1 - Math.cos(k * Math.PI / 2); } }
	public static function easeSineOut(k: Float): Float { if (k == 0) { return 0; } else if (k == 1) { return 1; } else { return Math.sin(k * (Math.PI * 0.5)); } }
	public static function easeSineInOut(k: Float): Float { if (k == 0) { return 0; } else if (k == 1) { return 1; } else { return -0.5 * (Math.cos(Math.PI * k) - 1); } }
	public static function easeQuadIn(k: Float): Float { return k * k; }
	public static function easeQuadOut(k: Float): Float { return -k * (k - 2); }
	public static function easeQuadInOut(k: Float): Float { return (k < 0.5) ? 2 * k * k : -2 * ((k -= 1) * k) + 1; }
	public static function easeCubicIn(k: Float): Float { return k * k * k; }
	public static function easeCubicOut(k: Float): Float { return (k = k - 1) * k * k + 1; }
	public static function easeCubicInOut(k: Float): Float { return ((k *= 2) < 1) ? 0.5 * k * k * k : 0.5 * ((k -= 2) * k * k + 2); }
	public static function easeQuartIn(k: Float): Float { return (k *= k) * k; }
	public static function easeQuartOut(k: Float): Float { return 1 - (k = (k = k - 1) * k) * k; }
	public static function easeQuartInOut(k: Float): Float { return ((k *= 2) < 1) ? 0.5 * (k *= k) * k : -0.5 * ((k = (k -= 2) * k) * k - 2); }
	public static function easeQuintIn(k: Float): Float { return k * (k *= k) * k; }
	public static function easeQuintOut(k: Float): Float { return (k = k - 1) * (k *= k) * k + 1; }
	public static function easeQuintInOut(k: Float): Float { return ((k *= 2) < 1) ? 0.5 * k * (k *= k) * k : 0.5 * (k -= 2) * (k *= k) * k + 1; }
	public static function easeExpoIn(k: Float): Float { return k == 0 ? 0 : Math.pow(2, 10 * (k - 1)); }
	public static function easeExpoOut(k: Float): Float { return k == 1 ? 1 : (1 - Math.pow(2, -10 * k)); }
	public static function easeExpoInOut(k: Float): Float { if (k == 0) { return 0; } if (k == 1) { return 1; } if ((k /= 1 / 2.0) < 1.0) { return 0.5 * Math.pow(2, 10 * (k - 1)); } return 0.5 * (2 - Math.pow(2, -10 * --k)); }
	public static function easeCircIn(k: Float): Float { return -(Math.sqrt(1 - k * k) - 1); }
	public static function easeCircOut(k: Float): Float { return Math.sqrt(1 - (k - 1) * (k - 1)); }
	public static function easeCircInOut(k: Float): Float { return k <= .5 ? (Math.sqrt(1 - k * k * 4) - 1) / -2 : (Math.sqrt(1 - (k * 2 - 2) * (k * 2 - 2)) + 1) / 2; }
	public static function easeBackIn(k: Float): Float { if (k == 0) { return 0; } else if (k == 1) { return 1; } else { return k * k * ((DEFAULT_OVERSHOOT + 1) * k - DEFAULT_OVERSHOOT); } }
	public static function easeBackOut(k: Float): Float { if (k == 0) { return 0; } else if (k == 1) { return 1; } else { return ((k = k - 1) * k * ((DEFAULT_OVERSHOOT + 1) * k + DEFAULT_OVERSHOOT) + 1); } }
	public static function easeBackInOut(k: Float): Float { if (k == 0) { return 0; } else if (k == 1) { return 1; } else if ((k *= 2) < 1) { return (0.5 * (k * k * (((DEFAULT_OVERSHOOT * 1.525) + 1) * k - DEFAULT_OVERSHOOT * 1.525))); } else { return (0.5 * ((k -= 2) * k * (((DEFAULT_OVERSHOOT * 1.525) + 1) * k + DEFAULT_OVERSHOOT * 1.525) + 2)); } }
	public static function easeBounceIn(k: Float): Float { return 1 - easeBounceOut(1 - k); }
	public static function easeBounceOut(k: Float): Float { return if (k < (1 / 2.75)) { 7.5625 * k * k; } else if (k < (2 / 2.75)) { 7.5625 * (k -= (1.5 / 2.75)) * k + 0.75; } else if (k < (2.5 / 2.75)) { 7.5625 * (k -= (2.25 / 2.75)) * k + 0.9375; } else { 7.5625 * (k -= (2.625 / 2.75)) * k + 0.984375; } }
	public static function easeBounceInOut(k: Float): Float { return (k < 0.5) ? easeBounceIn(k * 2) * 0.5 : easeBounceOut(k * 2 - 1) * 0.5 + 0.5; }

	public static function easeElasticIn(k: Float): Float {
		var s: Null<Float> = null;
		var a = 0.1, p = 0.4;
		if (k == 0) {
			return 0;
		}
		if (k == 1) {
			return 1;
		}
		if (a < 1) {
			a = 1;
			s = p / 4;
		}
		else {
			s = p * Math.asin(1 / a) / (2 * Math.PI);
		}
		return -(a * Math.pow(2, 10 * (k -= 1)) * Math.sin((k - s) * (2 * Math.PI) / p));
	}

	public static function easeElasticOut(k: Float): Float {
		var s: Null<Float> = null;
		var a = 0.1, p = 0.4;
		if (k == 0) {
			return 0;
		}
		if (k == 1) {
			return 1;
		}
		if (a < 1) {
			a = 1;
			s = p / 4;
		}
		else {
			s = p * Math.asin(1 / a) / (2 * Math.PI);
		}
		return (a * Math.pow(2, -10 * k) * Math.sin((k - s) * (2 * Math.PI) / p) + 1);
	}

	public static function easeElasticInOut(k: Float): Float {
		var s, a = 0.1, p = 0.4;
		if (k == 0) {
			return 0;
		}
		if (k == 1) {
			return 1;
		}
		if (a != 0 || a < 1) {
			a = 1;
			s = p / 4;
		}
		else {
			s = p * Math.asin(1 / a) / (2 * Math.PI);
		}
		if ((k *= 2) < 1) return - 0.5 * (a * Math.pow(2, 10 * (k -= 1)) * Math.sin((k - s) * (2 * Math.PI) / p));
		return a * Math.pow(2, -10 * (k -= 1)) * Math.sin((k - s) * (2 * Math.PI) / p) * 0.5 + 1;
	}
}

typedef TAnim = {
	var target: Dynamic;
	var props: Dynamic;
	var duration: Float;
	@:optional var isPlaying: Null<Bool>;
	@:optional var done: Void->Void;
	@:optional var tick: Void->Void;
	@:optional var delay: Null<Float>;
	@:optional var ease: Null<Ease>;
	// Internal
	@:optional var _time: Null<Float>;
	@:optional var _comps: Array<Int>;
	@:optional var _x: Array<Float>;
	@:optional var _y: Array<Float>;
	@:optional var _z: Array<Float>;
	@:optional var _w: Array<Float>;
	@:optional var _normalize: Array<Bool>;
}

@:enum abstract Ease(Int) from Int to Int {
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
