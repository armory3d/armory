package;

// Kha
import kha.input.KeyCode;

// Zui
import armory.ui.Canvas;

// Editor
import arm2d.Editor;

class Main {

	public static var prefs:TPrefs = null;
	public static var cwd = ""; // Canvas path
	public static var inst:Editor;

	public static function main() {

		var w = 1600;
		var h = 900;
		if (kha.Display.primary != null) { // TODO: no Display.primary returned on Linux
			if (w > kha.Display.primary.width) w = kha.Display.primary.width;
			if (h > kha.Display.primary.height - 30) h = kha.Display.primary.height - 30;
		}
		kha.System.start({ title : "Armory2D", width : w, height : h, framebuffer : {samplesPerPixel : 2}}, initialized);
	}

	static function initialized(window:kha.Window) {

		prefs = {
			path: "",
			scaleFactor: 1.0,
			keyMap: {
				selectMouseButton: "Left",
				grabKey: KeyCode.G,
				rotateKey: KeyCode.R,
				sizeKey: KeyCode.S,
				slowMovement: KeyCode.Shift,
				gridInvert: KeyCode.Control,
				gridInvertRelative: KeyCode.Alt,
			}
		};

		#if kha_krom

		var c = Krom.getArgCount();
		// ./krom . . canvas_path scale_factor
		if (c > 4) prefs.path = Krom.getArg(3);
		if (c > 5) prefs.scaleFactor = Std.parseFloat(Krom.getArg(4));

		var ar = prefs.path.split("/");
		ar.pop();
		cwd = ar.join("/");

		if(cwd != ""){
			var path = kha.System.systemId == "Windows" ? StringTools.replace(prefs.path, "/", "\\") : prefs.path;
			kha.Assets.loadBlobFromPath(path, function(cblob:kha.Blob) {
				inst = new Editor(Canvas.parseCanvasFromBlob(cblob));
			});
		}
		else {
			prefs.path = Krom.getFilesLocation();
		#end
			var raw:TCanvas = { name: "untitled", x: 0, y: 0, width: 1280, height: 720, theme: "Default Light", visible: true, elements: [], assets: [] };
			inst = new Editor(raw);
		#if kha_krom
		}
		#end
	}

	static function loadDefaultKeyMap() {
		Main.prefs.keyMap.grabKey = KeyCode.G;
		Main.prefs.keyMap.rotateKey = KeyCode.R;
		Main.prefs.keyMap.sizeKey = KeyCode.S;
		Main.prefs.keyMap.slowMovement = KeyCode.Shift;
		Main.prefs.keyMap.gridInvert = KeyCode.Control;
		Main.prefs.keyMap.gridInvertRelative = KeyCode.Alt;
	}
}

typedef TPrefs = {
	var path:String;
	var scaleFactor:Float;
	var keyMap:TKeyMap;
	@:optional var window_vsync:Bool;
}

typedef TKeyMap = {
	var selectMouseButton:String;
	var grabKey:Int;
	var rotateKey:Int;
	var sizeKey:Int;
	var slowMovement:Int; // Key which slows down manipulation
	var gridInvert:Int; // Toggles the grid setting during element manipulation
	var gridInvertRelative:Int; // Make the grid relative to the selected element
}
