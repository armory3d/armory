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
		var object: Object;
		var perObject: Null<Bool>;
		var mat: MaterialData;
		var link: String;
		var img: String;
		
		object = inputs[1].get();
		if(object == null) return;

		perObject = inputs[2].get();
		if(perObject == null) perObject = false;

		mat = inputs[3].get();
		if(mat == null) return;

		link = inputs[4].get();
		if(link == null) return;

		img = inputs[5].get();
		if(img == null) return;

		if(! perObject){
			UniformsManager.removeTextureValue(object, mat, link);
			object = Scene.active.root;
		}

		iron.data.Data.getImage(img, function(image: kha.Image) {
			UniformsManager.setTextureValue(mat, object, inputs[4].get(), image);
		});
		
		runOutput(0);
	}
}
