package armory.system;

import kha.FastFloat;
import iron.math.Vec4;
import iron.system.Input;

class InputMap {
	static var axes = new Map<String, InputAxis>();
	static var actions = new Map<String, InputAction>();
	var config = "";

	public function new() {}

	/**
	* Set the config that the input map will look for commands
	* @param config The config name
	* @return Void
	**/
	public function setConfig(config: String) {
		this.config = config;
	}

	/**
	* Add input axis in the input map
	* @param name The name of the input axis
	* @param pressure The pressure required to activate pressure sensitivity buttons
	* @param deadzone The displacement required to activate gamepad sticks or catch mouse movement
	* @param index The index used to indentify gamepads
	* @return InputAxis
	**/
	public function addAxis(name: String, ?pressure = 0.0, ?deadzone = 0.0, ?index = 0) {
		var axis = new InputAxis(pressure, deadzone, index);
		axes[name] = axis;
		return axis;
	}

	/**
	* Create input action in the input map
	* @param name The name of the input action
	* @param pressure The pressure required to activate pressure sensitivity buttons
	* @param deadzone The displacement required to activate gamepad sticks and catch mouse movement
	* @param index The index used to indentify gamepads
	* @return InputAction
	**/
	public function addAction(name: String, ?pressure = 0.0, ?index = 0) {
		var action = new InputAction(pressure, index);
		actions[name] = action;
		return action;
	}

	/**
	* Get the input axis present in the input map by its name
	* @param name The name of the input axis
	* @return InputAxis
	**/
	public inline function getAxis(name: String) {
		return axes[name];
	}

	/**
	* Get the input action present in the input map by its name
	* @param name The name of the input action
	* @return InputAction
	**/
	public inline function getAction(name: String) {
		return actions[name];
	}

	/**
	* Get the vector of the given input axis
	* @param name The name of the input axis
	* @return Vec4
	**/
	public inline function getVec(name: String) {
		return axes[name].getVec(config);
	}

	/**
	* Check if the given input action is started
	* @param name The name of the input action
	* @return Bool
	**/
	public inline function started(name: String) {
		return actions[name].started(config);
	}

	/**
	* Check if the given input action is released
	* @param name The name of the target input action
	* @return Bool
	**/
	public inline function released(name: String) {
		return actions[name].released(config);
	}
}

class InputAction {
	public final pressure: FastFloat;
	public final index: Int;

	static var commands = new Map<String, Array<InputActionCommand>>();
	var display = new Map<InputActionCommand, String>();

	public function new(pressure: FastFloat, index: Int) {
		this.index = index;
		this.pressure = pressure;
	}

	/**
	 * Get the display form of all commands that activates this action according to the active config
	 * @param config 
	 */
	public function getDisplay(config: String) {
		var s = "";
		for (c in commands[config]) {
			s += display[c] + " OR ";
		}
		return s;
	}

	/**
	* Add a keyboard input command
	* @param key The key that should be started or released
	* @param modifiers The keys that should be down before activate the main key
	* @param config The input command config
	* @param display The form this command will be displayed
	* @return InputActionCommand
	**/
	public function addKeyboard(key: String, ?modifiers: Array<String>, ?config = "", ?display = "") {
		var mod = modifiers == null ? new Array<String>() : modifiers;
		var command = new KeyboardActionCommand(this, key, mod);
		addCommand(command, config, display);
		return command;
	}

	/**
	* Add a mouse input command
	* @param button The button that should be started or released
	* @param modifiers The buttons that should be down before activate the main key
	* @param config The input command config
	* @param display The form this command will be displayed
	* @return InputActionCommand
	**/
	public function addMouse(button: String, ?modifiers: Array<String>, ?config = "", ?display = "") {
		var mod = modifiers == null ? new Array<String>() : modifiers;
		var command = new MouseActionCommand(this, button, mod);
		addCommand(command, config, display);
		return command;
	}

	/**
	* Add a gamepad input command
	* @param button The button that should be started or released
	* @param modifiers The buttons that should be down before activate the main key
	* @param config The input command config
	* @param display The form this command will be displayed
	* @return InputActionCommand
	**/
	public function addGamepad(button: String, ?modifiers: Array<String>, ?config = "", ?display = "") {
		var mod = modifiers == null ? new Array<String>() : modifiers;
		var command = new GamepadActionCommand(this, button, mod);
		addCommand(command, config, display);
		return command;
	}

	/**
	* Add a custom input command
	* @param command The constructed input command
	* @param config The input command config
	* @return InputActionCommand
	**/
	public function addCommand(command: InputActionCommand, config: String, display: String) {
		if (commands[config] == null) commands[config] = new Array<InputActionCommand>();
		commands[config].push(command);
		this.display[command] = display;
		return command;
	}

	public function started(config: String) {
		for (c in commands[config]) {
			if (c.started()) return true;
		}
		return false;
	}

	public function released(config: String) {
		for (c in commands[config]) {
			if (c.released()) return true;
		}
		return false;
	}
}

class InputActionCommand {
	final key: String;
	final modifiers: Array<String>;
	final pressure: FastFloat;
	final index: Int;

	public function new(parent: InputAction, key: String, modifiers: Array<String>) {
		this.key = key;
		this.modifiers = modifiers;

		pressure = parent.pressure;
		index = parent.index;
	}

	public function started() {
		return false;
	}

	public function released() {
		return false;
	}
}

class KeyboardActionCommand extends InputActionCommand {
	final keyboard = Input.getKeyboard();

	public function new(parent: InputAction, key: String, modifiers: Array<String>) {
		super(parent, key, modifiers);
	}

	public inline override function started() {
		if (keyboard.started(key)) {
			for (m in modifiers) {
				if (!keyboard.down(m)) return false;
			}
			return true;
		}
		return false;
	}

	public inline override function released() {
		if (keyboard.released(key)) {
			for (m in modifiers) {
				if (!keyboard.down(m)) return false;
			}
			return true;
		}
		return false;
	}
}

class MouseActionCommand extends InputActionCommand {
	final mouse = Input.getMouse();

	public function new(parent: InputAction, key: String, modifiers: Array<String>) {
		super(parent, key, modifiers);
	}

	public override function started() {
		if (mouse.started(key)) {
			for (m in modifiers) {
				if (!mouse.down(m)) return false;
			}
			return true;
		}
		return false;
	}

	public override function released() {
		if (mouse.released(key)) {
			for (m in modifiers) {
				if (!mouse.down(m)) return false;
			}
			return true;
		}
		return false;
	}
}

class GamepadActionCommand extends InputActionCommand {
	final gamepad: Gamepad;

	public function new(parent: InputAction, key: String, modifiers: Array<String>) {
		super(parent, key, modifiers);
		gamepad = Input.getGamepad(index);
	}

	public inline override function started() {
		if (gamepad.started(key)) {
			for (m in modifiers) {
				if (gamepad.down(m) <= pressure) return false;
			}
			return true;
		}
		return false;
	}

	public inline override function released() {
		if (gamepad.released(key)) {
			for (m in modifiers) {
				if (gamepad.down(m) <= pressure) return false;
			}
			return true;
		}
		return false;
	}
}

class InputAxis {
	public final pressure: FastFloat;
	public final deadzone: FastFloat;
	public final index: Int;
	static var commandsX = new Map<String, Array<InputAxisCommand>>();
	static var scaleX = 1.0;
	static var commandsY = new Map<String, Array<InputAxisCommand>>();
	static var scaleY = 1.0;
	static var normalize = false;
	static var vec = new Vec4();
	var display = new Map<InputAxisCommand, String>();

	public function new(pressure: FastFloat, deadzone: FastFloat, index: Int) {
		this.index = index;
		this.pressure = pressure;
		this.deadzone = deadzone;
	}

	/**
	 * Get the display form of all commands that activates this axis according to the active config
	 * @param config 
	 */
	public function getDisplay(config: String) {
		var s = "";
		for (c in commandsX[config]) {
			s += display[c] + " OR ";
		}

		for (c in commandsY[config]) {
			s += display[c] + " OR ";
		}

		return s;
	}

	/**
	* Add a keyboard input command
	* @param position The position that the added input command will be in the returned vector ("x" or "y")
	* @param positiveKey The key that when pressed will sum +1
	* @param negativeKey The key that when pressed will sum -1
	* @param config The input command config
	* @param display The form this command will be displayed
	* @return InputAxisCommand
	**/
	public function addKeyboard(position: String, positiveKey: String, ?negativeKey = "", ?config = "", ?display = "") {
		var command = new KeyboardAxisCommand(this, positiveKey, negativeKey);
		addCommand(position, command, config, display);
		return command;
	}

	/**
	* Add a mouse input command
	* @param position The position that the added input command will be in the returned vector ("x" or "y")
	* @param positiveButton The key that when pressed will sum +1
	* @param negativeButton The key that when pressed will sum -1
	* @param config The input command config
	* @param display The form this command will be displayed
	* @return InputAxisCommand
	**/
	public function addMouse(position: String, positiveButton: String, ?negativeButton = "", ?config = "", ?display = "") {
		var command = new MouseAxisCommand(this, positiveButton, negativeButton);
		addCommand(position, command, config, display);
		return command;
	}

	/**
	* Add a gamepad input command
	* @param position The position that the added input command will be in the returned vector ("x" or "y")
	* @param positiveButton The key that when pressed will sum +1
	* @param negativeButton The key that when pressed will sum -1
	* @param config The input command config
	* @param display The form this command will be displayed
	* @return InputAxisCommand
	**/
	public function addGamepad(position: String, positiveButton: String, ?negativeButton = "", ?config = "", ?display = "") {
		var command = new GamepadAxisCommand(this, positiveButton, negativeButton);
		addCommand(position, command, config, display);
		return command;
	}

	/**
	* Add a custom input command
	* @param command The constructed input command
	* @param config The input command config
	* @param display The form this command will be displayed
	* @return InputAxisCommand
	**/
	public function addCommand(position: String, command: InputAxisCommand, config: String, display: String) {
		switch (position) {
			case "x": {
				if (commandsX[config] == null) commandsX[config] = new Array<InputAxisCommand>();
				commandsX[config].push(command);
			}
			case "y": {
				if (commandsY[config] == null) commandsY[config] = new Array<InputAxisCommand>();
				commandsY[config].push(command);
			}
		}
		this.display[command] = display;
		return command;
	}

	/**
	* Set the scale of the returned vector
	* @param x The scale of the commands in the position x
	* @param y The scale of the commands in the positon y
	* @return Void
	**/
	public function setScale(x: FastFloat, y: FastFloat) {
		scaleX = x;
		scaleY = y;
	}

	/**
	* Enable the returned vector normalization
	* @return Void
	**/
	public function enableNormalize() {
		normalize = true;
	}

	/**
	* Disable the returned vector normalization
	* @return Void
	**/
	public function disableNormalize() {
		normalize = false;
	}

	/**
	* Get the input axis vector
	* @return Void
	**/
	public inline function getVec(config: String) {
		vec.set(0, 0, 0);

		for (c in commandsX[config]) {
			if (c.getScale() != 0.0) vec.x += c.getScale();
		}

		for (c in commandsY[config]) {
			if (c.getScale() != 0.0) vec.y += c.getScale();
		}

		if (normalize) vec.normalize();

		vec.x *= scaleX;
		vec.y *= scaleY;

		return vec;
	}
}

class InputAxisCommand {
	final positiveKey: String;
	final negativeKey: String;
	final pressure: FastFloat;
	final minusPressure: FastFloat;
	final deadzone: FastFloat;
	final minusDeadzone: FastFloat;
	var scale: FastFloat;

	public function new(parent: InputAxis, positiveKey: String, negativeKey: String) {
		this.positiveKey = positiveKey;
		this.negativeKey = negativeKey;

		pressure = parent.pressure;
		minusPressure = -pressure;
		deadzone = parent.deadzone;
		minusDeadzone = -deadzone;
	}

	public function getScale() {
		return scale;
	}
}

class KeyboardAxisCommand extends InputAxisCommand {
	final keyboard = Input.getKeyboard();

	public function new(parent: InputAxis, positiveKey: String, negativeKey: String) {
		super(parent, positiveKey, negativeKey);
	}

	public inline override function getScale() {
		var scale = 0.0;
		if (keyboard.down(positiveKey)) scale++;
		if (keyboard.down(negativeKey)) scale--;
		return scale;
	}
}

class MouseAxisCommand extends InputAxisCommand {
	final mouse = Input.getMouse();

	public function new(parent: InputAxis, positiveKey: String, negativeKey: String) {
		super(parent, positiveKey, negativeKey);
	}

	public inline override function getScale() {
		scale = 0.0;
		var movementX = mouse.movementX;
		var movementY = mouse.movementY;
		var wheelDelta = mouse.wheelDelta;

		switch (positiveKey) {
			case "moved x": if (movementX > deadzone) scale++;
			case "movement x": if (movementX > deadzone) return movementX - deadzone;
			case "moved y":	if (movementY > deadzone) scale++;
			case "movement y": if (movementY > deadzone) return movementY - deadzone;
			case "wheel moved": if (wheelDelta > deadzone) scale++;
			case "wheel movement": if (wheelDelta > deadzone) return wheelDelta - deadzone;
			default: if (mouse.down(positiveKey)) scale++;
		}
		switch (negativeKey) {
			case "moved x": if (movementX < minusDeadzone) scale--;
			case "movement x": if (movementX < minusDeadzone) return movementX + deadzone;
			case "moved y": if (movementY < minusDeadzone) scale--;
			case "movement y": if (movementY < minusDeadzone) return movementY + deadzone;
			case "wheel moved": if (wheelDelta < minusDeadzone) scale--;
			case "wheel movement": if (wheelDelta < minusDeadzone) return wheelDelta + deadzone;
			default: if (mouse.down(negativeKey)) scale--;
		}
		return scale;
	}
}

class GamepadAxisCommand extends InputAxisCommand {
	final gamepad: Gamepad;

	public function new(parent: InputAxis, positiveKey: String, negativeKey: String) {
		super(parent, positiveKey, negativeKey);
		gamepad = Input.getGamepad(parent.index);
	}

	public inline override function getScale() {
		scale = 0.0;
		var rx = gamepad.rightStick.movementX;
		var ry = gamepad.rightStick.movementY;
		var lx = gamepad.leftStick.movementX;
		var ly = gamepad.leftStick.movementY;
		var rt = gamepad.down("r2") > 0.0 ? (gamepad.down("r2") - pressure) / (1 - pressure) : 0.0;
		var lt = gamepad.down("l2") > 0.0 ? (gamepad.down("r2") - pressure) / (1 - pressure) : 0.0;

		switch (positiveKey) {
			case "right stick moved x": if (rx > deadzone) scale++;
			case "right stick movement x": if (rx > deadzone) return rx - deadzone;
			case "right stick moved y": if (ry > deadzone) scale++;
			case "right stick movement y": if (ry > deadzone) return ry - deadzone;
			case "left stick moved x": if (lx > deadzone) scale++;
			case "left stick movement x": if (lx > deadzone) return lx - deadzone;
			case "left stick moved y": if (ly > deadzone) scale++;
			case "left stick movement y": if (ly > deadzone) return ly - deadzone;
			case "right trigger": scale += rt;
			case "left trigger": scale += lt;
			default: if (gamepad.down(positiveKey) > pressure) scale++;
		}

		switch (negativeKey) {
			case "right stick moved x": if (rx < minusDeadzone) scale--;
			case "right stick movement x": if (rx < minusDeadzone) return rx + deadzone;
			case "right stick moved y": if (ry < minusDeadzone) scale--;
			case "right stick movement y": if (ry < minusDeadzone) return ry + deadzone;
			case "left stick moved x": if (lx < minusDeadzone) scale--;
			case "left stick movement x": if (lx < minusDeadzone) return lx + deadzone;
			case "left stick moved y": if (ly < minusDeadzone) scale--;
			case "left stick movement y": if (ly < minusDeadzone) return ly + deadzone;
			case "right trigger": scale -= rt;
			case "left trigger": scale -= lt;
			default: if (gamepad.down(negativeKey) < minusPressure) scale--;
		}

		return scale;
	}
}