package armory.logicnode;

import iron.Scene;
import iron.object.CameraObject;
import armory.renderpath.RenderPathCreator;

class DrawCameraNode extends LogicNode {

	var cam: Array<CameraObject> = [];
	var x: Array<Int> = [];
	var y: Array <Int> = [];
	var cami: CameraObject;
	
	var w: Int;
	var h: Int;

	public function new(tree: LogicTree) {
		super(tree);

	}

	override function run(from: Int) {
	
		w = iron.App.w();
		h = iron.App.h();
	
		cami = iron.Scene.active.camera;
		
		for(i in 0...Std.int((inputs.length-2)/5)){
		
			cam.push(inputs[(i*5+2)].get());
			
			x.push(inputs[(i*5+3)].get()); //x
			y.push(inputs[(i*5+4)].get()); //y
			
			cam[i].renderTarget = kha.Image.createRenderTarget(
				inputs[(i*5+5)].get(), //w
				inputs[(i*5+6)].get(), //h
				kha.graphics4.TextureFormat.RGBA32,
				kha.graphics4.DepthStencilFormat.NoDepthAndStencil
			);
			
		}
		
		tree.notifyOnRender2D(render2D);
		tree.notifyOnRender(render);	
		
		runOutput(0);
			
	}
	
	function render2D(g:kha.graphics2.Graphics) {
	
		var sw = iron.App.w()/w;
		var sh = iron.App.h()/h;
		
		if(inputs[1].get())
			for(i in 0...cam.length){
				var img = cam[i].renderTarget;
				g.color = 0xff000000;
				g.fillRect(x[i]*sw, y[i]*sh, img.width*sw, img.height*sh);
				g.color = 0xffffffff;
				g.drawScaledImage(img, x[i]*sw, y[i]*sh, img.width*sw, img.height*sh);
			}

	}
	
	function render(g:kha.graphics4.Graphics) {
	
		if(inputs[1].get())
			for(c in cam){
				iron.Scene.active.camera = c;
				c.renderFrame(g);
			} 

		iron.Scene.active.camera = cami;


	}
		
}