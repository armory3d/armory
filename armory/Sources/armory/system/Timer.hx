package armory.system;

import iron.App;
import iron.system.Time;

class Timer {
	public var timeout: Signal = new Signal();

	public var oneShot: Bool = true;
	public var paused: Bool = true;
	public var timeLeft: Float = 1.0;
	public var waitTime: Float = 1.0;

	public function new(time: Float = 1.0, oneShot: Bool = true) {
		this.oneShot = oneShot;
		this.waitTime = time;
		this.timeLeft = time;
	}

	public function start(time: Float = -1.0) {
		if (isStopped()) App.notifyOnUpdate(update);
		if (time > 0) {
			waitTime = time;
		}
		timeLeft = waitTime;
		paused = false;
	}

	public function pause() {
		paused = true;
	}

	public function stop() {
		if (!isStopped()) App.removeUpdate(update);
		paused = true;
		timeLeft = waitTime;
	}

	public function isStopped(): Bool {
		return paused && timeLeft == waitTime;
	}

	function update() {
		if (paused) return;

		timeLeft -= Time.delta;

		if (timeLeft <= 0) {
			timeout.emit();

			if (oneShot) {
				paused = true;
				timeLeft = waitTime;
				App.removeUpdate(update);
			} else {
				timeLeft += waitTime;
			}
		}
	}
}