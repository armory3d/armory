package armory.system;

import kha.FastFloat;
import iron.system.Input;

class InputMap {

	static var inputMaps(default, null) = new Map<String, InputMap>();

	public var inputs(default, null) = new Array<InputMapKey>();
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
			for (i in inputMaps[inputMap].inputs) {
				if (i.key == key) {
					return i;
				}
			}
		}

		return null;
	}

	public function addKeyboard(key: String, scale: FastFloat = 1.0): InputMapKey {
		return addInput(new KeyboardKey(key, scale));
	}

	public function addMouse(key: String, scale: FastFloat = 1.0, deadzone: FastFloat = 0.0): InputMapKey {
		return addInput(new MouseKey(key, scale, deadzone));
	}

	public function addGamepad(key: String, scale: FastFloat = 1.0, deadzone: FastFloat = 0.0): InputMapKey {
		return addInput(new GamepadKey(key, scale, deadzone));
	}

	public function addInput(input: InputMapKey): InputMapKey {
		inputs.push(input);
		return input;
	}

	public function removeInput(input: InputMapKey): Bool {
		return inputs.remove(input);
	}

	public function value(): FastFloat {
		var v = 0.0;

		for (i in inputs) {
			v += i.value();
		}

		return v;
	}

	public function started() {
		for (i in inputs) {
			if (i.started()) {
				lastKeyPressed = i.key;
				return true;
			}
		}

		return false;
	}

	public function released() {
		for (i in inputs) {
			if (i.released()) {
				lastKeyPressed = i.key;
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
