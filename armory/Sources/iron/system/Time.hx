package iron.system;

class Time {
	public static var scale = 1.0;
	public static var step(get, never): Float;
	static function get_step(): Float {
		if (frequency == null) initFrequency();
		return (1 / frequency) * scale;
	}

	static var _fixedStep: Null<Float>;
	public static var fixedStep(get, never): Float;
	static function get_fixedStep(): Float {
		return _fixedStep;
	}
	public static function initFixedStep(value: Float = 1 / 60) {
		_fixedStep = value;
	}

	static var lastRealDelta = 0.0;
	public static var realDelta = 0.0;

	static var lastDelta = 0.0;
	public static var delta = 0.0;

	public static inline function time(): Float {
		return kha.Scheduler.time();
	}
	public static inline function realTime(): Float {
		return kha.Scheduler.realTime();
	}

	static var frequency: Null<Int> = null;

	static function initFrequency() {
		frequency = kha.Display.primary != null ? kha.Display.primary.frequency : 60;
	}

	public static function update() {
		delta = realTime() - lastDelta;
		lastDelta = realTime();
	}

	public static function render() {
		realDelta = realTime() - lastRealDelta;
		lastRealDelta = realTime();
	}
}
