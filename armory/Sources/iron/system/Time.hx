package iron.system;

class Time {

	public static var step(get, never): Float;
	static function get_step(): Float {
		if (frequency == null) initFrequency();
		return 1 / frequency;
	}

	public static var scale = 1.0;
	public static var delta(get, never): Float;
	static function get_delta(): Float {
		if (frequency == null) initFrequency();
		return (1 / frequency) * scale;
	}

	static var last = 0.0;
	public static var realDelta = 0.0;
	public static inline function time(): Float {
		return kha.Scheduler.time();
	}
	public static inline function realTime(): Float {
		return kha.Scheduler.realTime();
	}

	static var frequency: Null<Int> = null;

	static function initFrequency() {
		#if kha_krom
		frequency = kha.Display.primary != null ? Krom.displayFrequency() : 60;
		#else
		frequency = kha.Display.primary != null ? kha.Display.primary.frequency : 60;
		#end
	}

	public static function update() {
		realDelta = realTime() - last;
		last = realTime();
	}
}
