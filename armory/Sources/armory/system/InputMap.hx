package armory.system;

import kha.FastFloat;
import iron.system.Input;

class InputMap {

	static var inputMaps = new Map<String, InputMap>();

	public var keys(default, null) = new Array<InputMapKey>();
	public var lastKeyPressed(default, null) = "";

	var startedCallbacks: Array<Void->Void> = [];
	var releasedCallbacks: Array<Void->Void> = [];

	var attached = false;

	public function new() {}

	public static function getInputMap(inputMap: String): Null<InputMap> {
		if (inputMaps.exists(inputMap)) {
			return inputMaps[inputMap];
		}

		return null;
	}

	public static function addInputMap(inputMap: String): InputMap {
		return inputMaps[inputMap] = new InputMap();
	}

	public static function getInputMapKey(inputMap: String, key: String): Null<InputMapKey> {
		if (inputMaps.exists(inputMap)) {
			for (k in inputMaps[inputMap].keys) {
				if (k.key == key) {
					return k;
				}
			}
		}

		return null;
	}

	public static function removeInputMapKey(inputMap: String, key: String): Bool {
		if (inputMaps.exists(inputMap)) {
			var i = inputMaps[inputMap];

			for (k in i.keys) {
				if (k.key == key) {
					return i.removeKey(k);
				}
			}
		}

		return false;
	}

	public function addKeyboard(key: String, scale: FastFloat = 1.0): InputMapKey {
		return addKey(new KeyboardKey(key, scale));
	}

	public function addMouse(key: String, scale: FastFloat = 1.0, deadzone: FastFloat = 0.0): InputMapKey {
		return addKey(new MouseKey(key, scale, deadzone));
	}

	public function addGamepad(key: String, scale: FastFloat = 1.0, deadzone: FastFloat = 0.0): InputMapKey {
		return addKey(new GamepadKey(key, scale, deadzone));
	}

	public function addKey(key: InputMapKey): InputMapKey {
		keys.push(key);
		if (attached) key.attach(this);
		return key;
	}

	public function removeKey(key: InputMapKey): Bool {
		key.detach();
		return keys.remove(key);
	}

	public function value(): FastFloat {
		var v = 0.0;

		for (k in keys) {
			v += k.value();
		}

		return v;
	}

	public function started() {
		for (k in keys) {
			if (k.started()) {
				lastKeyPressed = k.key;
				return true;
			}
		}

		return false;
	}

	public function released() {
		for (k in keys) {
			if (k.released()) {
				lastKeyPressed = k.key;
				return true;
			}
		}

		return false;
	}

	public function notifyOnStarted(callback: Void->Void) {
		if (!startedCallbacks.contains(callback)) startedCallbacks.push(callback);
		attach();
	}

	public function notifyOnReleased(callback: Void->Void) {
		if (!releasedCallbacks.contains(callback)) releasedCallbacks.push(callback);
		attach();
	}

	public function removeStarted(callback: Void->Void) {
		if (startedCallbacks.contains(callback)) startedCallbacks.remove(callback);
		detach();
	}

	public function removeReleased(callback: Void->Void) {
		if (releasedCallbacks.contains(callback)) releasedCallbacks.remove(callback);
		detach();
	}

	public function emitStarted(key: String) {
		lastKeyPressed = key;
		for (callback in startedCallbacks) callback();
	}

	public function emitReleased(key: String) {
		lastKeyPressed = key;
		for (callback in releasedCallbacks) callback();
	}

	function attach() {
		if (attached) return;
		attached = true;
		for (k in keys) k.attach(this);
	}

	function detach() {
		if (!attached) return;
		if (startedCallbacks.length > 0 || releasedCallbacks.length > 0) return;
		attached = false;
		for (k in keys) k.detach();
	}
}

class InputMapKey {

	public var key: String;
	public var scale: FastFloat;
	public var deadzone: FastFloat;

	public function new(key: String, scale = 1.0, deadzone = 0.0) {
		this.key = key.toLowerCase();
		this.scale = scale;
		this.deadzone = deadzone;
	}

	public function started(): Bool {
		return false;
	}

	public function released(): Bool {
		return false;
	}

	public function value(): FastFloat {
		return 0.0;
	}

	public function setIndex(index: Int) {}

	public function attach(map: InputMap) {}

	public function detach() {}

	function evalDeadzone(value: FastFloat): FastFloat {
		var v = 0.0;

		if (value > deadzone) {
			v = value - deadzone;

		} else if (value < -deadzone) {
			v = value + deadzone;
		}

		return v * scale;
	}

	function evalPressure(value: FastFloat): FastFloat {
		var v = value - deadzone;

		if (v > 0.0) {
			v /= (1.0 - deadzone);

		} else {
			v = 0.0;
		}

		return v;
	}
}

class KeyboardKey extends InputMapKey {

	var kb = Input.getKeyboard();

	var startedHandler: String->Void = null;
	var releasedHandler: String->Void = null;

	public inline override function started() {
		return kb.started(key);
	}

	public inline override function released() {
		return kb.released(key);
	}

	public inline override function value(): FastFloat {
		return kb.down(key) ? scale : 0.0;
	}

	public override function attach(map: InputMap) {
		if (startedHandler != null) return;
		startedHandler = function(name: String) {
			if (name == key) map.emitStarted(key);
		};
		releasedHandler = function(name: String) {
			if (name == key) map.emitReleased(key);
		};
		kb.notifyOnStarted(startedHandler);
		kb.notifyOnReleased(releasedHandler);
	}

	public override function detach() {
		if (startedHandler == null) return;
		kb.removeOnStarted(startedHandler);
		kb.removeOnReleased(releasedHandler);
		startedHandler = null;
		releasedHandler = null;
	}
}

class MouseKey extends InputMapKey {

	var m = Input.getMouse();

	var startedHandler: String->Void = null;
	var releasedHandler: String->Void = null;

	public inline override function started() {
		return m.started(key);
	}

	public inline override function released() {
		return m.released(key);
	}

	public override function value(): FastFloat {
		return switch (key) {
			case "movement x": evalDeadzone(m.movementX);
			case "movement y": evalDeadzone(m.movementY);
			case "wheel": evalDeadzone(m.wheelDelta);
			default: m.down(key) ? scale : 0.0;
		}
	}

	public override function attach(map: InputMap) {
		if (startedHandler != null) return;
		if (!Mouse.buttons.contains(key)) return; // Movement and wheel have no down/up event
		startedHandler = function(name: String) {
			if (name == key) map.emitStarted(key);
		};
		releasedHandler = function(name: String) {
			if (name == key) map.emitReleased(key);
		};
		m.notifyOnStarted(startedHandler);
		m.notifyOnReleased(releasedHandler);
	}

	public override function detach() {
		if (startedHandler == null) return;
		m.removeOnStarted(startedHandler);
		m.removeOnReleased(releasedHandler);
		startedHandler = null;
		releasedHandler = null;
	}
}

class GamepadKey extends InputMapKey {

	var g = Input.getGamepad();

	var startedHandler: String->Void = null;
	var releasedHandler: String->Void = null;

	public inline override function started() {
		return g.started(getKey());
	}

	public inline override function released() {
		return g.released(getKey());
	}

	public override function value(): FastFloat {
		return switch(key) {
			case "ls movement x": evalDeadzone(g.leftStick.x);
			case "ls movement y": evalDeadzone(g.leftStick.y);
			case "rs movement x": evalDeadzone(g.rightStick.x);
			case "rs movement y": evalDeadzone(g.rightStick.y);
			case "lt pressure": evalDeadzone(evalPressure(g.down("l2")));
			case "rt pressure": evalDeadzone(evalPressure(g.down("r2")));
			default: evalDeadzone(g.down(key));
		}
	}

	public override function setIndex(index: Int) {
		g = Input.getGamepad(index);
	}

	public override function attach(map: InputMap) {
		if (startedHandler != null) return;
		if (g == null) g = Input.getGamepad();
		if (g == null) return; // No gamepad connected
		var name = getKey();
		startedHandler = function(n: String) {
			if (n == name) map.emitStarted(key);
		};
		releasedHandler = function(n: String) {
			if (n == name) map.emitReleased(key);
		};
		g.notifyOnStarted(startedHandler);
		g.notifyOnReleased(releasedHandler);
	}

	public override function detach() {
		if (startedHandler == null) return;
		if (g != null) {
			g.removeOnStarted(startedHandler);
			g.removeOnReleased(releasedHandler);
		}
		startedHandler = null;
		releasedHandler = null;
	}

	// "lt pressure" and "rt pressure" are reported as the l2/r2 buttons
	function getKey(): String {
		return switch (key) {
			case "lt pressure": "l2";
			case "rt pressure": "r2";
			default: key;
		}
	}
}
