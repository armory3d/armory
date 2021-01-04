package armory.system;

import kha.FastFloat;
import iron.math.Vec4;
import iron.system.Input;

class InputMap {
	static var axes = new Map<String, InputAxis>();
	static var actions = new Map<String, InputAction>();

	public var index: Int;
	public var currentTag: String;

	public function new(index: Int): Void {
		this.index = index;
	}

	/**
	* Set the tag that this input map will look for
	* @param tag The tag name
	* @return Void
	**/
	public function setCurrentTag(tag: String): Void {
		currentTag = tag;
	}

	/**
	* Create input axis in the input map
	* @param name The name of the input axis
	* @param pressure The pressure required to activate pressure sensitivity buttons
	* @param deadzone The displacement required to activate gamepad sticks and catch mouse movement
	* @return Void
	**/
	public function createAxis(name: String, ?pressure: FastFloat, ?deadzone: FastFloat): Void {
		var p = pressure == null ? 0.0 : pressure;
		var d = deadzone == null ? 0.0 : deadzone;
		axes[name] = new InputAxis(this, index, p, d);
	}

	/**
	* Create input action in the input map
	* @param name The name of the input action
	* @param pressure The pressure required to activate pressure sensitivity buttons
	* @param deadzone The displacement required to activate gamepad sticks and catch mouse movement
	* @return Void
	**/
	public function createAction(name: String, ?pressure: FastFloat, ?deadzone: FastFloat): Void {
		var p = pressure == null ? 0.0 : pressure;
		var d = deadzone == null ? 0.0 : deadzone;
		actions[name] = new InputAction(this, index, p, d);
	}

	/**
	* Get the input axis present in the input map by its name
	* @param name The name of the input axis
	* @return InputAxis
	**/
	public inline function getAxis(name: String): InputAxis {
		return axes[name];
	}

	/**
	* Get the input action present in the input map by its name
	* @param name The name of the input action
	* @return InputAction
	**/
	public inline function getAction(name: String): InputAction {
		return actions[name];
	}

	/**
	* Get the vector of the given input axis
	* @param name The name of the input axis
	* @return Vec4
	**/
	public inline function getVec(name: String): Vec4 {
		return axes[name].get();
	}

	/**
	* Check if the given input action is started
	* @param name The name of the input action
	* @return Bool
	**/
	public inline function isActionPressed(name: String): Bool {
		return actions[name].pressed();
	}

	/**
	* Check if the given input action is released
	* @param name The name of the target input action
	* @return Bool
	**/
	public inline function isActionReleased(name: String): Bool {
		return actions[name].released();
	}
}

class InputAction {
	static var components = new Map<InputActionComponent, String>();

	final parent: InputMap;
	public final index: Int;
	public final deadzone: FastFloat;
	public final pressure: FastFloat;

	public function new(parent: InputMap, index: Int, pressure: FastFloat, deadzone: FastFloat) {
		this.parent = parent;
		this.index = index;
		this.pressure = pressure;
		this.deadzone = deadzone;
	}

	/**
	* Add a keyboard input component
	* @param tag The input component tag
	* @param key The key that should be started or released
	* @param modifiers The keys that should be down before activate the main key
	* @return Void
	**/
	public function addKeyboardComponent(tag: String, key: String, ?modifiers): Void {
		var mod = modifiers == null ? new Array<String>() : modifiers;
		addCustomComponent(tag, new KeyboardActionComponent(this, key, mod));
	}

	/**
	* Add a mouse input component
	* @param tag The input component tag
	* @param button The button that should be started or released
	* @param modifiers The buttons that should be down before activate the main key
	* @return Void
	**/
	public function addMouseComponent(tag: String, button: String, ?modifiers): Void {
		var mod = modifiers == null ? new Array<String>() : modifiers;
		addCustomComponent(tag, new MouseActionComponent(this, button, mod));
	}

	/**
	* Add a gamepad input component
	* @param tag The input component tag
	* @param button The button that should be started or released
	* @param modifiers The buttons that should be down before activate the main key
	* @return Void
	**/
	public function addGamepadComponent(tag: String, button: String, ?modifiers): Void {
		var mod = modifiers == null ? new Array<String>() : modifiers;
		addCustomComponent(tag, new GamepadActionComponent(this, button, mod));
	}

	/**
	* Add a custom input component
	* @param tag The input component tag
	* @param component The constructed input component
	* @return Void
	**/
	public function addCustomComponent(tag: String, component: InputActionComponent): Void {
		components[component] = tag;
	}

	/**
	* Remove an input component
	* @param component The component to be removed
	* @return Void
	**/
	public function removeComponent(component: InputActionComponent): Void {
		components.remove(component);
	}

	public function pressed(): Bool {
		for (component => tag in components) {
			if (tag == parent.currentTag) {
				if (component.started()) return true;
			}
		}
		return false;
	}

	public function released(): Bool {
		for (component => tag in components) {
			if (tag == parent.currentTag) {
				if (component.released()) return true;
			}
		}
		return false;
	}
}

class InputActionComponent {
	var parent: InputAction;
	var key: String;
	var modifiers: Array<String>;

	public function new(parent: InputAction, key: String, modifiers: Array<String>): Void {
		this.key = key;
		this.modifiers = modifiers;
		this.parent = parent;
	}

	public function started(): Bool {
		return false;
	}

	public function released(): Bool {
		return false;
	}
}

class KeyboardActionComponent extends InputActionComponent {

	final keyboard = Input.getKeyboard();

	public function new(parent: InputAction, key: String, modifiers: Array<String>): Void {
		super(parent, key, modifiers);
		this.parent = parent;
		this.key = key;
		this.modifiers = modifiers;
	}

	public inline override function started(): Bool {
		if (keyboard.started(key)) {
			for (m in modifiers) {
				if (!keyboard.down(m)) return false;
			}
			return true;
		}
		return false;
	}

	public inline override function released(): Bool {
		if (keyboard.released(key)) {
			for (m in modifiers) {
				if (!keyboard.down(m)) return false;
			}
			return true;
		}
		return false;
	}
}

class MouseActionComponent extends InputActionComponent {

	final mouse = Input.getMouse();

	public function new(parent: InputAction, key: String, modifiers: Array<String>): Void {
		super(parent, key, modifiers);
		this.parent = parent;
		this.key = key;
		this.modifiers = modifiers;
	}

	public override function started(): Bool {
		if (mouse.started(key)) {
			for (m in modifiers) {
				if (!mouse.down(m)) return false;
			}
			return true;
		}
		return false;
	}

	public override function released(): Bool {
		if (mouse.released(key)) {
			for (m in modifiers) {
				if (!mouse.down(m)) return false;
			}
			return true;
		}
		return false;
	}
}

class GamepadActionComponent extends InputActionComponent {

	final gamepad: Gamepad;

	public function new(parent: InputAction, key: String, modifiers: Array<String>) {
		super(parent, key, modifiers);
		this.parent = parent;
		this.key = key;
		this.modifiers = modifiers;
		gamepad = Input.getGamepad(parent.index);
	}

	public inline override function started(): Bool {
		if (gamepad.started(key)) {
			for (m in modifiers) {
				if (gamepad.down(m) <= parent.pressure) return false;
			}
			return true;
		}
		return false;
	}

	public inline override function released(): Bool {
		if (gamepad.released(key)) {
			for (m in modifiers) {
				if (gamepad.down(m) <= parent.pressure) return false;
			}
			return true;
		}
		return false;
	}
}

class InputAxis {
	static var componentsX = new Map<InputAxisComponent, String>();
	static var scaleX = 1.0;

	static var componentsY = new Map<InputAxisComponent, String>();
	static var scaleY = 1.0;

	static var normalize = false;
	static var vec = new Vec4();

	final parent: InputMap;
	public final index: Int;
	public final deadzone: FastFloat;
	public final pressure: FastFloat;

	public function new(parent: InputMap, index: Int, pressure: FastFloat, deadzone: FastFloat) {
		this.parent = parent;
		this.index = index;
		this.pressure = pressure;
		this.deadzone = deadzone;
	}

	/**
	* Add a keyboard input component
	* @param position The position that the added input component will be in the returned vector ("x" or "y")
	* @param tag The input component tag
	* @param positiveKey The key that when pressed will sum +1
	* @param negativeKey The key that when pressed will sum -1
	* @return Void
	**/
	public function addKeyboardComponent(position: String, tag: String, positiveKey: String, ?negativeKey: String): Void {
		var n = negativeKey == null ? "" : negativeKey;
		addCustomComponent(position, tag, new KeyboardAxisComponent(this, positiveKey, negativeKey));
	}

	/**
	* Add a mouse input component
	* @param position The position that the added input component will be in the returned vector ("x" or "y")
	* @param tag The input component tag
	* @param positiveButton The key that when pressed will sum +1
	* @param negativeButton The key that when pressed will sum -1
	* @return Void
	**/
	public function addMouseComponent(position: String, tag: String, positiveButton: String, ?negativeButton: String): Void {
		var n = negativeButton == null ? "" : negativeButton;
		addCustomComponent(position, tag, new MouseAxisComponent(this, positiveButton, negativeButton));
	}

	/**
	* Add a gamepad input component
	* @param position The position that the added input component will be in the returned vector ("x" or "y")
	* @param tag The input component tag
	* @param positiveButton The key that when pressed will sum +1
	* @param negativeButton The key that when pressed will sum -1
	* @return Void
	**/
	public function addGamepadComponent(position: String, tag: String, positiveButton: String, ?negativeButton: String): Void {
		var n = negativeButton == null ? "" : negativeButton;
		addCustomComponent(position, tag, new GamepadAxisComponent(this, positiveButton, negativeButton));
	}

	/**
	* Add a custom input component
	* @param tag The input component tag
	* @param component The constructed input component
	* @return Void
	**/
	public function addCustomComponent(position: String, tag: String, component: InputAxisComponent): Void {
		switch (position) {
			case "x": componentsX[component] = tag;
			case "y": componentsY[component] = tag;
		}
	}

	/**
	* Remove an input component
	* @param component The component to be removed
	* @return Void
	**/
	public function removeComponent(position: String, component: InputAxisComponent): Void {
		switch (position) {
			case "x": componentsX.remove(component);
			case "y": componentsY.remove(component);
		}
	}

	/**
	* Set the scale of the returned vector
	* @param x The scale of the components in the position x
	* @param y The scale of the components in the positon y
	* @return Void
	**/
	public function setScale(x: FastFloat, y: FastFloat): Void {
		scaleX = x;
		scaleY = y;
	}

	/**
	* Enable the returned vector normalization
	* @return Void
	**/
	public function enableNormalize(): Void {
		normalize = true;
	}

	/**
	* Disable the returned vector normalization
	* @return Void
	**/
	public function disableNormalize(): Void {
		normalize = false;
	}

	/**
	* Get the input axis vector
	* @return Void
	**/
	public inline function get(): Vec4 {
		vec.set(0, 0, 0);

		for (component => tag in componentsX) {
			if (tag == parent.currentTag) if (component.get() != 0.0) vec.x += component.get();
		}

		for (component => tag in componentsY) {
			if (tag == parent.currentTag) if (component.get() != 0.0) vec.y += component.get();
		}

		if (normalize) vec.normalize();

		vec.x *= scaleX;
		vec.y *= scaleY;

		return vec;
	}
}

class InputAxisComponent {
	var parent: InputAxis;
	var positiveKey: String;
	var negativeKey: String;
	var scale: FastFloat;

	public function new(parent: InputAxis, positiveKey: String, negativeKey: String): Void {
		this.parent = parent;
		this.positiveKey = positiveKey;
		this.negativeKey = negativeKey;
	}

	public function get(): FastFloat {
		return 0.0;
	}
}

class KeyboardAxisComponent extends InputAxisComponent {
	final keyboard = Input.getKeyboard();

	public function new(parent: InputAxis, positiveKey: String, negativeKey: String): Void {
		super(parent, positiveKey, negativeKey);
		this.parent = parent;
		this.positiveKey = positiveKey;
		this.negativeKey = negativeKey;
	}

	public inline override function get(): FastFloat {
		scale = 0.0;
		if (keyboard.down(positiveKey)) scale++;
		if (keyboard.down(negativeKey)) scale--;
		return scale;
	}
}

class MouseAxisComponent extends InputAxisComponent {
	final mouse = Input.getMouse();

	public function new(parent: InputAxis, positiveKey: String, negativeKey: String): Void {
		super(parent, positiveKey, negativeKey);
		this.parent = parent;
		this.positiveKey = positiveKey;
		this.negativeKey = negativeKey;
	}

	public inline override function get(): FastFloat {
		scale = 0.0;
		var movX = mouse.movementX;
		var movY = mouse.movementY;
		var wheelMov = mouse.wheelDelta;

		switch (positiveKey) {
			case "moved x": if (movX > parent.deadzone) scale++;
			case "movement x": if (movX > parent.deadzone) return movX - parent.deadzone;
			case "moved y":	if (movY > parent.deadzone) scale++;
			case "movement y": if (movY > parent.deadzone) return movY - parent.deadzone;
			case "wheel moved": if (wheelMov > parent.deadzone) scale ++;
			case "wheel movement": if (wheelMov > parent.deadzone) return wheelMov - parent.deadzone;
			default: if (mouse.down(positiveKey)) scale++;
		}
		switch (negativeKey) {
			case "moved x": if (movX < -parent.deadzone) scale--;
			case "movement x": if (movX < -parent.deadzone) return movX + parent.deadzone;
			case "moved y": if (movY < -parent.deadzone) scale--;
			case "movement y": if (movY < -parent.deadzone) return movY + parent.deadzone;
			case "wheel moved": if (wheelMov > parent.deadzone) scale --;
			case "wheel movement": if (wheelMov > parent.deadzone) return wheelMov + parent.deadzone;
			default: if (mouse.down(negativeKey)) scale--;
		}
		return scale;
	}
}

class GamepadAxisComponent extends InputAxisComponent {
	final gamepad: Gamepad;

	public function new(parent: InputAxis, positiveKey: String, negativeKey: String): Void {
		super(parent, positiveKey, negativeKey);
		this.parent = parent;
		this.positiveKey = positiveKey;
		this.negativeKey = negativeKey;
		gamepad = Input.getGamepad(parent.index);
	}

	public inline override function get(): FastFloat {
		scale = 0.0;
		var rightMovX = gamepad.rightStick.movementX;
		var rightMovY = gamepad.rightStick.movementY;
		var leftMovX = gamepad.leftStick.movementX;
		var leftMovY = gamepad.leftStick.movementY;

		// Avoid division by zero
		var rightTrigger = gamepad.down("r2") > 0.0 ? (gamepad.down("r2") - parent.pressure) / (1 - parent.pressure) : 0.0;
		var leftTrigger = gamepad.down("l2") > 0.0 ? (gamepad.down("r2") - parent.pressure) / (1 - parent.pressure) : 0.0;

		switch (positiveKey) {
			case "right stick moved x": if (rightMovX > parent.deadzone) scale++;
			case "right stick movement x": if (rightMovX > parent.deadzone) return rightMovX - parent.deadzone;
			case "right stick moved y": if (rightMovY > parent.deadzone) scale++;
			case "right stick movement y": if (rightMovY > parent.deadzone) return rightMovY - parent.deadzone;
			case "left stick moved x": if (leftMovX > parent.deadzone) scale++;
			case "left stick movement x": if (leftMovX > parent.deadzone) return leftMovX - parent.deadzone;
			case "left stick moved y": if (leftMovY > parent.deadzone) scale++;
			case "left stick movement y": if (leftMovY > parent.deadzone) return leftMovY - parent.deadzone;
			case "right trigger": scale += rightTrigger;
			case "left trigger": scale += leftTrigger;
			default: if (gamepad.down(positiveKey) > parent.pressure) scale++;
		}

		switch (negativeKey) {
			case "right stick moved x": if (rightMovX < -parent.deadzone) scale--;
			case "right stick movement x": if (rightMovX < -parent.deadzone) return rightMovX + parent.deadzone;
			case "right stick moved y": if (rightMovY < -parent.deadzone) scale--;
			case "right stick movement y": if (rightMovY < -parent.deadzone) return rightMovY + parent.deadzone;
			case "left stick moved x": if (leftMovX < -parent.deadzone) scale--;
			case "left stick movement x": if (leftMovX < -parent.deadzone) return leftMovX + parent.deadzone;
			case "left stick moved y": if (leftMovY < -parent.deadzone) scale--;
			case "left stick movement y": if (leftMovY < -parent.deadzone) return leftMovY + parent.deadzone;
			case "right trigger": scale -= rightTrigger;
			case "left trigger": scale -= leftTrigger;
			default: if (gamepad.down(negativeKey) < -parent.pressure) scale--;
		}

		return scale;
	}
}
