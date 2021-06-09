package armory.logicnode;

import iron.Scene;
import iron.math.Vec4;
import iron.data.MaterialData;
import iron.object.Object;
import armory.trait.internal.UniformsManager;

class SetMaterialRgbParamNode extends LogicNode {

	public var property0: Bool; // per object
	
	var manager: UniformsManager;

	public function new(tree: LogicTree) {
		super(tree);

		manager = new UniformsManager(UniformType.Vector);
	}

	override function run(from: Int) {
		var object = inputs[1].get();
		if(object == null) return;

		var mat = inputs[2].get();
		if(mat == null) return;

		if(! property0){
			object = Scene.active.root;
		}

		manager.setVec3Value(mat, object, inputs[3].get(), inputs[4].get());
		runOutput(0);
	}
}
