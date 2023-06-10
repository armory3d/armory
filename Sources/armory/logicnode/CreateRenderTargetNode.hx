package armory.logicnode;

import kha.Image;
import kha.graphics4.TextureFormat;
import iron.Scene;
import iron.data.MaterialData;
import iron.object.Object;
import armory.trait.internal.UniformsManager;

class CreateRenderTargetNode extends LogicNode {
	
	public function new(tree: LogicTree) {
		super(tree);

	}

	override function run(from: Int) {
		var perObject: Null<Bool>;
		
		var object = inputs[1].get();
		if(object == null) return;

		perObject = inputs[2].get();
		if(perObject == null) perObject = false;

		var mat = inputs[3].get();
		if(mat == null) return;

		if(! perObject){
			UniformsManager.removeTextureValue(object, mat, inputs[4].get());
			object = Scene.active.root;
		}

		var img = Image.createRenderTarget(inputs[5].get(), inputs[6].get(), TextureFormat.RGBA32);
		UniformsManager.setTextureValue(mat, object, inputs[4].get(), img);

		runOutput(0);
	}
}
