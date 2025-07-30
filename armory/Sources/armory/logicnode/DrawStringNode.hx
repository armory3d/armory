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
	var string:String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawStringNode");

		string = Std.string(inputs[1].get());
		var angle: Float = inputs[7].get();

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

		RenderToTexture.g.rotate(angle, inputs[5].get(), inputs[6].get());

		final colorVec = inputs[4].get();
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		RenderToTexture.g.fontSize = inputs[3].get();
		RenderToTexture.g.font = font;

		RenderToTexture.g.drawString(string, inputs[5].get(), inputs[6].get());

		RenderToTexture.g.rotate(-angle, inputs[5].get(), inputs[6].get());

		runOutput(0);
	}

	override function get(from: Int): Dynamic {

		return from == 1 ? RenderToTexture.g.font.width(RenderToTexture.g.fontSize, string) : RenderToTexture.g.font.height(RenderToTexture.g.fontSize);
	
	}
}
