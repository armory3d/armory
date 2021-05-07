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
		switch (keycode) {
			case -1: return "None";
			case KeyCode.Unknown: return "Unknown";
			case KeyCode.Back: return "Back";
			case KeyCode.Cancel: return "Cancel";
			case KeyCode.Help: return "Help";
			case KeyCode.Backspace: return "Backspace";
			case KeyCode.Tab: return "Tab";
			case KeyCode.Clear: return "Clear";
			case KeyCode.Return: return "Return";
			case KeyCode.Shift: return "Shift";
			case KeyCode.Control: return "Ctrl";
			case KeyCode.Alt: return "Alt";
			case KeyCode.Pause: return "Pause";
			case KeyCode.CapsLock: return "CapsLock";
			case KeyCode.Kana: return "Kana";
			// case KeyCode.Hangul: return "Hangul"; // Hangul == Kana
			case KeyCode.Eisu: return "Eisu";
			case KeyCode.Junja: return "Junja";
			case KeyCode.Final: return "Final";
			case KeyCode.Hanja: return "Hanja";
			// case KeyCode.Kanji: return "Kanji"; // Kanji == Hanja
			case KeyCode.Escape: return "Esc";
			case KeyCode.Convert: return "Convert";
			case KeyCode.NonConvert: return "NonConvert";
			case KeyCode.Accept: return "Accept";
			case KeyCode.ModeChange: return "ModeChange";
			case KeyCode.Space: return "Space";
			case KeyCode.PageUp: return "PageUp";
			case KeyCode.PageDown: return "PageDown";
			case KeyCode.End: return "End";
			case KeyCode.Home: return "Home";
			case KeyCode.Left: return "Left";
			case KeyCode.Up: return "Up";
			case KeyCode.Right: return "Right";
			case KeyCode.Down: return "Down";
			case KeyCode.Select: return "Select";
			case KeyCode.Print: return "Print";
			case KeyCode.Execute: return "Execute";
			case KeyCode.PrintScreen: return "PrintScreen";
			case KeyCode.Insert: return "Insert";
			case KeyCode.Delete: return "Delete";
			case KeyCode.Colon: return "Colon";
			case KeyCode.Semicolon: return "Semicolon";
			case KeyCode.LessThan: return "LessThan";
			case KeyCode.Equals: return "Equals";
			case KeyCode.GreaterThan: return "GreaterThan";
			case KeyCode.QuestionMark: return "QuestionMark";
			case KeyCode.At: return "At";
			case KeyCode.Win: return "Win";
			case KeyCode.ContextMenu: return "ContextMenu";
			case KeyCode.Sleep: return "Sleep";
			case KeyCode.Numpad0: return "Numpad0";
			case KeyCode.Numpad1: return "Numpad1";
			case KeyCode.Numpad2: return "Numpad2";
			case KeyCode.Numpad3: return "Numpad3";
			case KeyCode.Numpad4: return "Numpad4";
			case KeyCode.Numpad5: return "Numpad5";
			case KeyCode.Numpad6: return "Numpad6";
			case KeyCode.Numpad7: return "Numpad7";
			case KeyCode.Numpad8: return "Numpad8";
			case KeyCode.Numpad9: return "Numpad9";
			case KeyCode.Multiply: return "Multiply";
			case KeyCode.Add: return "Add";
			case KeyCode.Separator: return "Separator";
			case KeyCode.Subtract: return "Subtract";
			case KeyCode.Decimal: return "Decimal";
			case KeyCode.Divide: return "Divide";
			case KeyCode.F1: return "F1";
			case KeyCode.F2: return "F2";
			case KeyCode.F3: return "F3";
			case KeyCode.F4: return "F4";
			case KeyCode.F5: return "F5";
			case KeyCode.F6: return "F6";
			case KeyCode.F7: return "F7";
			case KeyCode.F8: return "F8";
			case KeyCode.F9: return "F9";
			case KeyCode.F10: return "F10";
			case KeyCode.F11: return "F11";
			case KeyCode.F12: return "F12";
			case KeyCode.F13: return "F13";
			case KeyCode.F14: return "F14";
			case KeyCode.F15: return "F15";
			case KeyCode.F16: return "F16";
			case KeyCode.F17: return "F17";
			case KeyCode.F18: return "F18";
			case KeyCode.F19: return "F19";
			case KeyCode.F20: return "F20";
			case KeyCode.F21: return "F21";
			case KeyCode.F22: return "F22";
			case KeyCode.F23: return "F23";
			case KeyCode.F24: return "F24";
			case KeyCode.NumLock: return "NumLock";
			case KeyCode.ScrollLock: return "ScrollLock";
			case KeyCode.WinOemFjJisho: return "WinOemFjJisho";
			case KeyCode.WinOemFjMasshou: return "WinOemFjMasshou";
			case KeyCode.WinOemFjTouroku: return "WinOemFjTouroku";
			case KeyCode.WinOemFjLoya: return "WinOemFjLoya";
			case KeyCode.WinOemFjRoya: return "WinOemFjRoya";
			case KeyCode.Circumflex: return "Circumflex";
			case KeyCode.Exclamation: return "Exclamation";
			case KeyCode.DoubleQuote: return "DoubleQuote";
			case KeyCode.Hash: return "Hash";
			case KeyCode.Dollar: return "Dollar";
			case KeyCode.Percent: return "Percent";
			case KeyCode.Ampersand: return "Ampersand";
			case KeyCode.Underscore: return "Underscore";
			case KeyCode.OpenParen: return "OpenParen";
			case KeyCode.CloseParen: return "CloseParen";
			case KeyCode.Asterisk: return "Asterisk";
			case KeyCode.Plus: return "Plus";
			case KeyCode.Pipe: return "Pipe";
			case KeyCode.HyphenMinus: return "HyphenMinus";
			case KeyCode.OpenCurlyBracket: return "OpenCurlyBracket";
			case KeyCode.CloseCurlyBracket: return "CloseCurlyBracket";
			case KeyCode.Tilde: return "Tilde";
			case KeyCode.VolumeMute: return "VolumeMute";
			case KeyCode.VolumeDown: return "VolumeDown";
			case KeyCode.VolumeUp: return "VolumeUp";
			case KeyCode.Comma: return "Comma";
			case KeyCode.Period: return "Period";
			case KeyCode.Slash: return "Slash";
			case KeyCode.BackQuote: return "BackQuote";
			case KeyCode.OpenBracket: return "OpenBracket";
			case KeyCode.BackSlash: return "BackSlash";
			case KeyCode.CloseBracket: return "CloseBracket";
			case KeyCode.Quote: return "Quote";
			case KeyCode.Meta: return "Meta";
			case KeyCode.AltGr: return "AltGr";
			case KeyCode.WinIcoHelp: return "WinIcoHelp";
			case KeyCode.WinIco00: return "WinIco00";
			case KeyCode.WinIcoClear: return "WinIcoClear";
			case KeyCode.WinOemReset: return "WinOemReset";
			case KeyCode.WinOemJump: return "WinOemJump";
			case KeyCode.WinOemPA1: return "WinOemPA1";
			case KeyCode.WinOemPA2: return "WinOemPA2";
			case KeyCode.WinOemPA3: return "WinOemPA3";
			case KeyCode.WinOemWSCTRL: return "WinOemWSCTRL";
			case KeyCode.WinOemCUSEL: return "WinOemCUSEL";
			case KeyCode.WinOemATTN: return "WinOemATTN";
			case KeyCode.WinOemFinish: return "WinOemFinish";
			case KeyCode.WinOemCopy: return "WinOemCopy";
			case KeyCode.WinOemAuto: return "WinOemAuto";
			case KeyCode.WinOemENLW: return "WinOemENLW";
			case KeyCode.WinOemBackTab: return "WinOemBackTab";
			case KeyCode.ATTN: return "ATTN";
			case KeyCode.CRSEL: return "CRSEL";
			case KeyCode.EXSEL: return "EXSEL";
			case KeyCode.EREOF: return "EREOF";
			case KeyCode.Play: return "Play";
			case KeyCode.Zoom: return "Zoom";
			case KeyCode.PA1: return "PA1";
			case KeyCode.WinOemClear: return "WinOemClear";
		}
		return String.fromCharCode(keycode);
	}
}
