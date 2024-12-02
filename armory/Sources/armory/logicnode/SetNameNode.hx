package armory.logicnode;

import iron.object.Object;

class SetNameNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var name: String = inputs[2].get();

		if (object == null) return;

		#if arm_skin
		for(a in iron.Scene.active.animations)
			if(a.armature != null && a.armature.name == object.name)
				a.armature.name = name;
		#end

		object.name = name;

		runOutput(0);
	}
}
