package armory.logicnode;

class GetGroupNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var groupName: String = inputs[0].get();
		return iron.Scene.active.getGroup(groupName);
	}
}
