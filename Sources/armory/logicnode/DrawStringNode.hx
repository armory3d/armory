package armory.logicnode;

import kha.Font;
import kha.Color;
import armory.renderpath.RenderToTexture;

#if arm_ui
import armory.ui.Canvas;
#end

class DrawStringNode extends LogicNode {
	var font: Font;
	var lastFontName = "";

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawStringNode");

		var string:String = Std.string(inputs[1].get());
		var fontName = inputs[2].get();
		if (fontName == "") {
			#if arm_ui
			fontName = Canvas.defaultFontName;
			#else
			return; // No default font is exported, there is nothing we can do here
			#end
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
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		RenderToTexture.g.fontSize = inputs[3].get();
		RenderToTexture.g.font = font;

		RenderToTexture.g.drawString(string, inputs[5].get(), inputs[6].get());

		runOutput(0);
	}
}
