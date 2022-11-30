package armory.logicnode;

import iron.Scene;
import iron.math.Vec4;
import iron.data.MaterialData;
import iron.object.Object;
import armory.trait.internal.UniformsManager;

class SetMaterialRgbParamNode extends LogicNode {
	
	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object;
		var perObject: Null<Bool>;
		var mat: MaterialData;
		var link: String;
		var vec: Vec4;
		
		object = inputs[1].get();
		if(object == null) return;

		perObject = inputs[2].get();
		if(perObject == null) perObject = false;

		mat = inputs[3].get();
		if(mat == null) return;

		link = inputs[4].get();
		if(link == null) return;

		vec = inputs[5].get();
		if(vec == null) return;

		if(! perObject){
			UniformsManager.removeVectorValue(object, mat, link);
			object = Scene.active.root;
		}

		UniformsManager.setVec3Value(mat, object, inputs[4].get(), vec);
		runOutput(0);
	}
}
