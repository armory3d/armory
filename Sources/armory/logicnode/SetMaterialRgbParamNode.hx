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
		var perObject: Null<Bool>;
		
		var object = inputs[1].get();
		if(object == null) return;

		perObject = inputs[2].get();
		if(perObject == null) perObject = false;

		var mat = inputs[3].get();
		if(mat == null) return;

		if(! perObject){
			UniformsManager.removeObjectFromMap(object, Vector);
			object = Scene.active.root;
		}

		UniformsManager.setVec3Value(mat, object, inputs[4].get(), inputs[5].get());
		runOutput(0);
	}
}
