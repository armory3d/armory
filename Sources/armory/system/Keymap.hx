package armory.system;

class Keymap {
	// Primitive key mapping
	public static inline var forward = 'w';
	public static inline var backward = 's';
	public static inline var left = 'a';
	public static inline var right = 'd';
	public static inline var jump = ' ';
	public static inline var fire = 'f';
	public static inline var brake = ' ';
	public static inline var up = 'e';
	public static inline var down = 'q';

	public static var fast = kha.Key.SHIFT;
	public static var slow = kha.Key.ALT;

	public function new() { }
}
