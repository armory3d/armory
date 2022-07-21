package armory.logicnode;

import kha.Font;
import kha.Color;

import armory.ui.Canvas;


class DrawStringNode extends LogicNode {
	var font: Font;
	var lastFontName = "";

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		OnRender2DNode.ensure2DContext("DrawStringNode");

		var fontName = inputs[2].get();
		if (fontName == "") {
			fontName = Canvas.defaultFontName;
		}

		if (fontName != lastFontName) {
			// Load new font
			lastFontName = fontName;
			iron.data.Data.getFont(fontName, (f: Font) -> {
				font = f;
			});
		}

		if (font == null) {
			runOutput(0);
			return;
		}

		final colorVec = inputs[4].get();
		OnRender2DNode.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		OnRender2DNode.g.fontSize = inputs[3].get();
		OnRender2DNode.g.font = font;

		OnRender2DNode.g.drawString(inputs[1].get(), inputs[5].get(), inputs[6].get());

		runOutput(0);
	}
}
