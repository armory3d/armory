package iron.system;

class Time {
	public static var scale = 1.0;

	static var frequency: Null<Int> = null;
	static function initFrequency() {
		frequency = kha.Display.primary != null ? kha.Display.primary.frequency : 60;
	}

	public static var step(get, never): Float;
	static function get_step(): Float {
		if (frequency == null) initFrequency();
		return 1 / frequency;
	}

	static var _fixedStep: Null<Float>;
	public static var fixedStep(get, never): Float;
	static function get_fixedStep(): Float {
		return _fixedStep;
	}
	public static function initFixedStep(value: Float = 1 / 60) {
		_fixedStep = value;
	}

	static var lastTime = 0.0;
	static var _delta = 0.0;
	public static var delta(get, never): Float;
	static function get_delta(): Float {
		return _delta;
	}

	static var lastRenderTime = 0.0;
	static var _renderDelta = 0.0;
	public static var renderDelta(get, never): Float;
	static function get_renderDelta(): Float {
		return _renderDelta;
	}

	public static inline function time(): Float {
		return kha.Scheduler.time();
	}

	public static inline function realTime(): Float {
		return kha.Scheduler.realTime();
	}

	public static function update() {
		_delta = realTime() - lastTime;
		lastTime = realTime();
	}

	public static function render() {
		_renderDelta = realTime() - lastRenderTime;
		lastRenderTime = realTime();
	}
}
