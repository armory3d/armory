package zui;

class Themes {

	public static var dark: TTheme = {
		NAME: "Default Dark",
		WINDOW_BG_COL: 0xff292929,
		WINDOW_TINT_COL: 0xffffffff,
		ACCENT_COL: 0xff393939,
		ACCENT_HOVER_COL: 0xff434343,
		ACCENT_SELECT_COL: 0xff505050,
		BUTTON_COL: 0xff383838,
		BUTTON_TEXT_COL: 0xffe8e7e5,
		BUTTON_HOVER_COL: 0xff494949,
		BUTTON_PRESSED_COL: 0xff1b1b1b,
		TEXT_COL: 0xffe8e7e5,
		LABEL_COL: 0xffc8c8c8,
		SEPARATOR_COL: 0xff202020,
		HIGHLIGHT_COL: 0xff205d9c,
		CONTEXT_COL: 0xff222222,
		PANEL_BG_COL: 0xff3b3b3b,
		FONT_SIZE: 13,
		ELEMENT_W: 100,
		ELEMENT_H: 24,
		ELEMENT_OFFSET: 4,
		ARROW_SIZE: 5,
		BUTTON_H: 22,
		CHECK_SIZE: 15,
		CHECK_SELECT_SIZE: 8,
		SCROLL_W: 9,
		TEXT_OFFSET: 8,
		TAB_W: 6,
		FILL_WINDOW_BG: false,
		FILL_BUTTON_BG: true,
		FILL_ACCENT_BG: false,
		LINK_STYLE: Line,
		FULL_TABS: false
	};
}

typedef TTheme = {
	var NAME: String;
	var WINDOW_BG_COL: Int;
	var WINDOW_TINT_COL: Int;
	var ACCENT_COL: Int;
	var ACCENT_HOVER_COL: Int;
	var ACCENT_SELECT_COL: Int;
	var BUTTON_COL: Int;
	var BUTTON_TEXT_COL: Int;
	var BUTTON_HOVER_COL: Int;
	var BUTTON_PRESSED_COL: Int;
	var TEXT_COL: Int;
	var LABEL_COL: Int;
	var SEPARATOR_COL: Int;
	var HIGHLIGHT_COL: Int;
	var CONTEXT_COL: Int;
	var PANEL_BG_COL: Int;
	var FONT_SIZE: Int;
	var ELEMENT_W: Int;
	var ELEMENT_H: Int;
	var ELEMENT_OFFSET: Int;
	var ARROW_SIZE: Int;
	var BUTTON_H: Int;
	var CHECK_SIZE: Int;
	var CHECK_SELECT_SIZE: Int;
	var SCROLL_W: Int;
	var TEXT_OFFSET: Int;
	var TAB_W: Int; // Indentation
	var FILL_WINDOW_BG: Bool;
	var FILL_BUTTON_BG: Bool;
	var FILL_ACCENT_BG: Bool;
	var LINK_STYLE: LinkStyle;
	var FULL_TABS: Bool; // Make tabs take full window width
}

@:enum abstract LinkStyle(Int) from Int {
	var Line = 0;
	var CubicBezier = 1;
}
