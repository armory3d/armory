package armory.ui;

import zui.Zui;
import kha.input.Keyboard;
import kha.input.KeyCode;

typedef ListOpts = {
	?addCb: String->Void,
	?removeCb: Int->Void,
	?getNameCb: Int->String,
	?setNameCb: Int->String->Void,
	?getLabelCb: Int->String,
	?itemDrawCb: Handle->Int->Void,
	?showRadio: Bool, // false
	?editable: Bool, // true
	?showAdd: Bool, // true
	?addLabel: String // 'Add'
}

@:access(zui.Zui)
class Ext {
	public static function keyInput(ui: Zui, handle: Handle, label = "", align: Align = Left): Int {
		if (!ui.isVisible(ui.ELEMENT_H())) {
			ui.endElement();
			return Std.int(handle.value);
		}

		var hover = ui.getHover();
		if (hover && Zui.onTextHover != null) Zui.onTextHover();
		ui.g.color = hover ? ui.t.ACCENT_HOVER_COL : ui.t.ACCENT_COL; // Text bg
		ui.drawRect(ui.g, ui.t.FILL_ACCENT_BG, ui._x + ui.buttonOffsetY, ui._y + ui.buttonOffsetY, ui._w - ui.buttonOffsetY * 2, ui.BUTTON_H());

		var startEdit = ui.getReleased() || ui.tabPressed;
		if (ui.textSelectedHandle != handle && startEdit) ui.startTextEdit(handle);
		if (ui.textSelectedHandle == handle) Ext.listenToKey(ui, handle);
		else handle.changed = false;

		if (label != "") {
			ui.g.color = ui.t.LABEL_COL; // Label
			var labelAlign = align == Align.Right ? Align.Left : Align.Right;
			var xOffset = labelAlign == Align.Left ? 7 : 0;
			ui.drawString(ui.g, label, xOffset, 0, labelAlign);
		}

		handle.text = Ext.keycodeToString(Std.int(handle.value));

		ui.g.color = ui.t.TEXT_COL; // Text
		ui.textSelectedHandle != handle ? ui.drawString(ui.g, handle.text, null, 0, align) : ui.drawString(ui.g, ui.textSelected, null, 0, align);

		ui.endElement();

		return Std.int(handle.value);
	}

	static function listenToKey(ui: Zui, handle: Handle) {
		if (ui.isKeyDown) {
			handle.value = ui.key;
			handle.changed = ui.changed = true;

			ui.textSelectedHandle = null;
			ui.isTyping = false;

			if (Keyboard.get() != null) Keyboard.get().hide();
		}
		else {
			ui.textSelected = "Press a key...";
		}
	}

	public static function list(ui: Zui, handle: Handle, ar: Array<Dynamic>, ?opts: ListOpts ): Int {
		var selected = 0;
		if (opts == null) opts = {};

		var addCb = opts.addCb != null ? opts.addCb : function(name: String) ar.push(name);
		var removeCb = opts.removeCb != null ? opts.removeCb : function(i: Int) ar.splice(i, 1);
		var getNameCb = opts.getNameCb != null ? opts.getNameCb : function(i: Int) return ar[i];
		var setNameCb = opts.setNameCb != null ? opts.setNameCb : function(i: Int, name: String) ar[i] = name;
		var getLabelCb = opts.getLabelCb != null ? opts.getLabelCb : function(i: Int) return "";
		var itemDrawCb = opts.itemDrawCb;
		var showRadio = opts.showRadio != null ? opts.showRadio : false;
		var editable = opts.editable != null ? opts.editable : true;
		var showAdd = opts.showAdd != null ? opts.showAdd : true;
		var addLabel = opts.addLabel != null ? opts.addLabel : "Add";

		var i = 0;
		while (i < ar.length) {
			if (showRadio) { // Prepend ratio button
				ui.row([0.12, 0.68, 0.2]);
				if (ui.radio(handle.nest(0), i, "")) {
					selected = i;
				}
			}
			else ui.row([0.8, 0.2]);

			var itemHandle = handle.nest(i);
			itemHandle.text = getNameCb(i);
			editable ? setNameCb(i, ui.textInput(itemHandle, getLabelCb(i))) : ui.text(getNameCb(i));
			if (ui.button("X")) removeCb(i);
			else i++;

			if (itemDrawCb != null) itemDrawCb(itemHandle.nest(i), i - 1);
		}
		if (showAdd && ui.button(addLabel)) addCb("untitled");

		return selected;
	}

	public static function panelList(ui: Zui, handle: Handle, ar: Array<Dynamic>,
									 addCb: String->Void = null,
									 removeCb: Int->Void = null,
									 getNameCb: Int->String = null,
									 setNameCb: Int->String->Void = null,
									 itemDrawCb: Handle->Int->Void = null,
									 editable = true,
									 showAdd = true,
									 addLabel: String = "Add") {

		if (addCb == null) addCb = function(name: String) { ar.push(name); };
		if (removeCb == null) removeCb = function(i: Int) { ar.splice(i, 1); };
		if (getNameCb == null) getNameCb = function(i: Int) { return ar[i]; };
		if (setNameCb == null) setNameCb = function(i: Int, name: String) { ar[i] = name; };

		var i = 0;
		while (i < ar.length) {
			ui.row([0.12, 0.68, 0.2]);
			var expanded = ui.panel(handle.nest(i), "");

			var itemHandle = handle.nest(i);
			editable ? setNameCb(i, ui.textInput(itemHandle, getNameCb(i))) : ui.text(getNameCb(i));
			if (ui.button("X")) removeCb(i);
			else i++;

			if (itemDrawCb != null && expanded) itemDrawCb(itemHandle.nest(i), i - 1);
		}
		if (showAdd && ui.button(addLabel)) {
			addCb("untitled");
		}
	}

	public static function colorField(ui: Zui, handle:Handle, alpha = false): Int {
		ui.g.color = handle.color;

		ui.drawRect(ui.g, true, ui._x + 2, ui._y + ui.buttonOffsetY, ui._w - 4, ui.BUTTON_H());
		ui.g.color = ui.getHover() ? ui.t.ACCENT_HOVER_COL : ui.t.ACCENT_COL;
		ui.drawRect(ui.g, false, ui._x + 2, ui._y + ui.buttonOffsetY, ui._w - 4, ui.BUTTON_H(), 1.0);

		if (ui.getStarted()) {
			Popup.showCustom(
				new Zui(ui.ops),
				function(ui:Zui) {
					zui.Ext.colorWheel(ui, handle, alpha);
				},
				Std.int(ui.inputX), Std.int(ui.inputY), 200, 500);
		}

		ui.endElement();
		return handle.color;
	}

	public static function colorPicker(ui: Zui, handle: Handle, alpha = false): Int {
		var r = ui.slider(handle.nest(0, {value: handle.color.R}), "R", 0, 1, true);
		var g = ui.slider(handle.nest(1, {value: handle.color.G}), "G", 0, 1, true);
		var b = ui.slider(handle.nest(2, {value: handle.color.B}), "B", 0, 1, true);
		var a = handle.color.A;
		if (alpha) a = ui.slider(handle.nest(3, {value: a}), "A", 0, 1, true);
		var col = kha.Color.fromFloats(r, g, b, a);
		ui.text("", Right, col);
		return col;
	}

	/**
		Keycodes can be found here: http://api.kha.tech/kha/input/KeyCode.html
	**/
	static function keycodeToString(keycode: Int): String {
		return switch (keycode) {
			default: String.fromCharCode(keycode);
			case -1: "None";
			case KeyCode.Unknown: "Unknown";
			case KeyCode.Back: "Back";
			case KeyCode.Cancel: "Cancel";
			case KeyCode.Help: "Help";
			case KeyCode.Backspace: "Backspace";
			case KeyCode.Tab: "Tab";
			case KeyCode.Clear: "Clear";
			case KeyCode.Return: "Return";
			case KeyCode.Shift: "Shift";
			case KeyCode.Control: "Ctrl";
			case KeyCode.Alt: "Alt";
			case KeyCode.Pause: "Pause";
			case KeyCode.CapsLock: "CapsLock";
			case KeyCode.Kana: "Kana";
			// case KeyCode.Hangul: "Hangul"; // Hangul == Kana
			case KeyCode.Eisu: "Eisu";
			case KeyCode.Junja: "Junja";
			case KeyCode.Final: "Final";
			case KeyCode.Hanja: "Hanja";
			// case KeyCode.Kanji: "Kanji"; // Kanji == Hanja
			case KeyCode.Escape: "Esc";
			case KeyCode.Convert: "Convert";
			case KeyCode.NonConvert: "NonConvert";
			case KeyCode.Accept: "Accept";
			case KeyCode.ModeChange: "ModeChange";
			case KeyCode.Space: "Space";
			case KeyCode.PageUp: "PageUp";
			case KeyCode.PageDown: "PageDown";
			case KeyCode.End: "End";
			case KeyCode.Home: "Home";
			case KeyCode.Left: "Left";
			case KeyCode.Up: "Up";
			case KeyCode.Right: "Right";
			case KeyCode.Down: "Down";
			case KeyCode.Select: "Select";
			case KeyCode.Print: "Print";
			case KeyCode.Execute: "Execute";
			case KeyCode.PrintScreen: "PrintScreen";
			case KeyCode.Insert: "Insert";
			case KeyCode.Delete: "Delete";
			case KeyCode.Colon: "Colon";
			case KeyCode.Semicolon: "Semicolon";
			case KeyCode.LessThan: "LessThan";
			case KeyCode.Equals: "Equals";
			case KeyCode.GreaterThan: "GreaterThan";
			case KeyCode.QuestionMark: "QuestionMark";
			case KeyCode.At: "At";
			case KeyCode.Win: "Win";
			case KeyCode.ContextMenu: "ContextMenu";
			case KeyCode.Sleep: "Sleep";
			case KeyCode.Numpad0: "Numpad0";
			case KeyCode.Numpad1: "Numpad1";
			case KeyCode.Numpad2: "Numpad2";
			case KeyCode.Numpad3: "Numpad3";
			case KeyCode.Numpad4: "Numpad4";
			case KeyCode.Numpad5: "Numpad5";
			case KeyCode.Numpad6: "Numpad6";
			case KeyCode.Numpad7: "Numpad7";
			case KeyCode.Numpad8: "Numpad8";
			case KeyCode.Numpad9: "Numpad9";
			case KeyCode.Multiply: "Multiply";
			case KeyCode.Add: "Add";
			case KeyCode.Separator: "Separator";
			case KeyCode.Subtract: "Subtract";
			case KeyCode.Decimal: "Decimal";
			case KeyCode.Divide: "Divide";
			case KeyCode.F1: "F1";
			case KeyCode.F2: "F2";
			case KeyCode.F3: "F3";
			case KeyCode.F4: "F4";
			case KeyCode.F5: "F5";
			case KeyCode.F6: "F6";
			case KeyCode.F7: "F7";
			case KeyCode.F8: "F8";
			case KeyCode.F9: "F9";
			case KeyCode.F10: "F10";
			case KeyCode.F11: "F11";
			case KeyCode.F12: "F12";
			case KeyCode.F13: "F13";
			case KeyCode.F14: "F14";
			case KeyCode.F15: "F15";
			case KeyCode.F16: "F16";
			case KeyCode.F17: "F17";
			case KeyCode.F18: "F18";
			case KeyCode.F19: "F19";
			case KeyCode.F20: "F20";
			case KeyCode.F21: "F21";
			case KeyCode.F22: "F22";
			case KeyCode.F23: "F23";
			case KeyCode.F24: "F24";
			case KeyCode.NumLock: "NumLock";
			case KeyCode.ScrollLock: "ScrollLock";
			case KeyCode.WinOemFjJisho: "WinOemFjJisho";
			case KeyCode.WinOemFjMasshou: "WinOemFjMasshou";
			case KeyCode.WinOemFjTouroku: "WinOemFjTouroku";
			case KeyCode.WinOemFjLoya: "WinOemFjLoya";
			case KeyCode.WinOemFjRoya: "WinOemFjRoya";
			case KeyCode.Circumflex: "Circumflex";
			case KeyCode.Exclamation: "Exclamation";
			case KeyCode.DoubleQuote: "DoubleQuote";
			case KeyCode.Hash: "Hash";
			case KeyCode.Dollar: "Dollar";
			case KeyCode.Percent: "Percent";
			case KeyCode.Ampersand: "Ampersand";
			case KeyCode.Underscore: "Underscore";
			case KeyCode.OpenParen: "OpenParen";
			case KeyCode.CloseParen: "CloseParen";
			case KeyCode.Asterisk: "Asterisk";
			case KeyCode.Plus: "Plus";
			case KeyCode.Pipe: "Pipe";
			case KeyCode.HyphenMinus: "HyphenMinus";
			case KeyCode.OpenCurlyBracket: "OpenCurlyBracket";
			case KeyCode.CloseCurlyBracket: "CloseCurlyBracket";
			case KeyCode.Tilde: "Tilde";
			case KeyCode.VolumeMute: "VolumeMute";
			case KeyCode.VolumeDown: "VolumeDown";
			case KeyCode.VolumeUp: "VolumeUp";
			case KeyCode.Comma: "Comma";
			case KeyCode.Period: "Period";
			case KeyCode.Slash: "Slash";
			case KeyCode.BackQuote: "BackQuote";
			case KeyCode.OpenBracket: "OpenBracket";
			case KeyCode.BackSlash: "BackSlash";
			case KeyCode.CloseBracket: "CloseBracket";
			case KeyCode.Quote: "Quote";
			case KeyCode.Meta: "Meta";
			case KeyCode.AltGr: "AltGr";
			case KeyCode.WinIcoHelp: "WinIcoHelp";
			case KeyCode.WinIco00: "WinIco00";
			case KeyCode.WinIcoClear: "WinIcoClear";
			case KeyCode.WinOemReset: "WinOemReset";
			case KeyCode.WinOemJump: "WinOemJump";
			case KeyCode.WinOemPA1: "WinOemPA1";
			case KeyCode.WinOemPA2: "WinOemPA2";
			case KeyCode.WinOemPA3: "WinOemPA3";
			case KeyCode.WinOemWSCTRL: "WinOemWSCTRL";
			case KeyCode.WinOemCUSEL: "WinOemCUSEL";
			case KeyCode.WinOemATTN: "WinOemATTN";
			case KeyCode.WinOemFinish: "WinOemFinish";
			case KeyCode.WinOemCopy: "WinOemCopy";
			case KeyCode.WinOemAuto: "WinOemAuto";
			case KeyCode.WinOemENLW: "WinOemENLW";
			case KeyCode.WinOemBackTab: "WinOemBackTab";
			case KeyCode.ATTN: "ATTN";
			case KeyCode.CRSEL: "CRSEL";
			case KeyCode.EXSEL: "EXSEL";
			case KeyCode.EREOF: "EREOF";
			case KeyCode.Play: "Play";
			case KeyCode.Zoom: "Zoom";
			case KeyCode.PA1: "PA1";
			case KeyCode.WinOemClear: "WinOemClear";
		}
	}
}
