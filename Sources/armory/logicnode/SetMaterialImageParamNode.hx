package armory.logicnode;

import iron.Scene;
import iron.data.MaterialData;
import iron.object.Object;
import armory.trait.internal.UniformsManager;

class SetMaterialImageParamNode extends LogicNode {

	public var property0: Bool; // per object
	
	var manager: UniformsManager;

	public function new(tree: LogicTree) {
		super(tree);

		manager = new UniformsManager(UniformType.Texture);
	}

	override function run(from: Int) {
		var object = inputs[1].get();
		if(object == null) return;

		var mat = inputs[2].get();
		if(mat == null) return;

		if(! property0){
			object = Scene.active.root;
		}

		manager.setTextureValue(mat, object, inputs[3].get(), inputs[4].get());
		runOutput(0);
	}
}
