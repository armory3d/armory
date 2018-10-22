package armory.logicnode;

class AddGroupNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var groupName:String = inputs[1].get();
		
		if (iron.Scene.active.groups.get(groupName) == null) {
			iron.Scene.active.groups.set(groupName, []);
		}

		runOutput(0);
	}
}
