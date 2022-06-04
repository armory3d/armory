package armory.logicnode;

import kha.Color;

class DrawCircleNode extends LogicNode {

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
			
			g.color = Color.fromFloats(inputs[3].get().x, inputs[3].get().y, inputs[3].get().z, inputs[3].get().w);
			if(inputs[2].get())
				kha.graphics2.GraphicsExtension.fillCircle(g, inputs[5].get()*sw, inputs[6].get()*sh, inputs[7].get()*(sw+sh)/2, inputs[8].get());
			else
				kha.graphics2.GraphicsExtension.drawCircle(g, inputs[5].get()*sw, inputs[6].get()*sh, inputs[7].get()*(sw+sh)/2, inputs[4].get()*(sw+sh)/2, inputs[8].get());

		}

	}
		
}