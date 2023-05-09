package armory.ui;

import zui.Zui;

using kha.graphics2.GraphicsExtension;

@:access(zui.Zui)
class Canvas {

	public static inline var defaultFontName = "font_default.ttf";

	public static var assetMap = new Map<Int, Dynamic>(); // kha.Image | kha.Font
	public static var themes = new Array<zui.Themes.TTheme>();
	static var events:Array<String> = [];

	public static var screenW = -1;
	public static var screenH = -1;
	public static var locale = "en";
	static var _ui: Zui;
	static var h = new zui.Zui.Handle(); // TODO: needs one handle per canvas

	public static function draw(ui: Zui, canvas: TCanvas, g: kha.graphics2.Graphics): Array<String> {

		screenW = kha.System.windowWidth();
		screenH = kha.System.windowHeight();

		events.resize(0);

		_ui = ui;

		g.end();
		ui.begin(g); // Bake elements
		g.begin(false);

		ui.g = g;

		for (elem in canvas.elements) {
			if (elem.parent == null) drawElement(ui, canvas, elem);
		}

		g.end();
		ui.end(); // Finish drawing
		g.begin(false);

		return events;
	}

	static function drawElement(ui: Zui, canvas: TCanvas, element: TElement, px = 0.0, py = 0.0) {

		if (element == null || element.visible == false) return;

		var anchorOffset = getAnchorOffset(canvas, element);
		px += anchorOffset[0];
		py += anchorOffset[1];

		ui._x = canvas.x + scaled(element.x) + px;
		ui._y = canvas.y + scaled(element.y) + py;
		ui._w = scaled(element.width);

		var rotated = element.rotation != null && element.rotation != 0;
		if (rotated) ui.g.pushRotation(element.rotation, ui._x + scaled(element.width) / 2, ui._y + scaled(element.height) / 2);

		var font = ui.ops.font;
		var fontAsset = isFontAsset(element.asset);
		if (fontAsset) ui.ops.font = getAsset(canvas, element.asset);

		switch (element.type) {
			case Text:
				var prevFontSize = ui.fontSize;
				var prevTEXT_COL = ui.t.TEXT_COL;
				ui.fontSize = scaled(element.height);
				ui.t.TEXT_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);

				ui.text(getText(canvas, element), element.alignment);

				ui.fontSize = prevFontSize;
				ui.t.TEXT_COL = prevTEXT_COL;

			case Button:
				var prevELEMENT_H = ui.t.ELEMENT_H;
				var prevBUTTON_H = ui.t.BUTTON_H;
				var prevBUTTON_COL = ui.t.BUTTON_COL;
				var prevBUTTON_TEXT_COL = ui.t.BUTTON_TEXT_COL;
				var prevBUTTON_HOVER_COL = ui.t.BUTTON_HOVER_COL;
				var prevBUTTON_PRESSED_COL = ui.t.BUTTON_PRESSED_COL;
				ui.t.ELEMENT_H = element.height;
				ui.t.BUTTON_H = element.height;
				ui.t.BUTTON_COL = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.t.BUTTON_TEXT_COL = getColor(element.color_text, getTheme(canvas.theme).BUTTON_TEXT_COL);
				ui.t.BUTTON_HOVER_COL = getColor(element.color_hover, getTheme(canvas.theme).BUTTON_HOVER_COL);
				ui.t.BUTTON_PRESSED_COL = getColor(element.color_press, getTheme(canvas.theme).BUTTON_PRESSED_COL);

				if (ui.button(getText(canvas, element), element.alignment)) {
					var e = element.event;
					if (e != null && e != "") events.push(e);
				}

				ui.t.ELEMENT_H = prevELEMENT_H;
				ui.t.BUTTON_H = prevBUTTON_H;
				ui.t.BUTTON_COL = prevBUTTON_COL;
				ui.t.BUTTON_TEXT_COL = prevBUTTON_TEXT_COL;
				ui.t.BUTTON_HOVER_COL = prevBUTTON_HOVER_COL;
				ui.t.BUTTON_PRESSED_COL = prevBUTTON_PRESSED_COL;

			case Image:
				var image = getAsset(canvas, element.asset);
				if (image != null && !fontAsset) {
					ui.imageScrollAlign = false;
					var tint = element.color != null ? element.color : 0xffffffff;
					if (ui.image(image, tint, scaled(element.height)) == zui.Zui.State.Released) {
						var e = element.event;
						if (e != null && e != "") events.push(e);
					}
					ui.imageScrollAlign = true;
				}

			case FRectangle:
				var col = ui.g.color;
				ui.g.color = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.g.fillRect(ui._x, ui._y, ui._w, scaled(element.height));
				ui.g.color = col;

			case FCircle:
				var col = ui.g.color;
				ui.g.color = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.g.fillCircle(ui._x + (scaled(element.width) / 2), ui._y + (scaled(element.height) / 2), ui._w / 2);
				ui.g.color = col;

			case Rectangle:
				var col = ui.g.color;
				ui.g.color = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.g.drawRect(ui._x, ui._y, ui._w, scaled(element.height), element.strength);
				ui.g.color = col;

			case Circle:
				var col = ui.g.color;
				ui.g.color = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.g.drawCircle(ui._x+(scaled(element.width) / 2), ui._y + (scaled(element.height) / 2), ui._w / 2, element.strength);
				ui.g.color = col;

			case FTriangle:
				var col = ui.g.color;
				ui.g.color = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.g.fillTriangle(ui._x + (ui._w / 2), ui._y, ui._x, ui._y + scaled(element.height), ui._x + ui._w, ui._y + scaled(element.height));
				ui.g.color = col;

			case Triangle:
				var col = ui.g.color;
				ui.g.color = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.g.drawLine(ui._x + (ui._w / 2), ui._y, ui._x, ui._y + scaled(element.height), element.strength);
				ui.g.drawLine(ui._x, ui._y + scaled(element.height), ui._x + ui._w, ui._y + scaled(element.height), element.strength);
				ui.g.drawLine(ui._x + ui._w, ui._y + scaled(element.height), ui._x + (ui._w / 2), ui._y, element.strength);
				ui.g.color = col;

			case Check:
				var prevTEXT_COL = ui.t.TEXT_COL;
				var prevACCENT_COL = ui.t.ACCENT_COL;
				var prevACCENT_HOVER_COL = ui.t.ACCENT_HOVER_COL;
				ui.t.TEXT_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.ACCENT_COL = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.t.ACCENT_HOVER_COL = getColor(element.color_hover, getTheme(canvas.theme).BUTTON_HOVER_COL);

				ui.check(h.nest(element.id), getText(canvas, element));

				ui.t.TEXT_COL = prevTEXT_COL;
				ui.t.ACCENT_COL = prevACCENT_COL;
				ui.t.ACCENT_HOVER_COL = prevACCENT_HOVER_COL;

			case Radio:
				var prevTEXT_COL = ui.t.TEXT_COL;
				var prevACCENT_COL = ui.t.ACCENT_COL;
				var prevACCENT_HOVER_COL = ui.t.ACCENT_HOVER_COL;
				ui.t.TEXT_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.ACCENT_COL = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.t.ACCENT_HOVER_COL = getColor(element.color_hover, getTheme(canvas.theme).BUTTON_HOVER_COL);

				zui.Ext.inlineRadio(ui, h.nest(element.id), getText(canvas, element).split(";"));

				ui.t.TEXT_COL = prevTEXT_COL;
				ui.t.ACCENT_COL = prevACCENT_COL;
				ui.t.ACCENT_HOVER_COL = prevACCENT_HOVER_COL;

			case Combo:
				var prevTEXT_COL = ui.t.TEXT_COL;
				var prevLABEL_COL = ui.t.LABEL_COL;
				var prevACCENT_COL = ui.t.ACCENT_COL;
				var prevSEPARATOR_COL = ui.t.SEPARATOR_COL;
				var prevACCENT_HOVER_COL = ui.t.ACCENT_HOVER_COL;
				ui.t.TEXT_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.LABEL_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.ACCENT_COL = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.t.SEPARATOR_COL = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.t.ACCENT_HOVER_COL = getColor(element.color_hover, getTheme(canvas.theme).BUTTON_HOVER_COL);

				ui.combo(h.nest(element.id), getText(canvas, element).split(";"));

				ui.t.TEXT_COL = prevTEXT_COL;
				ui.t.LABEL_COL = prevLABEL_COL;
				ui.t.ACCENT_COL = prevACCENT_COL;
				ui.t.SEPARATOR_COL = prevSEPARATOR_COL;
				ui.t.ACCENT_HOVER_COL = prevACCENT_HOVER_COL;

			case Slider:
				var prevTEXT_COL = ui.t.TEXT_COL;
				var prevLABEL_COL = ui.t.LABEL_COL;
				var prevACCENT_COL = ui.t.ACCENT_COL;
				var prevACCENT_HOVER_COL = ui.t.ACCENT_HOVER_COL;
				ui.t.TEXT_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.LABEL_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.ACCENT_COL = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.t.ACCENT_HOVER_COL = getColor(element.color_hover, getTheme(canvas.theme).BUTTON_HOVER_COL);

				ui.slider(h.nest(element.id), getText(canvas, element), 0.0, 1.0, true, 100, true, element.alignment);

				ui.t.TEXT_COL = prevTEXT_COL;
				ui.t.LABEL_COL = prevLABEL_COL;
				ui.t.ACCENT_COL = prevACCENT_COL;
				ui.t.ACCENT_HOVER_COL = prevACCENT_HOVER_COL;

			case TextInput:
				var prevTEXT_COL = ui.t.TEXT_COL;
				var prevLABEL_COL = ui.t.LABEL_COL;
				var prevACCENT_COL = ui.t.ACCENT_COL;
				var prevACCENT_HOVER_COL = ui.t.ACCENT_HOVER_COL;
				ui.t.TEXT_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.LABEL_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.ACCENT_COL = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.t.ACCENT_HOVER_COL = getColor(element.color_hover, getTheme(canvas.theme).BUTTON_HOVER_COL);

				ui.textInput(h.nest(element.id), getText(canvas, element), element.alignment);
				if (h.nest(element.id).changed) {
					var e = element.event;
					if (e != null && e != "") events.push(e);
				}

				ui.t.TEXT_COL = prevTEXT_COL;
				ui.t.LABEL_COL = prevLABEL_COL;
				ui.t.ACCENT_COL = prevACCENT_COL;
				ui.t.ACCENT_HOVER_COL = prevACCENT_HOVER_COL;

			case TextArea:
				var prevTEXT_COL = ui.t.TEXT_COL;
				var prevLABEL_COL = ui.t.LABEL_COL;
				var prevACCENT_COL = ui.t.ACCENT_COL;
				var prevACCENT_HOVER_COL = ui.t.ACCENT_HOVER_COL;
				ui.t.TEXT_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.LABEL_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.ACCENT_COL = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.t.ACCENT_HOVER_COL = getColor(element.color_hover, getTheme(canvas.theme).BUTTON_HOVER_COL);

				h.nest(element.id).text = getText(canvas, element);
				zui.Ext.textArea(ui,h.nest(element.id), element.alignment,element.editable);
				if (h.nest(element.id).changed) {
					var e = element.event;
					if (e != null && e != "") events.push(e);
				}

				ui.t.TEXT_COL = prevTEXT_COL;
				ui.t.LABEL_COL = prevLABEL_COL;
				ui.t.ACCENT_COL = prevACCENT_COL;
				ui.t.ACCENT_HOVER_COL = prevACCENT_HOVER_COL;

			case KeyInput:
				var prevTEXT_COL = ui.t.TEXT_COL;
				var prevLABEL_COL = ui.t.LABEL_COL;
				var prevACCENT_COL = ui.t.ACCENT_COL;
				var prevACCENT_HOVER_COL = ui.t.ACCENT_HOVER_COL;
				ui.t.TEXT_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.LABEL_COL = getColor(element.color_text, getTheme(canvas.theme).TEXT_COL);
				ui.t.ACCENT_COL = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.t.ACCENT_HOVER_COL = getColor(element.color_hover, getTheme(canvas.theme).BUTTON_HOVER_COL);

				Ext.keyInput(ui, h.nest(element.id), getText(canvas, element));

				ui.t.TEXT_COL = prevTEXT_COL;
				ui.t.LABEL_COL = prevLABEL_COL;
				ui.t.ACCENT_COL = prevACCENT_COL;
				ui.t.ACCENT_HOVER_COL = prevACCENT_HOVER_COL;

			case ProgressBar:
				var col = ui.g.color;
				var progress = element.progress_at;
				var totalprogress = element.progress_total;
				ui.g.color = getColor(element.color_progress, getTheme(canvas.theme).TEXT_COL);
				ui.g.fillRect(ui._x, ui._y, ui._w / totalprogress * Math.min(progress, totalprogress), scaled(element.height));
				ui.g.color = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.g.drawRect(ui._x, ui._y, ui._w, scaled(element.height), element.strength);
				ui.g.color = col;

			case CProgressBar:
				var col = ui.g.color;
				var progress = element.progress_at;
				var totalprogress = element.progress_total;
				ui.g.color = getColor(element.color_progress, getTheme(canvas.theme).TEXT_COL);
				ui.g.drawArc(ui._x + (scaled(element.width) / 2), ui._y + (scaled(element.height) / 2), ui._w / 2, -Math.PI / 2, ((Math.PI * 2) / totalprogress * progress) - Math.PI / 2, element.strength);
				ui.g.color = getColor(element.color, getTheme(canvas.theme).BUTTON_COL);
				ui.g.fillCircle(ui._x + (scaled(element.width) / 2), ui._y + (scaled(element.height) / 2), (ui._w / 2) - 10);
				ui.g.color = col;

			case Empty:
		}

		ui.ops.font = font;

		if (element.children != null) {
			for (id in element.children) {
				drawElement(ui, canvas, elemById(canvas, id), scaled(element.x) + px, scaled(element.y) + py);
			}
		}

		if (rotated) ui.g.popTransformation();
	}

	static inline function getText(canvas: TCanvas, e: TElement): String {
		return e.text;
	}

	public static function getAsset(canvas: TCanvas, asset: String): Dynamic { // kha.Image | kha.Font {
		for (a in canvas.assets) if (a.name == asset) return assetMap.get(a.id);
		return null;
	}

	static var elemId = -1;
	public static function getElementId(canvas: TCanvas): Int {
		if (elemId == -1) for (e in canvas.elements) if (elemId < e.id) elemId = e.id;
		return ++elemId;
	}

	static var assetId = -1;
	public static function getAssetId(canvas: TCanvas): Int {
		if (assetId == -1) for (a in canvas.assets) if (assetId < a.id) assetId = a.id;
		return ++assetId;
	}

	static function elemById(canvas: TCanvas, id: Int): TElement {
		for (e in canvas.elements) if (e.id == id) return e;
		return null;
	}

	static inline function scaled(f: Float): Int {
		return Std.int(f * _ui.SCALE());
	}

	public static inline function isFontAsset(assetName: Null<String>): Bool {
		return assetName != null && StringTools.endsWith(assetName.toLowerCase(), ".ttf");
	}

	public static inline function getColor(color: Null<Int>, defaultColor: Int): Int {
		return color != null ? color : defaultColor;
	}

	public static function getTheme(theme: String): zui.Themes.TTheme {
		for (t in Canvas.themes) {
			if (t.NAME == theme) return t;
		}
		return null;
	}

	/**
		Returns the positional scaled offset of the given element based on its anchor setting.
		@param canvas The canvas object
		@param element The element
		@return `Array<Float> [xOffset, yOffset]`
	**/
	public static function getAnchorOffset(canvas: TCanvas, element: TElement): Array<Float> {
		var boxWidth, boxHeight: Float;
		var offsetX = 0.0;
		var offsetY = 0.0;

		if (element.parent == null) {
			boxWidth = canvas.width;
			boxHeight = canvas.height;
		}
		else {
			var parent = elemById(canvas, element.parent);
			boxWidth = scaled(parent.width);
			boxHeight = scaled(parent.height);
		}

		switch (element.anchor) {
			case Top:
				offsetX += boxWidth / 2 - scaled(element.width) / 2;
			case TopRight:
				offsetX += boxWidth - scaled(element.width);
			case CenterLeft:
				offsetY += boxHeight / 2 - scaled(element.height) / 2;
			case Center:
				offsetX += boxWidth / 2 - scaled(element.width) / 2;
				offsetY += boxHeight / 2 - scaled(element.height) / 2;
			case CenterRight:
				offsetX += boxWidth - scaled(element.width);
				offsetY += boxHeight / 2 - scaled(element.height) / 2;
			case BottomLeft:
				offsetY += boxHeight - scaled(element.height);
			case Bottom:
				offsetX += boxWidth / 2 - scaled(element.width) / 2;
				offsetY += boxHeight - scaled(element.height);
			case BottomRight:
				offsetX += boxWidth - scaled(element.width);
				offsetY += boxHeight - scaled(element.height);
		}

		return [offsetX, offsetY];
	}
}

typedef TCanvas = {
	var name: String;
	var x: Float;
	var y: Float;
	var width: Int;
	var height: Int;
	var elements: Array<TElement>;
	var theme: String;
	@:optional var assets: Array<TAsset>;
	@:optional var locales: Array<TLocale>;
}

typedef TElement = {
	var id: Int;
	var type: ElementType;
	var name: String;
	var x: Float;
	var y: Float;
	var width: Int;
	var height: Int;
	@:optional var rotation: Null<kha.FastFloat>;
	@:optional var text: String;
	@:optional var event: String;
	// null = follow theme settings
	@:optional var color: Null<Int>;
	@:optional var color_text: Null<Int>;
	@:optional var color_hover: Null<Int>;
	@:optional var color_press: Null<Int>;
	@:optional var color_progress: Null<Int>;
	@:optional var progress_at: Null<Int>;
	@:optional var progress_total: Null<Int>;
	@:optional var strength: Null<Int>;
	@:optional var alignment: Null<Int>;
	@:optional var anchor: Null<Int>;
	@:optional var parent: Null<Int>; // id
	@:optional var children: Array<Int>; // ids
	@:optional var asset: String;
	@:optional var visible: Null<Bool>;
	@:optional var editable: Null<Bool>;
}

typedef TAsset = {
	var id: Int;
	var name: String;
	var file: String;
}

typedef TLocale = {
	var name: String; // "en"
	var texts: Array<TTranslatedText>;
}

typedef TTranslatedText = {
	var id: Int; // element id
	var text: String;
}

@:enum abstract ElementType(Int) from Int to Int {
	var Text = 0;
	var Image = 1;
	var Button = 2;
	var Empty = 3;
	// var HLayout = 4;
	// var VLayout = 5;
	var Check = 6;
	var Radio = 7;
	var Combo = 8;
	var Slider = 9;
	var TextInput = 10;
	var KeyInput = 11;
	var FRectangle = 12;
	var Rectangle = 13;
	var FCircle = 14;
	var Circle = 15;
	var FTriangle = 16;
	var Triangle = 17;
	var ProgressBar = 18;
	var CProgressBar = 19;
	var TextArea = 20;
}

@:enum abstract Anchor(Int) from Int to Int {
	var TopLeft = 0;
	var Top = 1;
	var TopRight = 2;
	var CenterLeft = 3;
	var Center = 4;
	var CenterRight = 5;
	var BottomLeft = 6;
	var Bottom = 7;
	var BottomRight = 8;
}
