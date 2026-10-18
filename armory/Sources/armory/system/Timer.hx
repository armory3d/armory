package armory.system;

import iron.App;
import iron.system.Time;

class Timer {
	public var timeout: Signal = new Signal();

	public var oneShot: Bool = true;
	public var paused: Bool = true;
	public var timeLeft(get, never): Float;
	var _timeLeft: Float = 1.0;
	public var waitTime(default, set): Float = 1.0;

	public function new(time: Float = 1.0, oneShot: Bool = true) {
		this.oneShot = oneShot;
		this.waitTime = time;
		this._timeLeft = time;
	}

	function get_timeLeft(): Float {
		return _timeLeft;
	}

	function set_waitTime(value: Float): Float {
		this.waitTime = value;
		this._timeLeft = value;
		return waitTime;
	}

	public function start(time: Float = -1.0) {
		if (isStopped()) App.notifyOnUpdate(update);
		if (time > 0) {
			waitTime = time;
		}
		_timeLeft = waitTime;
		paused = false;
	}

	public function pause() {
		paused = true;
	}

	public function stop() {
		if (!isStopped()) App.removeUpdate(update);
		paused = true;
		_timeLeft = waitTime;
	}

	public function isStopped(): Bool {
		return paused && _timeLeft == waitTime;
	}

	function update() {
		if (paused) return;

		_timeLeft -= Time.delta;

		if (_timeLeft <= 0) {
			timeout.emit();

			if (oneShot) {
				paused = true;
				_timeLeft = waitTime;
				App.removeUpdate(update);
			} else {
				_timeLeft += waitTime;
			}
		}
	}
}