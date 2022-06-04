package armory.logicnode;

import kha.Color;
import kha.math.Vector2;

class DrawPolygonNode extends LogicNode {

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
			
			var vertices: Array<Vector2> = [];
			
			for(v in 0...Std.int((inputs.length-6)/2))
				vertices.push({x: inputs[(6+(v*2+1))].get()*sw, y: inputs[(6+(v*2+2))].get()*sh});
			
			g.color = Color.fromFloats(inputs[3].get().x, inputs[3].get().y, inputs[3].get().z, inputs[3].get().w);
			
			if(inputs[2].get())
				kha.graphics2.GraphicsExtension.fillPolygon(g, inputs[5].get()*sw, inputs[6].get()*sh, vertices);
			else
				kha.graphics2.GraphicsExtension.drawPolygon(g, inputs[5].get()*sw, inputs[6].get()*sh, vertices, inputs[4].get()*(sw+sh)/2);
		
		}

	}
		
}