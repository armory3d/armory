package zui;

import zui.Zui;
import kha.input.KeyCode;

@:access(zui.Zui)
class Ext {

	public static function floatInput(ui: Zui, handle: Handle, label = "", align: Align = Left, precision = 1000.0): Float {
		handle.text = Std.string(Math.round(handle.value * precision) / precision);
		var text = ui.textInput(handle, label, align);
		handle.value = Std.parseFloat(text);
		return handle.value;
	}

	static function initPath(handle: Handle, systemId: String) {
		handle.text = systemId == "Windows" ? "C:\\Users" : "/";
		// %HOMEDRIVE% + %HomePath%
		// ~
	}

	public static var dataPath = "";
	static var lastPath = "";
	public static function fileBrowser(ui: Zui, handle: Handle, foldersOnly = false): String {
		var sep = "/";

		#if kha_krom

		var cmd = "ls ";
		var systemId = kha.System.systemId;
		if (systemId == "Windows") {
			cmd = "dir /b ";
			if (foldersOnly) cmd += "/ad ";
			sep = "\\";
			handle.text = StringTools.replace(handle.text, "\\\\", "\\");
			handle.text = StringTools.replace(handle.text, "\r", "");
		}
		if (handle.text == "") initPath(handle, systemId);

		var save = Krom.getFilesLocation() + sep + dataPath + "dir.txt";
		if (handle.text != lastPath) Krom.sysCommand(cmd + '"' + handle.text + '"' + " > " + '"' + save + '"');
		lastPath = handle.text;
		var str = haxe.io.Bytes.ofData(Krom.loadBlob(save)).toString();
		var files = str.split("\n");

		#elseif kha_kore

		if (handle.text == "") initPath(handle, kha.System.systemId);
		var files = sys.FileSystem.isDirectory(handle.text) ? sys.FileSystem.readDirectory(handle.text) : [];

		#elseif kha_webgl

		var files: Array<String> = [];

		var userAgent = untyped navigator.userAgent.toLowerCase();
		if (userAgent.indexOf(" electron/") > -1) {
			if (handle.text == "") {
				var pp = untyped window.process.platform;
				var systemId = pp == "win32" ? "Windows" : (pp == "darwin" ? "OSX" : "Linux");
				initPath(handle, systemId);
			}
			try {
				files = untyped require("fs").readdirSync(handle.text);
			}
			catch (e: Dynamic) {
				// Non-directory item selected
			}
		}

		#else

		var files: Array<String> = [];

		#end

		// Up directory
		var i1 = handle.text.indexOf("/");
		var i2 = handle.text.indexOf("\\");
		var nested =
			(i1 > -1 && handle.text.length - 1 > i1) ||
			(i2 > -1 && handle.text.length - 1 > i2);
		handle.changed = false;
		if (nested && ui.button("..", Align.Left)) {
			handle.changed = ui.changed = true;
			handle.text = handle.text.substring(0, handle.text.lastIndexOf(sep));
			// Drive root
			if (handle.text.length == 2 && handle.text.charAt(1) == ":") handle.text += sep;
		}

		// Directory contents
		for (f in files) {
			if (f == "" || f.charAt(0) == ".") continue; // Skip hidden
			if (ui.button(f, Align.Left)) {
				handle.changed = ui.changed = true;
				if (handle.text.charAt(handle.text.length - 1) != sep) handle.text += sep;
				handle.text += f;
			}
		}

		return handle.text;
	}

	public static function inlineRadio(ui: Zui, handle: Handle, texts: Array<String>, align: Align = Left): Int {
		if (!ui.isVisible(ui.ELEMENT_H())) {
			ui.endElement();
			return handle.position;
		}
		var step = ui._w / texts.length;
		var hovered = -1;
		if (ui.getHover()) {
			var ix = Std.int(ui.inputX - ui._x - ui._windowX);
			for (i in 0...texts.length) {
				if (ix < i * step + step) {
					hovered = i;
					break;
				}
			}
		}
		if (ui.getReleased()) {
			handle.position = hovered;
			handle.changed = ui.changed = true;
		}
		else handle.changed = false;

		for (i in 0...texts.length) {
			if (handle.position == i) {
				ui.g.color = ui.t.ACCENT_HOVER_COL;
				if (!ui.enabled) ui.fadeColor();
				ui.g.fillRect(ui._x + step * i, ui._y + ui.buttonOffsetY, step, ui.BUTTON_H());
			}
			else if (hovered == i) {
				ui.g.color = ui.t.ACCENT_COL;
				if (!ui.enabled) ui.fadeColor();
				ui.g.drawRect(ui._x + step * i, ui._y + ui.buttonOffsetY, step, ui.BUTTON_H());
			}
			ui.g.color = ui.t.TEXT_COL; // Text
			ui._x += step * i;
			var _w = ui._w;
			ui._w = Std.int(step);
			ui.drawString(ui.g, texts[i], null, 0, align);
			ui._x -= step * i;
			ui._w = _w;
		}
		ui.endElement();
		return handle.position;
	}

	static var wheelSelectedHandle: Handle = null;
	static var gradientSelectedHandle: Handle = null;
	public static function colorWheel(ui: Zui, handle: Handle, alpha = false, w: Null<Float> = null, h: Null<Float> = null, colorPreview = true, picker: Void->Void = null): kha.Color {
		if (w == null) w = ui._w;
		rgbToHsv(handle.color.R, handle.color.G, handle.color.B, ar);
		var chue = ar[0];
		var csat = ar[1];
		var cval = ar[2];
		var calpha = handle.color.A;
		// Wheel
		var px = ui._x;
		var py = ui._y;
		var scroll = ui.currentWindow != null ? ui.currentWindow.scrollEnabled : false;
		if (!scroll) {
			w -= ui.SCROLL_W();
			px += ui.SCROLL_W() / 2;
		}
		var _x = ui._x;
		var _y = ui._y;
		var _w = ui._w;
		ui._w = Std.int(28 * ui.SCALE());
		if (picker != null && ui.button("P")) {
			picker();
			ui.changed = false;
			handle.changed = false;
			return handle.color;
		}
		ui._x = _x;
		ui._y = _y;
		ui._w = _w;
		ui.image(ui.ops.color_wheel, kha.Color.fromFloats(cval, cval, cval));
		// Picker
		var ph = ui._y - py;
		var ox = px + w / 2;
		var oy = py + ph / 2;
		var cw = w * 0.7;
		var cwh = cw / 2;
		var cx = ox;
		var cy = oy + csat * cwh; // Sat is distance from center
		var gradTx = px + 0.897 * w ;
		var gradTy = oy - cwh;
		var gradW = 0.0777 * w;
		var gradH = cw;
		// Rotate around origin by hue
		var theta = chue * (Math.PI * 2.0);
		var cx2 = Math.cos(theta) * (cx - ox) - Math.sin(theta) * (cy - oy) + ox;
		var cy2 = Math.sin(theta) * (cx - ox) + Math.cos(theta) * (cy - oy) + oy;
		cx = cx2;
		cy = cy2;

		ui._x = px - (scroll ? 0 : ui.SCROLL_W() / 2);
		ui._y = py;
		ui.image(ui.ops.black_white_gradient);

		ui.g.color = 0xff000000;
		ui.g.fillRect(cx - 3 * ui.SCALE(), cy - 3 * ui.SCALE(), 6 * ui.SCALE(), 6 * ui.SCALE());
		ui.g.color = 0xffffffff;
		ui.g.fillRect(cx - 2 * ui.SCALE(), cy - 2 * ui.SCALE(), 4 * ui.SCALE(), 4 * ui.SCALE());

		ui.g.color = 0xff000000;
		ui.g.fillRect(gradTx + gradW / 2 - 3 * ui.SCALE(), gradTy + (1 - cval) * gradH - 3 * ui.SCALE(), 6 * ui.SCALE(), 6 * ui.SCALE());
		ui.g.color = 0xffffffff;
		ui.g.fillRect(gradTx + gradW / 2 - 2 * ui.SCALE(), gradTy + (1 - cval) * gradH - 2 * ui.SCALE(), 4 * ui.SCALE(), 4 * ui.SCALE());

		if (alpha) {
			var alphaHandle = handle.nest(1, {value: Math.round(calpha * 100) / 100});
			calpha = ui.slider(alphaHandle, "Alpha", 0.0, 1.0, true);
			if (alphaHandle.changed) handle.changed = ui.changed = true;
		}
		// Mouse picking for color wheel
		var gx = ox + ui._windowX;
		var gy = oy + ui._windowY;
		if (ui.inputStarted && ui.getInputInRect(gx - cwh, gy - cwh, cw, cw)) wheelSelectedHandle = handle;
		if (ui.inputReleased && wheelSelectedHandle != null) { wheelSelectedHandle = null; handle.changed = ui.changed = true; }
		if (ui.inputDown && wheelSelectedHandle == handle) {
			csat = Math.min(dist(gx, gy, ui.inputX, ui.inputY), cwh) / cwh;
			var angle = Math.atan2(ui.inputX - gx, ui.inputY - gy);
			if (angle < 0) angle = Math.PI + (Math.PI - Math.abs(angle));
			angle = Math.PI * 2 - angle;
			chue = angle / (Math.PI * 2);
			handle.changed = ui.changed = true;
		}
		// Mouse picking for cval
		if (ui.inputStarted && ui.getInputInRect(gradTx + ui._windowX, gradTy + ui._windowY, gradW, gradH)) gradientSelectedHandle = handle;
		if (ui.inputReleased && gradientSelectedHandle != null) { gradientSelectedHandle = null; handle.changed = ui.changed = true; }
		if (ui.inputDown && gradientSelectedHandle == handle) {
			cval = Math.max(0.01, Math.min(1, 1 - (ui.inputY - gradTy - ui._windowY) / gradH));
			handle.changed = ui.changed = true;
		}
		// Save as rgb
		hsvToRgb(chue, csat, cval, ar);
		handle.color = kha.Color.fromFloats(ar[0], ar[1], ar[2], calpha);

		if (colorPreview) ui.text("", Right, handle.color);

		var pos = Ext.inlineRadio(ui, Id.handle(), ["RGB", "HSV", "Hex"]);
		var h0 = handle.nest(0).nest(0);
		var h1 = handle.nest(0).nest(1);
		var h2 = handle.nest(0).nest(2);
		if (pos == 0) {
			h0.value = handle.color.R;

			handle.color.R = ui.slider(h0, "R", 0, 1, true);
			h1.value = handle.color.G;

			handle.color.G = ui.slider(h1, "G", 0, 1, true);
			h2.value = handle.color.B;
			handle.color.B = ui.slider(h2, "B", 0, 1, true);
		}
		else if (pos == 1) {
			rgbToHsv(handle.color.R, handle.color.G, handle.color.B, ar);
			h0.value = ar[0];
			h1.value = ar[1];
			h2.value = ar[2];
			var chue = ui.slider(h0, "H", 0, 1, true);
			var csat = ui.slider(h1, "S", 0, 1, true);
			var cval = ui.slider(h2, "V", 0, 1, true);
			hsvToRgb(chue, csat, cval, ar);
			handle.color = kha.Color.fromFloats(ar[0], ar[1], ar[2]);
		}
		else if (pos == 2) {
			#if js
			handle.text = untyped (handle.color >>> 0).toString(16);
			var hexCode = ui.textInput(handle, "#");
			
			if (hexCode.length >= 1 && hexCode.charAt(0) == "#") // Allow # at the beginning
				hexCode = hexCode.substr(1);
			if (hexCode.length == 3) // 3 digit CSS style values like fa0 --> ffaa00
				hexCode = hexCode.charAt(0) + hexCode.charAt(0) + hexCode.charAt(1) + hexCode.charAt(1) + hexCode.charAt(2) + hexCode.charAt(2);
			if (hexCode.length == 4) // 4 digit CSS style values
				hexCode = hexCode.charAt(0) + hexCode.charAt(0) + hexCode.charAt(1) + hexCode.charAt(1) + hexCode.charAt(2) + hexCode.charAt(2) + hexCode.charAt(3) + hexCode.charAt(3);
			if (hexCode.length == 6) // Make the alpha channel optional
				hexCode = "ff" + hexCode;
			
			handle.color = untyped parseInt(hexCode, 16);
			#end
		}
		if (h0.changed || h1.changed || h2.changed) handle.changed = ui.changed = true;

		if (ui.getInputInRect(ui._windowX + px, ui._windowY + py, w, h == null ? (ui._y - py) : h) && ui.inputReleased) // Do not close if user clicks
		   ui.changed = true;

		return handle.color;
	}

	static function rightAlignNumber(number: Int, length: Int): String {
		var s = number + "";
		while (s.length < length)
			s = " " + s;
		return s;
	}

	public static var textAreaLineNumbers = false;
	public static var textAreaScrollPastEnd = false;
	public static var textAreaColoring: TTextColoring = null;

	public static function textArea(ui: Zui, handle: Handle, align = Align.Left, editable = true, label = "", wordWrap = false): String {
		handle.text = StringTools.replace(handle.text, "\t", "    ");
		var selected = ui.textSelectedHandle == handle; // Text being edited
		var lines = handle.text.split("\n");
		var showLabel = (lines.length == 1 && lines[0] == "");
		var keyPressed = selected && ui.isKeyPressed;
		ui.highlightOnSelect = false;
		ui.tabSwitchEnabled = false;

		if (wordWrap && handle.text != "") {
			var cursorSet = false;
			var cursorPos = ui.cursorX;
			for (i in 0...handle.position) cursorPos += lines[i].length + 1; // + \n
			var words = lines.join(" ").split(" ");
			lines = [];
			var line = "";
			for (w in words) {
				var linew = ui.ops.font.width(ui.fontSize, line + " " + w);
				var wordw = ui.ops.font.width(ui.fontSize, " " + w);
				if (linew > ui._w - 10 && linew > wordw) {
					lines.push(line);
					line = "";
				}
				line = line == "" ? w : line + " " + w;

				var linesLen = lines.length;
				for (l in lines) linesLen += l.length;
				if (selected && !cursorSet && cursorPos <= linesLen + line.length) {
					cursorSet = true;
					handle.position = lines.length;
					ui.cursorX = ui.highlightAnchor = cursorPos - linesLen;
				}
			}
			lines.push(line);
			if (selected) {
				ui.textSelected = handle.text = lines[handle.position];
			}
		}
		var cursorStartX = ui.cursorX;

		if (textAreaLineNumbers) {
			var _y = ui._y;
			var _TEXT_COL = ui.t.TEXT_COL;
			ui.t.TEXT_COL = ui.t.ACCENT_COL;
			var maxLength = Math.ceil(Math.log(lines.length + 0.5) / Math.log(10)); // Express log_10 with natural log
			for (i in 0...lines.length) {
				ui.text(rightAlignNumber(i + 1, maxLength));
				ui._y -= ui.ELEMENT_OFFSET();
			}
			ui.t.TEXT_COL = _TEXT_COL;
			ui._y = _y;
			ui._x += (lines.length + "").length * 16 + 4;
		}

		ui.g.color = ui.t.SEPARATOR_COL; // Background
		ui.drawRect(ui.g, true, ui._x + ui.buttonOffsetY, ui._y + ui.buttonOffsetY, ui._w - ui.buttonOffsetY * 2, lines.length * ui.ELEMENT_H() - ui.buttonOffsetY * 2);

		var _textColoring = ui.textColoring;
		ui.textColoring = textAreaColoring;

		for (i in 0...lines.length) { // Draw lines
			if ((!selected && ui.getHover()) || (selected && i == handle.position)) {
				handle.position = i; // Set active line
				handle.text = lines[i];
				ui.submitTextHandle = null;
				ui.textInput(handle, showLabel ? label : "", align, editable);
				if (keyPressed && ui.key != KeyCode.Return && ui.key != KeyCode.Escape) { // Edit text
					lines[i] = ui.textSelected;
				}
			}
			else {
				if (showLabel) {
					var TEXT_COL = ui.t.TEXT_COL;
					ui.t.TEXT_COL = ui.t.LABEL_COL;
					ui.text(label, Right);
					ui.t.TEXT_COL = TEXT_COL;
				}
				else {
					ui.text(lines[i], align);
				}
			}
			ui._y -= ui.ELEMENT_OFFSET();
		}
		ui._y += ui.ELEMENT_OFFSET();
		ui.textColoring = _textColoring;

		if (textAreaScrollPastEnd) {
			ui._y += ui._h - ui.windowHeaderH - ui.ELEMENT_H() - ui.ELEMENT_OFFSET();
		}

		if (keyPressed) {
			// Move cursor vertically
			if (ui.key == KeyCode.Down && handle.position < lines.length - 1) {
				handle.position++;
				scrollAlign(ui, handle);
			}
			if (ui.key == KeyCode.Up && handle.position > 0) {
				handle.position--;
				scrollAlign(ui, handle);
			}
			// New line
			if (editable && ui.key == KeyCode.Return && !wordWrap) {
				handle.position++;
				lines.insert(handle.position, lines[handle.position - 1].substr(ui.cursorX));
				lines[handle.position - 1] = lines[handle.position - 1].substr(0, ui.cursorX);
				ui.startTextEdit(handle);
				ui.cursorX = ui.highlightAnchor = 0;
				scrollAlign(ui, handle);
			}
			// Delete line
			if (editable && ui.key == KeyCode.Backspace && cursorStartX == 0 && handle.position > 0) {
				handle.position--;
				ui.cursorX = ui.highlightAnchor = lines[handle.position].length;
				lines[handle.position] += lines[handle.position + 1];
				lines.splice(handle.position + 1, 1);
				scrollAlign(ui, handle);
			}
			ui.textSelected = lines[handle.position];
		}

		ui.highlightOnSelect = true;
		ui.tabSwitchEnabled = true;
		handle.text = lines.join("\n");
		return handle.text;
	}

	static function scrollAlign(ui: Zui, handle: Handle) {
		// Scroll down
		if ((handle.position + 1) * ui.ELEMENT_H() + ui.currentWindow.scrollOffset > ui._h - ui.windowHeaderH) {
			ui.currentWindow.scrollOffset -= ui.ELEMENT_H();
		}
		// Scroll up
		else if ((handle.position + 1) * ui.ELEMENT_H() + ui.currentWindow.scrollOffset < ui.windowHeaderH) {
			ui.currentWindow.scrollOffset += ui.ELEMENT_H();
		}
	}

	static var _ELEMENT_OFFSET = 0;
	static var _BUTTON_COL = 0;
	public static function beginMenu(ui: Zui) {
		_ELEMENT_OFFSET = ui.t.ELEMENT_OFFSET;
		_BUTTON_COL = ui.t.BUTTON_COL;
		ui.t.ELEMENT_OFFSET = 0;
		ui.t.BUTTON_COL = ui.t.SEPARATOR_COL;
		ui.g.color = ui.t.SEPARATOR_COL;
		ui.g.fillRect(0, 0, ui._windowW, MENUBAR_H(ui));
	}

	public static function endMenu(ui: Zui) {
		ui.t.ELEMENT_OFFSET = _ELEMENT_OFFSET;
		ui.t.BUTTON_COL = _BUTTON_COL;
	}

	public static function menuButton(ui: Zui, text: String): Bool {
		ui._w = Std.int(ui.ops.font.width(ui.fontSize, text) + 25 * ui.SCALE());
		return ui.button(text);
	}

	public static inline function MENUBAR_H(ui: Zui): Float {
		return ui.BUTTON_H() * 1.1 + 2 + ui.buttonOffsetY;
	}

	static inline function dist(x1: Float, y1: Float, x2: Float, y2: Float): Float {
		var vx = x1 - x2;
		var vy = y1 - y2;
		return Math.sqrt(vx * vx + vy * vy);
	}
	static inline function fract(f: Float): Float {
		return f - Std.int(f);
	}
	static inline function mix(x: Float, y: Float, a: Float): Float {
		return x * (1.0 - a) + y * a;
	}
	static inline function clamp(x: Float, minVal: Float, maxVal: Float): Float {
		return Math.min(Math.max(x, minVal), maxVal);
	}
	static inline function step(edge: Float, x: Float): Float {
		return x < edge ? 0.0 : 1.0;
	}

	static inline var kx = 1.0;
	static inline var ky = 2.0 / 3.0;
	static inline var kz = 1.0 / 3.0;
	static inline var kw = 3.0;
	static var ar = [0.0, 0.0, 0.0];
	static function hsvToRgb(cR: Float, cG: Float, cB: Float, out: Array<Float>) {
		var px = Math.abs(fract(cR + kx) * 6.0 - kw);
		var py = Math.abs(fract(cR + ky) * 6.0 - kw);
		var pz = Math.abs(fract(cR + kz) * 6.0 - kw);
		out[0] = cB * mix(kx, clamp(px - kx, 0.0, 1.0), cG);
		out[1] = cB * mix(kx, clamp(py - kx, 0.0, 1.0), cG);
		out[2] = cB * mix(kx, clamp(pz - kx, 0.0, 1.0), cG);
	}

	static inline var Kx = 0.0;
	static inline var Ky = -1.0 / 3.0;
	static inline var Kz = 2.0 / 3.0;
	static inline var Kw = -1.0;
	static inline var e = 1.0e-10;
	static function rgbToHsv(cR: Float, cG: Float, cB: Float, out: Array<Float>) {
		var px = mix(cB, cG, step(cB, cG));
		var py = mix(cG, cB, step(cB, cG));
		var pz = mix(Kw, Kx, step(cB, cG));
		var pw = mix(Kz, Ky, step(cB, cG));
		var qx = mix(px, cR, step(px, cR));
		var qy = mix(py, py, step(px, cR));
		var qz = mix(pw, pz, step(px, cR));
		var qw = mix(cR, px, step(px, cR));
		var d = qx - Math.min(qw, qy);
		out[0] = Math.abs(qz + (qw - qy) / (6.0 * d + e));
		out[1] = d / (qx + e);
		out[2] = qx;
	}
}
