package armory.logicnode;

import kha.Color;

class DrawLineNode extends LogicNode {

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
			g.drawLine(inputs[4].get()*sw, inputs[5].get()*sh, inputs[6].get()*sw, inputs[7].get()*sh, inputs[3].get());

		}

	}
		
}