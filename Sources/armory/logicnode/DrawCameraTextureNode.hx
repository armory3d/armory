package armory.logicnode;

import iron.Scene;
import iron.object.CameraObject;
import armory.renderpath.RenderPathCreator;

class DrawCameraTextureNode extends LogicNode {

	var cam: CameraObject;
	var cami: CameraObject;

	public function new(tree: LogicTree) {
		super(tree);

	}

	override function run(from: Int) {

		cami = iron.Scene.active.camera;
		cam = inputs[2].get();
		
		cam.renderTarget = kha.Image.createRenderTarget(
				iron.App.w(),
				iron.App.h()
		);
			
		var o = cast(inputs[3].get(), iron.object.MeshObject);
		o.materials[inputs[4].get()].contexts[0].textures[0] = cam.renderTarget;
		
		tree.notifyOnRender(render);	
		
		runOutput(0);
			
	}
	
	function render(g:kha.graphics4.Graphics) {
		
		if(inputs[1].get()){
			iron.Scene.active.camera = cam;
			cam.renderFrame(g);
		} 

		iron.Scene.active.camera = cami;

	}
		
}