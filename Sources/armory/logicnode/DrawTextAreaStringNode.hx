package armory.logicnode;

import kha.Font;
import kha.Color;
import armory.renderpath.RenderToTexture;

import kha.graphics2.VerTextAlignment;
import kha.graphics2.HorTextAlignment;

using kha.graphics2.GraphicsExtension;

#if arm_ui
import armory.ui.Canvas;
#end

class DrawTextAreaStringNode extends LogicNode {
	var font: Font;
	var lastFontName = "";
	
	public var property0: String;
	public var property1: String;
	public var property2: String;
	
	var index: Int;
	var max: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawTextAreaStringNode");

		var string:String = Std.string(inputs[1].get());
		var length:Int = inputs[3].get();
		
		var horA = TextLeft;
		var verA = TextTop;
		
		
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
		
		
		//mi codigo
		
		var len = string.length;
		
		var ar_lines = [];
		
		var ar_words = string.split(' ');
		
		if(property0 == 'Lines')
			max = Std.int(len/length);
		else max = length;
		
		while(ar_words.length > 0){
			var str_line = '';
			
				while(str_line.length < max && ar_words.length > 0){
					str_line +=' '+ar_words.shift();
				}
				
			ar_lines.push(str_line);
		
		}
		
		var spacing = inputs[4].get();

		final colorVec = inputs[6].get();
		final colorVecB = inputs[7].get();

		RenderToTexture.g.fontSize = inputs[5].get();
		RenderToTexture.g.font = font;
		
		index = 0;
		
		var height = RenderToTexture.g.font.height(RenderToTexture.g.fontSize);
		
		var yoffset = 0.0;
		
		switch(property2){
			case 'TextTop': verA = TextTop; 
			case 'TextMiddle': { verA = TextMiddle; yoffset = -height * 0.5; }
			case 'TextBottom': { verA = TextBottom; yoffset = -height; }
		}

		
		for (line in ar_lines){
		
			var width = RenderToTexture.g.font.width(RenderToTexture.g.fontSize, line);
			
			var xoffset = 0.0;
			
			switch(property1){
				case 'TextLeft': horA = TextLeft;
				case 'TextCenter': {horA = TextCenter; xoffset = -width * 0.5; }
				case 'TextRight': {horA = TextRight;  xoffset = -width; }
			}

			RenderToTexture.g.color = Color.fromFloats(colorVecB.x, colorVecB.y, colorVecB.z, colorVecB.w);
			
			RenderToTexture.g.fillRect(inputs[8].get()+xoffset, inputs[9].get()+yoffset+index*height*spacing, width, height);
			
			RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);
			
			RenderToTexture.g.drawAlignedString(line, inputs[8].get(), inputs[9].get()+index*height*spacing, horA, verA);
			++index;
			
		}
		
		runOutput(0);
	}
}