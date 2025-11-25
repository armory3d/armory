package iron.system;

import kha.input.KeyCode;
#if arm_target_n64
import iron.n64.N64Bridge;
#end

class Input {

	public static var occupied = false;
	static var mouse: Mouse = null;
	static var pen: Pen = null;
	static var keyboard: Keyboard = null;
	static var gamepads: Array<Gamepad> = [];
	static var sensor: Sensor = null;
	static var registered = false;
	public static var virtualButtons: Map<String, VirtualButton> = null; // Button name

	public static function reset() {
		occupied = false;
		if (mouse != null) mouse.reset();
		if (pen != null) pen.reset();
		if (keyboard != null) keyboard.reset();
		for (gamepad in gamepads) gamepad.reset();
	}

	public static function endFrame() {
		if (mouse != null) mouse.endFrame();
		if (pen != null) pen.endFrame();
		if (keyboard != null) keyboard.endFrame();
		for (gamepad in gamepads) gamepad.endFrame();

		if (virtualButtons != null) {
			for (vb in virtualButtons) vb.started = vb.released = false;
		}
	}

	public static function getMouse(): Mouse {
		if (!registered) register();
		if (mouse == null) mouse = new Mouse();
		return mouse;
	}

	public static function getPen(): Pen {
		if (!registered) register();
		if (pen == null) pen = new Pen();
		return pen;
	}

	public static function getSurface(): Surface {
		if (!registered) register();
		// Map to mouse for now..
		return getMouse();
	}

	/**
	  Get the Keyboard object. If it is not registered yet then register a new Keyboard.
	**/
	public static function getKeyboard(): Keyboard {
		if (!registered) register();
		if (keyboard == null) keyboard = new Keyboard();
		return keyboard;
	}

	public static function getGamepad(i = 0): Gamepad {
		if (i >= 4) return null;
		if (!registered) register();
		while (gamepads.length <= i) gamepads.push(new Gamepad(gamepads.length));
		return gamepads[i].connected ? gamepads[i] : null;
	}

	public static function getSensor(): Sensor {
		if (!registered) register();
		if (sensor == null) sensor = new Sensor();
		return sensor;
	}

	public static function getVirtualButton(virtual: String): VirtualButton {
		if (!registered) register();
		if (virtualButtons == null) return null;
		return virtualButtons.get(virtual);
	}

	static inline function register() {
		registered = true;
		App.notifyOnEndFrame(endFrame);
		App.notifyOnReset(reset);
		// Reset mouse delta on foreground
		kha.System.notifyOnApplicationState(function() { getMouse().reset(); }, null, null, null, null);
	}
}

class VirtualButton {
	public var started = false;
	public var released = false;
	public var down = false;
	public function new() {}
}

class VirtualInput {
	var virtualButtons: Map<String, VirtualButton> = null; // Button id

	public function setVirtual(virtual: String, button: String) {
		if (Input.virtualButtons == null) Input.virtualButtons = new Map<String, VirtualButton>();

		var vb = Input.virtualButtons.get(virtual);
		if (vb == null) {
			vb = new VirtualButton();
			Input.virtualButtons.set(virtual, vb);
		}

		if (virtualButtons == null) virtualButtons = new Map<String, VirtualButton>();
		virtualButtons.set(button, vb);
	}

	function downVirtual(button: String) {
		if (virtualButtons != null) {
			var vb = virtualButtons.get(button);
			if (vb != null) {
				vb.down = true;
				vb.started = true;
			}
		}
	}

	function upVirtual(button: String) {
		if (virtualButtons != null) {
			var vb = virtualButtons.get(button);
			if (vb != null) {
				vb.down = false;
				vb.released = true;
			}
		}
	}
}

typedef Surface = Mouse;

class Mouse extends VirtualInput {

	public static var buttons = ["left", "right", "middle", "side1", "side2"];
	var buttonsDown = [false, false, false, false, false];
	var buttonsStarted = [false, false, false, false, false];
	var buttonsReleased = [false, false, false, false, false];

	public var x(default, null) = 0.0;
	public var y(default, null) = 0.0;
	public var viewX(get, null) = 0.0;
	public var viewY(get, null) = 0.0;
	public var moved(default, null) = false;
	public var movementX(default, null) = 0.0;
	public var movementY(default, null) = 0.0;
	public var wheelDelta(default, null) = 0;
	public var locked(default, null) = false;
	public var hidden(default, null) = false;
	public var lastX = -1.0;
	public var lastY = -1.0;

	public function new() {
		kha.input.Mouse.get().notify(downListener, upListener, moveListener, wheelListener);
		#if (kha_android || kha_ios)
		if (kha.input.Surface.get() != null) kha.input.Surface.get().notify(onTouchDown, onTouchUp, onTouchMove);
		#end
	}

	public function endFrame() {
		buttonsStarted[0] = buttonsStarted[1] = buttonsStarted[2] = buttonsStarted[3] = buttonsStarted[4] = false;
		buttonsReleased[0] = buttonsReleased[1] = buttonsReleased[2] = buttonsReleased[3] = buttonsReleased[4] = false;
		moved = false;
		movementX = 0;
		movementY = 0;
		wheelDelta = 0;
	}

	public function reset() {
		buttonsDown[0] = buttonsDown[1] = buttonsDown[2] = buttonsDown[3] = buttonsDown[4] = false;
		endFrame();
	}

	function buttonIndex(button: String): Int {
		for (i in 0...buttons.length) if (buttons[i] == button) return i;
		return 0;
	}

	public function down(button = "left"): Bool {
		return buttonsDown[buttonIndex(button)];
	}

	public function started(button = "left"): Bool {
		return buttonsStarted[buttonIndex(button)];
	}

	public function released(button = "left"): Bool {
		return buttonsReleased[buttonIndex(button)];
	}

	public function lock() {
		if (kha.input.Mouse.get().canLock()) {
			kha.input.Mouse.get().lock();
			locked = true;
			hidden = true;
		}
	}
	public function unlock() {
		if (kha.input.Mouse.get().canLock()) {
			kha.input.Mouse.get().unlock();
			locked = false;
			hidden = false;
		}
	}

	public function hide() {
		kha.input.Mouse.get().hideSystemCursor();
		hidden = true;
	}

	public function show() {
		kha.input.Mouse.get().showSystemCursor();
		hidden = false;
	}

	function downListener(index: Int, x: Int, y: Int) {
		if (Input.getPen().inUse) return;

		buttonsDown[index] = true;
		buttonsStarted[index] = true;
		this.x = x;
		this.y = y;
		#if (kha_android || kha_ios || kha_webgl) // For movement delta using touch
		if (index == 0) {
			lastX = x;
			lastY = y;
		}
		#end

		downVirtual(buttons[index]);
	}

	function upListener(index: Int, x: Int, y: Int) {
		if (Input.getPen().inUse) return;

		buttonsDown[index] = false;
		buttonsReleased[index] = true;
		this.x = x;
		this.y = y;

		upVirtual(buttons[index]);
	}

	function moveListener(x: Int, y: Int, movementX: Int, movementY: Int) {
		if (lastX == -1.0 && lastY == -1.0) { // First frame init
			lastX = x;
			lastY = y;
		}
		if (locked) {
			// Can be called multiple times per frame
			this.movementX += movementX;
			this.movementY += movementY;
		}
		else {
			this.movementX += x - lastX;
			this.movementY += y - lastY;
		}
		lastX = x;
		lastY = y;
		this.x = x;
		this.y = y;
		moved = true;
	}

	function wheelListener(delta: Int) {
		wheelDelta = delta;
	}

	#if (kha_android || kha_ios)
	public function onTouchDown(index: Int, x: Int, y: Int) {
		if (index == 1) { // Two fingers down - right mouse button
			buttonsDown[0] = false;
			downListener(1, Std.int(this.x), Std.int(this.y));
			pinchStarted = true;
			pinchTotal = 0.0;
			pinchDistance = 0.0;
		}
		else if (index == 2) { // Three fingers down - middle mouse button
			buttonsDown[1] = false;
			downListener(2, Std.int(this.x), Std.int(this.y));
		}
	}

	public function onTouchUp(index: Int, x: Int, y: Int) {
		if (index == 1) upListener(1, Std.int(this.x), Std.int(this.y));
		else if (index == 2) upListener(2, Std.int(this.x), Std.int(this.y));
	}

	var pinchDistance = 0.0;
	var pinchTotal = 0.0;
	var pinchStarted = false;

	public function onTouchMove(index: Int, x: Int, y: Int) {
		// Pinch to zoom - mouse wheel
		if (index == 1) {
			var lastDistance = pinchDistance;
			var dx = this.x - x;
			var dy = this.y - y;
			pinchDistance = Math.sqrt(dx * dx + dy * dy);
			pinchTotal += lastDistance != 0 ? lastDistance - pinchDistance : 0;
			if (!pinchStarted) {
				wheelDelta = Std.int(pinchTotal / 10);
				if (wheelDelta != 0) {
					pinchTotal = 0.0;
				}
			}
			pinchStarted = false;
		}
	}
	#end

	inline function get_viewX(): Float {
		return x - iron.App.x();
	}

	inline function get_viewY(): Float {
		return y - iron.App.y();
	}
}

class Pen extends VirtualInput {

	static var buttons = ["tip"];
	var buttonsDown = [false];
	var buttonsStarted = [false];
	var buttonsReleased = [false];

	public var x(default, null) = 0.0;
	public var y(default, null) = 0.0;
	public var viewX(get, null) = 0.0;
	public var viewY(get, null) = 0.0;
	public var moved(default, null) = false;
	public var movementX(default, null) = 0.0;
	public var movementY(default, null) = 0.0;
	public var pressure(default, null) = 0.0;
	public var connected = false;
	public var inUse = false;
	var lastX = -1.0;
	var lastY = -1.0;

	public function new() {
		var pen = kha.input.Pen.get();
		if (pen != null) pen.notify(downListener, upListener, moveListener);
	}

	public function endFrame() {
		buttonsStarted[0] = false;
		buttonsReleased[0] = false;
		moved = false;
		movementX = 0;
		movementY = 0;
		inUse = false;
	}

	public function reset() {
		buttonsDown[0] = false;
		endFrame();
	}

	function buttonIndex(button: String): Int {
		return 0;
	}

	public function down(button = "tip"): Bool {
		return buttonsDown[buttonIndex(button)];
	}

	public function started(button = "tip"): Bool {
		return buttonsStarted[buttonIndex(button)];
	}

	public function released(button = "tip"): Bool {
		return buttonsReleased[buttonIndex(button)];
	}

	function downListener(x: Int, y: Int, pressure: Float) {
		buttonsDown[0] = true;
		buttonsStarted[0] = true;
		this.x = x;
		this.y = y;
		this.pressure = pressure;

		#if (!kha_android && !kha_ios)
		@:privateAccess Input.getMouse().downListener(0, x, y);
		#end
	}

	function upListener(x: Int, y: Int, pressure: Float) {
		#if (!kha_android && !kha_ios)
		if (buttonsStarted[0]) { buttonsStarted[0] = false; inUse = true; return; }
		#end

		buttonsDown[0] = false;
		buttonsReleased[0] = true;
		this.x = x;
		this.y = y;
		this.pressure = pressure;

		#if (!kha_android && !kha_ios)
		@:privateAccess Input.getMouse().upListener(0, x, y);
		inUse = true; // On pen release, additional mouse down & up events are fired at once - filter those out
		#end
	}

	function moveListener(x: Int, y: Int, pressure: Float) {
		if (lastX == -1.0 && lastY == -1.0) { // First frame init
			lastX = x;
			lastY = y;
		}
		this.movementX = x - lastX;
		this.movementY = y - lastY;
		lastX = x;
		lastY = y;
		this.x = x;
		this.y = y;
		moved = true;
		this.pressure = pressure;
		connected = true;
	}

	inline function get_viewX(): Float {
		return x - iron.App.x();
	}

	inline function get_viewY(): Float {
		return y - iron.App.y();
	}
}

class Keyboard extends VirtualInput {

	public static var keys = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "space", "backspace", "tab", "enter", "shift", "control", "alt", "capslock", "win", "escape", "delete", "up", "down", "left", "right", "back", ",", ".", ":", ";", "<", "=", ">", "?", "!", '"', "#", "$", "%", "&", "_", "(", ")", "*", "|", "{", "}", "[", "]", "~", "`", "/", "\\", "@", "+", "-", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12"];
	var keysDown = new Map<String, Bool>();
	var keysStarted = new Map<String, Bool>();
	var keysReleased = new Map<String, Bool>();
	var keysFrame: Array<String> = [];
	var repeatKey = false;
	var repeatTime = 0.0;

	public function new() {
		reset();
		kha.input.Keyboard.get().notify(downListener, upListener, pressListener);
	}

	public function endFrame() {
		if (keysFrame.length > 0) {
			for (s in keysFrame) {
				keysStarted.set(s, false);
				keysReleased.set(s, false);
			}
			keysFrame.splice(0, keysFrame.length);
		}

		if (kha.Scheduler.time() - repeatTime > 0.05) {
			repeatTime = kha.Scheduler.time();
			repeatKey = true;
		}
		else repeatKey = false;
	}

	public function reset() {
		// Use Map for now..
		for (s in keys) {
			keysDown.set(s, false);
			keysStarted.set(s, false);
			keysReleased.set(s, false);
		}
		endFrame();
	}

	/**
		Check if a key is currently pressed.
		@param	key A String representing the physical keyboard key to check.
		@return	Bool. Returns true or false depending on the keyboard state.
	**/
	public function down(key: String): Bool {
		return keysDown.get(key);
	}

	/**
		Check if a key has started being pressed down. Will only be run once until the key is released and pressed again.
		@param	key A String representing the physical keyboard key to check.
		@return	Bool. Returns true or false depending on the keyboard state.
	**/
	public function started(key: String): Bool {
		return keysStarted.get(key);
	}

	/**
		Check if a key has been released from being pressed down. Will only be run once until the key is pressed again and release again.
		@param	key A String representing the physical keyboard key to check.
		@return	Bool. Returns true or false depending on the keyboard state.
	**/
	public function released(key: String): Bool {
		return keysReleased.get(key);
	}

	/**
		Check every repeat period if a key is currently pressed.
		@param	key A String representing the physical keyboard key to check.
		@return	Bool. Returns true or false depending on the keyboard state.
	**/
	public function repeat(key: String): Bool {
		return keysStarted.get(key) || (repeatKey && keysDown.get(key));
	}

	public static function keyCode(key: KeyCode): String {
		return switch(key) {
			case KeyCode.Space: "space";
			case KeyCode.Backspace: "backspace";
			case KeyCode.Tab: "tab";
			case KeyCode.Return: "enter";
			case KeyCode.Shift: "shift";
			case KeyCode.Control: "control";
			#if kha_darwin
			case KeyCode.Meta: "control";
			#end
			case KeyCode.Alt: "alt";
			case KeyCode.CapsLock: "capslock";
			case KeyCode.Win: "win";
			case KeyCode.Escape: "escape";
			case KeyCode.Delete: "delete";
			case KeyCode.Up: "up";
			case KeyCode.Down: "down";
			case KeyCode.Left: "left";
			case KeyCode.Right: "right";
			case KeyCode.Back: "back";
			case KeyCode.Comma: ",";
			case KeyCode.Period: ".";
			case KeyCode.Colon: ":";
			case KeyCode.Semicolon: ";";
			case KeyCode.LessThan: "<";
			case KeyCode.Equals: "=";
			case KeyCode.GreaterThan: ">";
			case KeyCode.QuestionMark: "?";
			case KeyCode.Exclamation: "!";
			case KeyCode.DoubleQuote: '"';
			case KeyCode.Hash: "#";
			case KeyCode.Dollar: "$";
			case KeyCode.Percent: "%";
			case KeyCode.Ampersand: "&";
			case KeyCode.Underscore: "_";
			case KeyCode.OpenParen: "(";
			case KeyCode.CloseParen: ")";
			case KeyCode.Asterisk: "*";
			case KeyCode.Pipe: "|";
			case KeyCode.OpenCurlyBracket: "{";
			case KeyCode.CloseCurlyBracket: "}";
			case KeyCode.OpenBracket: "[";
			case KeyCode.CloseBracket: "]";
			case KeyCode.Tilde: "~";
			case KeyCode.BackQuote: "`";
			case KeyCode.Slash: "/";
			case KeyCode.BackSlash: "\\";
			case KeyCode.At: "@";
			case KeyCode.Add: "+";
			case KeyCode.Plus: "+";
			case KeyCode.Subtract: "-";
			case KeyCode.HyphenMinus: "-";
			case KeyCode.Multiply: "*";
			case KeyCode.Divide: "/";
			case KeyCode.Decimal: ".";
			case KeyCode.Zero: "0";
			case KeyCode.Numpad0: "0";
			case KeyCode.One: "1";
			case KeyCode.Numpad1: "1";
			case KeyCode.Two: "2";
			case KeyCode.Numpad2: "2";
			case KeyCode.Three: "3";
			case KeyCode.Numpad3: "3";
			case KeyCode.Four: "4";
			case KeyCode.Numpad4: "4";
			case KeyCode.Five: "5";
			case KeyCode.Numpad5: "5";
			case KeyCode.Six: "6";
			case KeyCode.Numpad6: "6";
			case KeyCode.Seven: "7";
			case KeyCode.Numpad7: "7";
			case KeyCode.Eight: "8";
			case KeyCode.Numpad8: "8";
			case KeyCode.Nine: "9";
			case KeyCode.Numpad9: "9";
			case KeyCode.F1: "f1";
			case KeyCode.F2: "f2";
			case KeyCode.F3: "f3";
			case KeyCode.F4: "f4";
			case KeyCode.F5: "f5";
			case KeyCode.F6: "f6";
			case KeyCode.F7: "f7";
			case KeyCode.F8: "f8";
			case KeyCode.F9: "f9";
			case KeyCode.F10: "f10";
			case KeyCode.F11: "f11";
			case KeyCode.F12: "f12";
			default: String.fromCharCode(cast key).toLowerCase();
		}
	}

	function downListener(code: KeyCode) {
		var s = keyCode(code);
		keysFrame.push(s);
		keysStarted.set(s, true);
		keysDown.set(s, true);
		repeatTime = kha.Scheduler.time() + 0.4;

		#if kha_android_rmb // Detect right mouse button on Android..
		if (code == KeyCode.Back) {
			var m = Input.getMouse();
			@:privateAccess if (!m.buttonsDown[1]) m.downListener(1, Std.int(m.x), Std.int(m.y));
		}
		#end

		downVirtual(s);
	}

	function upListener(code: KeyCode) {
		var s = keyCode(code);
		keysFrame.push(s);
		keysReleased.set(s, true);
		keysDown.set(s, false);

		#if kha_android_rmb
		if (code == KeyCode.Back) {
			var m = Input.getMouse();
			@:privateAccess m.upListener(1, Std.int(m.x), Std.int(m.y));
		}
		#end

		upVirtual(s);
	}

	function pressListener(char: String) {}
}

class GamepadStick {
	public var x = 0.0;
	public var y = 0.0;
	public var lastX = 0.0;
	public var lastY = 0.0;
	public var moved = false;
	public var movementX = 0.0;
	public var movementY = 0.0;
	public function new() {}
}

class Gamepad extends VirtualInput {

	public static var buttonsPS = ["cross", "circle", "square", "triangle", "l1", "r1", "l2", "r2", "share", "options", "l3", "r3", "up", "down", "left", "right", "home", "touchpad"];
	public static var buttonsXBOX = ["a", "b", "x", "y", "l1", "r1", "l2", "r2", "share", "options", "l3", "r3", "up", "down", "left", "right", "home", "touchpad"];
	public static var buttons = buttonsPS;

	public var id(get, never): String;
	inline function get_id() return kha.input.Gamepad.get(num).id;

	var buttonsDown: Array<Float> = []; // Intensity 0 - 1
	var buttonsStarted: Array<Bool> = [];
	var buttonsReleased: Array<Bool> = [];

	var buttonsFrame: Array<Int> = [];

	public var leftStick = new GamepadStick();
	public var rightStick = new GamepadStick();

	public var connected = false;
	var num = 0;

	public function new(i: Int, virtual = false) {
		for (s in buttons) {
			buttonsDown.push(0.0);
			buttonsStarted.push(false);
			buttonsReleased.push(false);
		}
		num = i;
		reset();
		virtual ? connected = true : connect();
	}

	var connects = 0;
	function connect() {
		var gamepad = kha.input.Gamepad.get(num);
		if (gamepad == null) {
			// if (connects < 10) armory.system.Tween.timer(1, connect);
			// connects++;
			return;
		}
		connected = true;
		gamepad.notify(axisListener, buttonListener);
	}

	public function endFrame() {
		if (buttonsFrame.length > 0) {
			for (i in buttonsFrame) {
				buttonsStarted[i] = false;
				buttonsReleased[i] = false;
			}
			buttonsFrame.splice(0, buttonsFrame.length);
		}
		leftStick.moved = false;
		leftStick.movementX = 0;
		leftStick.movementY = 0;
		rightStick.moved = false;
		rightStick.movementX = 0;
		rightStick.movementY = 0;
	}

	public function reset() {
		for (i in 0...buttonsDown.length) {
			buttonsDown[i] = 0.0;
			buttonsStarted[i] = false;
			buttonsReleased[i] = false;
		}
		endFrame();
	}

	public static function keyCode(button: Int): String {
		return buttons[button];
	}

	function buttonIndex(button: String): Int {
		for (i in 0...buttons.length) if (buttons[i] == button) return i;
		return 0;
	}

	public function down(button: String): Float {
		#if arm_target_n64
		return N64Bridge.input.down(button);
		#end
		return buttonsDown[buttonIndex(button)];
	}

	public function started(button: String): Bool {
		#if arm_target_n64
		return N64Bridge.input.started(button);
		#end
		return buttonsStarted[buttonIndex(button)];
	}

	public function released(button: String): Bool {
		#if arm_target_n64
		return N64Bridge.input.released(button);
		#end
		return buttonsReleased[buttonIndex(button)];
	}

	function axisListener(axis: Int, value: Float) {
		var stick = axis <= 1 ? leftStick : rightStick;

		if (axis == 0 || axis == 2) { // X
			stick.lastX = stick.x;
			stick.x = value;
			stick.movementX = stick.x - stick.lastX;
		}
		else if (axis == 1 || axis == 3) { // Y
			stick.lastY = stick.y;
			stick.y = value;
			stick.movementY = stick.y - stick.lastY;
		}
		stick.moved = true;
	}

	function buttonListener(button: Int, value: Float) {
		buttonsFrame.push(button);

		buttonsDown[button] = value;
		if (value > 0) buttonsStarted[button] = true; // Will trigger L2/R2 multiple times..
		else buttonsReleased[button] = true;

		if (value == 0.0) upVirtual(buttons[button]);
		else if (value == 1.0) downVirtual(buttons[button]);
	}
}

class Sensor {

	public var x = 0.0;
	public var y = 0.0;
	public var z = 0.0;

	public function new() {
		kha.input.Sensor.get(kha.input.SensorType.Accelerometer).notify(listener);
	}

	function listener(x: Float, y: Float, z: Float) {
		this.x = x;
		this.y = y;
		this.z = z;
	}
}
