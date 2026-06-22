package armory.system;

import kha.FastFloat;
import iron.system.Input;

class InputMap {

	static var inputMaps = new Map<String, InputMap>();

	public var keys(default, null) = new Array<InputMapKey>();
	public var lastKeyPressed(default, null) = "";

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
		return key;
	}

	public function removeKey(key: InputMapKey): Bool {
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

	public inline override function started() {
		return kb.started(key);
	}

	public inline override function released() {
		return kb.released(key);
	}

	public inline override function value(): FastFloat {
		return kb.down(key) ? scale : 0.0;
	}
}

class MouseKey extends InputMapKey {

	var m = Input.getMouse();

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
}

class GamepadKey extends InputMapKey {

	var g = Input.getGamepad();

	public inline override function started() {
		return g.started(key);
	}

	public inline override function released() {
		return g.released(key);
	}

	public override function value(): FastFloat {
		return switch(key) {
			case "ls movement x": evalDeadzone(g.leftStick.movementX);
			case "ls movement y": evalDeadzone(g.leftStick.movementY);
			case "rs movement x": evalDeadzone(g.rightStick.movementX);
			case "rs movement y": evalDeadzone(g.rightStick.movementY);
			case "lt pressure": evalDeadzone(evalPressure(g.down("l2")));
			case "rt pressure": evalDeadzone(evalPressure(g.down("r2")));
			default: evalDeadzone(g.down(key));
		}
	}

	public override function setIndex(index: Int) {
		g = Input.getGamepad(index);
	}
}
