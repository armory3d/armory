package armory.logicnode;

import kha.Image;
import kha.Color;

class DrawImageSequenceNode extends LogicNode {

	var img: Array<Image> = [];
	var w: Int;
	var h: Int;
	var timer: haxe.Timer;
	var t = 0;
	
	public function new(tree: LogicTree) {
		super(tree);

	}

	override function run(from: Int) {
	
		w = iron.App.w();
		h = iron.App.h();
		
		timer = new haxe.Timer(inputs[6].get());				
			
		for(i in inputs[4].get()...inputs[5].get()+1){
		//trace(inputs[2].get()+i+'.png');
			iron.data.Data.getImage(inputs[2].get()+i+'.'+inputs[3].get(), function(image:kha.Image) { img.push(image); });
		}
		
		tree.notifyOnRender2D(render2D);

		runOutput(0);

	}
	
	function render2D(g:kha.graphics2.Graphics) {
		
		if(inputs[1].get()){
		
			var sw = iron.App.w()/w;
			var sh = iron.App.h()/h;
			
			g.color = Color.fromFloats(inputs[8].get().x, inputs[8].get().y, inputs[8].get().z, inputs[8].get().w);	
			
			timer.run = function(){
				++t;
			if(t == img.length)
				if(inputs[7].get()) t = 0; else { timer.stop();	t = img.length-1; }		
			}
			
			g.drawScaledImage(img[t], inputs[9].get()*sw, inputs[10].get()*sh, inputs[11].get()*sw, inputs[12].get()*sh);

		}

	}
		
}