package armory.ui;

import zui.Zui;
import kha.System;

@:access(zui.Zui)
class Popup {
	public static var show = false;

	static var ui: Zui = null;
	static var hwnd = new Handle();
	static var boxTitle = "";
	static var boxText = "";
	static var boxCommands: Zui->Void = null;
	static var modalX = 0;
	static var modalY = 0;
	static var modalW = 400;
	static var modalH = 160;

	public static function render(g: kha.graphics2.Graphics) {
		if (boxCommands == null) {
			ui.begin(g);
			if (ui.window(hwnd, modalX, modalY, modalW, modalH)) {
				drawTitle(g);

				for (line in boxText.split("\n")) {
					ui.text(line);
				}

				ui._y = ui._h - ui.t.BUTTON_H - 10;
				ui.row([1/3, 1/3, 1/3]);
				ui.endElement();
				if (ui.button("OK")) {
					show = false;
				}
			}
			ui.end();
		}
		else {
			ui.begin(g);
			if (ui.window(hwnd, modalX, modalY, modalW, modalH)) {
				drawTitle(g);

				ui._y += 10;
				boxCommands(ui);
			}
			ui.end();
		}
	}

	public static function drawTitle(g: kha.graphics2.Graphics) {
		if (boxTitle != "") {
			g.color = ui.t.SEPARATOR_COL;
			ui.drawRect(g, true, ui._x, ui._y, ui._w, ui.t.BUTTON_H);

			g.color = ui.t.TEXT_COL;
			ui.text(boxTitle);
		}
	}

	public static function update() {
		var inUse = ui.comboSelectedHandle != null;

		// Close popup
		if (ui.inputStarted && !inUse) {
			if (ui.inputX < modalX || ui.inputX > modalX + modalW || ui.inputY < modalY || ui.inputY > modalY + modalH) {
				show = false;
			}
		}
	}

	/**
		Displays a message box with a title, a text body and a centered "OK" button.
		@param ui    the Zui instance for the popup
		@param title the title to display
		@param text  the text to display
	**/
	public static function showMessage(ui: Zui, title: String, text: String) {
		Popup.ui = ui;
		init();

		boxTitle = title;
		boxText = text;
		boxCommands = null;
	}

	/**
		Displays a popup box with custom drawing code.
		@param ui       the Zui instance for the popup
		@param commands the function for drawing the popup's content
		@param mx       the x position of the popup. -1 = screen center (defaults to -1)
		@param my       the y position of the popup. -1 = screen center (defaults to -1)
		@param mw       the width of the popup (defaults to 400)
		@param mh       the height of the popup (defaults to 160)
	**/
	public static function showCustom(ui: Zui, commands: Zui->Void = null, mx = -1, my = -1, mw = 400, mh = 160) {
		Popup.ui = ui;
		init(mx, my, mw, mh);

		boxTitle = "";
		boxText = "";
		boxCommands = commands;
	}

	static function init(mx = -1, my = -1, mw = 400, mh = 160) {
		var appW = System.windowWidth();
		var appH = System.windowHeight();

		modalX = mx;
		modalY = my;
		modalW = Std.int(mw * ui.SCALE());
		modalH = Std.int(mh * ui.SCALE());

		// Center popup window if no value is given
		if (mx == -1) modalX = Std.int(appW / 2 - modalW / 2);
		if (my == -1) modalY = Std.int(appH / 2 - modalH / 2);

		// Limit popup position to screen
		modalX = Std.int(Math.max(0, Math.min(modalX, appW - modalW)));
		modalY = Std.int(Math.max(0, Math.min(modalY, appH - modalH)));

		hwnd.dragX = 0;
		hwnd.dragY = 0;
		hwnd.scrollOffset = 0.0;
		show = true;
	}
}
