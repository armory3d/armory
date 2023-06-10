package armory.logicnode;

import iron.Scene;
import iron.data.MaterialData;
import iron.object.Object;
import armory.trait.internal.UniformsManager;

class SetMaterialValueParamNode extends LogicNode {
	
	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object;
		var perObject: Null<Bool>;
		var mat: MaterialData;
		var link: String;
		var value: Null<kha.FastFloat>;
		
		object = inputs[1].get();
		if(object == null) return;

		perObject = inputs[2].get();
		if(perObject == null) perObject = false;

		mat = inputs[3].get();
		if(mat == null) return;

		link = inputs[4].get();
		if(link == null) return;

		value = inputs[5].get();
		if(value == null) return;

		if(! perObject){
			UniformsManager.removeFloatValue(object, mat, link);
			object = Scene.active.root;
		}

		UniformsManager.setFloatValue(mat, object, inputs[4].get(), value);
		runOutput(0);
	}

}
