package armory.logicnode;

import iron.object.Object;

class AddObjectToGroupNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var groupName: String = inputs[1].get();
		var object: Object = inputs[2].get();

		iron.Scene.active.getGroup(groupName).push(object);
		
		runOutput(0);

	}
}
