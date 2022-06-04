package armory.logicnode;

import kha.Font;
import kha.Color;


class DrawStringNode extends LogicNode {

	var font:Font;
	var w: Int;
	var h: Int;

	public function new(tree: LogicTree) {
		super(tree);

	}

	override function run(from: Int) {
	
		w = iron.App.w();
		h = iron.App.h();
				
		iron.data.Data.getFont(inputs[3].get(), function(f:kha.Font){ font =f; });
		
		tree.notifyOnRender2D(render2D);
		
		runOutput(0);
		
	}
	
	function render2D(g:kha.graphics2.Graphics) {
		
		if(inputs[1].get()){
		
			var sw = iron.App.w()/w;
			var sh = iron.App.h()/h;
		
			g.color = Color.fromFloats(inputs[5].get().x, inputs[5].get().y, inputs[5].get().z, inputs[5].get().w);
			g.fontSize = Std.int(inputs[4].get()*((sw+sh)/2));
			g.font = font;
			
			g.drawString(inputs[2].get(), inputs[6].get()*sw, inputs[7].get()*sh);
			
		}

	}
		
}