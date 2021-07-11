package armory.logicnode;

import iron.Scene;
import iron.data.MaterialData;
import iron.object.Object;
import armory.trait.internal.UniformsManager;

class SetMaterialImageParamNode extends LogicNode {
	
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
			UniformsManager.removeObjectFromMap(object, Texture);
			object = Scene.active.root;
		}

		var img = inputs[5].get();
		if(img == null) return;
		iron.data.Data.getImage(img, function(image: kha.Image) {
			UniformsManager.setTextureValue(mat, object, inputs[4].get(), image);
		});
		
		runOutput(0);
	}
}
