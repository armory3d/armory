package armory.logicnode;

import kha.Color;

class DrawCurveNode extends LogicNode {

	var w: Int;
	var h: Int;
	
	public function new(tree: LogicTree) {
		super(tree);

	}

	override function run(from: Int) {
	
		w = iron.App.w();
		h = iron.App.h();
				
		tree.notifyOnRender2D(render2D);
		
		runOutput(0);

	}
	
	function render2D(g:kha.graphics2.Graphics) {
		
		if(inputs[1].get()){
		
			var sw = iron.App.w()/w;
			var sh = iron.App.h()/h;
			
			g.color = Color.fromFloats(inputs[2].get().x, inputs[2].get().y, inputs[2].get().z, inputs[2].get().w);
			kha.graphics2.GraphicsExtension.drawCubicBezier(g, 
			[inputs[5].get()*sw, inputs[7].get()*sw, inputs[9].get()*sw, inputs[11].get()*sw],
			[inputs[6].get()*sh, inputs[8].get()*sh, inputs[10].get()*sh, inputs[12].get()*sh], inputs[4].get(), inputs[3].get()*((sw+sh)/2));

		}

	}
		
}