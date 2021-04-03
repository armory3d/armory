package armory.system;

import kha.FastFloat;
import iron.system.Input;

class InputMap {
	var commands = new Map<String, Null<Array<InputCommand>>>();

	public function new() {}

	public function addKeyboard(config: String) {
		var command = new KeyboardCommand();
		return addCustomCommand(command, config);
	}

	public function addGamepad(config: String) {
		var command = new GamepadCommand();
		return addCustomCommand(command, config);
	}

	public function addCustomCommand(command: InputCommand, config: String) {
		if (commands[config] == null) commands[config] = new Array<InputCommand>();
		commands[config].push(command);
		return command;
	}
}

class ActionMap extends InputMap {

	public inline function started(config: String) {
		var started = false;

		for (c in commands[config]) {
			if (c.started()) {
				started = true;
				break;
			}
		}

		return started;
	}

	public inline function released(config: String) {
		var released = false;

		for (c in commands[config]) {
			if (c.released()) {
				released = true;
				break;
			}
		}

		return released;
	}
}

class AxisMap extends InputMap {
	var scale: FastFloat = 1.0;

	public inline function getAxis(config: String) {
		var axis = 0.0;

		for (c in commands[config]) {
			var tempAxis = c.getAxis();

			if (tempAxis != 0.0 && tempAxis != axis) {
				axis += tempAxis;
				scale = c.getScale();
			}
		}

		return axis;
	}

	public inline function getScale() {
		return scale;
	}
}

class InputCommand {
	var keys = new Array<String>();
	var modifiers = new Array<String>();
	var displacementKeys = new Array<String>();
	var displacementModifiers = new Array<String>();
	var deadzone: FastFloat = 0.0;
	var scale: FastFloat = 1.0;

	public function new() {}

	public function setKeys(keys: Array<String>) {
		return this.keys = keys;
	}

	public function setMods(modifiers: Array<String>) {
		return this.modifiers = modifiers;
	}

	public function setDisplacementKeys(keys: Array<String>) {
		return displacementKeys = keys;
	}

	public function setDisplacementMods(modifiers: Array<String>) {
		return displacementModifiers = modifiers;
	}

	public function setDeadzone(deadzone: FastFloat) {
		return this.deadzone = deadzone;
	}

	public function setScale(scale: FastFloat) {
		return this.scale = scale;
	}

	public function getScale() {
		return scale;
	}

	public function started() {
		return false;
	}

	public function released() {
		return false;
	}

	public function getAxis(): FastFloat {
		return 0.0;
	}
}

class KeyboardCommand extends InputCommand {
	var keyboard = Input.getKeyboard();
	var mouse = Input.getMouse();

	public inline override function started() {
		for (k in keys) {
			if (keyboard.started(k)) {
				for (m in modifiers) {
					if (!keyboard.down(m)) return false;
				}

				for (m in displacementModifiers) {
					if (!mouse.down(m)) return false;
				}

				return true;
			}
		}

		for (k in displacementKeys) {
			if (mouse.started(k)) {
				for (m in modifiers) {
					if (!keyboard.down(m)) return false;
				}
					
				for (m in displacementModifiers) {
					if (!mouse.down(m)) return false;
				}

				return true;
			}
		}

		return false;
	}

	public inline override function released() {
		for (k in keys) {
			if (keyboard.released(k)) {
				for (m in modifiers) {
					if (!keyboard.down(m)) return false;
				}

				for (m in displacementModifiers) {
					if (!mouse.down(m)) return false;
				}

				return true;
			}
		}

		for (k in displacementKeys) {
			if (mouse.released(k)) {
				for (m in modifiers) {
					if (!keyboard.down(m)) return false;
				}
					
				for (m in displacementModifiers) {
					if (!mouse.down(m)) return false;
				}

				return true;
			}
		}

		return false;
	}

	public inline override function getAxis() {
		var axis = 0.0;
		var movementX = mouse.movementX;
		var movementY = mouse.movementY;
		var wheelDelta = mouse.wheelDelta;

		for (k in keys) {
			if (keyboard.down(k)) {
				axis++;
				break;
			}
		}

		for (m in modifiers) {
			if (keyboard.down(m)) {
				axis --;
				break;
			}
		}

		for (k in displacementKeys) {
			switch (k) {
				case "moved x": if (movementX > deadzone) axis++;
				case "moved y": if (movementY > deadzone) axis--;
				case "wheel": if (wheelDelta < -deadzone) axis++;
				case "movement x": if (movementX > deadzone) return movementX - deadzone;
				case "movement y": if (movementY > deadzone) return movementY - deadzone;
				default: {
					if (mouse.down(k)) {
						axis ++;
						break;
					}
				}
			}
		}

		for (m in displacementModifiers) {
			switch (m) {
				case "moved x": if (movementX < -deadzone) axis--;
				case "moved y": if (movementY < -deadzone) axis++;
				case "wheel": if (wheelDelta > deadzone) axis--;
				case "movement x": if (movementX < -deadzone) return movementX + deadzone;
				case "movement y": if (movementY < -deadzone) return movementY + deadzone;
				default: {
					if (mouse.down(m)) {
						axis --;
						break;
					}
				}
			}
		}

		return axis > 1 ? 1 : axis < -1 ? -1 : axis;
	}
}

class GamepadCommand extends InputCommand {
	var gamepad = Input.getGamepad(0);

	public inline override function started() {
		for (k in keys) {
			if (gamepad.started(k)) {
				for (m in modifiers) {
					if (gamepad.down(m) < deadzone) return false;
				}

				return true;
			}
		}

		return false;
	}

	public inline override function released() {
		for (k in keys) {
			if (gamepad.released(k)) {
				for (m in modifiers) {
					if (gamepad.down(m) < deadzone) return false;
				}

				return true;
			}
		}

		return false;
	}

	public inline override function getAxis() {
		var axis = 0.0;
		var rsMovementX = gamepad.rightStick.movementX;
		var rsMovementY = gamepad.rightStick.movementY;
		var lsMovementX = gamepad.leftStick.movementX;
		var lsMovementY = gamepad.leftStick.movementY;
		var rtPressure = gamepad.down("r2") > 0.0 ? (gamepad.down("r2") - deadzone) / (1 - deadzone) : 0.0;
		var ltPressure = gamepad.down("l2") > 0.0 ? (gamepad.down("r2") - deadzone) / (1 - deadzone) : 0.0;

		for (k in keys) {
			switch(k) {
				case "rtPressure": axis += rtPressure;
				case "ltPressure": axis += ltPressure;
				default: {
					if (gamepad.down(k) > deadzone) {
						axis++;
						break;
					}
				}
			}
		}

		for (m in modifiers) {
			switch (m) {
				case "rtPressure": axis -= rtPressure;
				case "ltPressure": axis -= ltPressure;
				default: {
					if (gamepad.down(m) > deadzone) {
						axis--;
						break;
					}
				}
			}
		}

		for (k in displacementKeys) {
			switch(k) {
			case "rs moved x": if (rsMovementX > deadzone) axis++;
			case "rs moved y": if (rsMovementY > deadzone) axis++;
			case "ls moved x": if (lsMovementX > deadzone) axis++;
			case "ls moved y": if (lsMovementY > deadzone) axis++;
			case "rs movement x": if (rsMovementX > deadzone) return rsMovementX - deadzone;
			case "rs movement y": if (rsMovementY > deadzone) return rsMovementY - deadzone;
			case "ls movement x": if (lsMovementX > deadzone) return lsMovementX - deadzone;
			case "ls movement y": if (lsMovementY > deadzone) return lsMovementY - deadzone;
			}
		}

		for (m in displacementModifiers) {
			switch (m) {
				case "rs moved x": if (rsMovementX < -deadzone) axis--;
				case "rs moved y": if (rsMovementY < -deadzone) axis--;
				case "ls moved x": if (lsMovementX < -deadzone) axis--;
				case "ls moved y": if (lsMovementY < -deadzone) axis--;
				case "rs movement x": if (rsMovementX < -deadzone) return rsMovementX + deadzone;
				case "rs movement y": if (rsMovementY < -deadzone) return rsMovementY + deadzone;
				case "ls movement x": if (lsMovementX < -deadzone) return lsMovementX + deadzone;
				case "ls movement y": if (lsMovementY < -deadzone) return lsMovementY + deadzone;

			}
		}

		return axis > 1 ? 1 : axis < -1 ? -1 : axis;
	}
}