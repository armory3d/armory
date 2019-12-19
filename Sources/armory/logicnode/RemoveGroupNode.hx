package armory.logicnode;

class RemoveGroupNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var groupName: String = inputs[1].get();
		var raw = iron.Scene.active.raw;

		for (g in raw.groups) {
			if (g.name == groupName) {
				raw.groups.remove(g);
				@:privateAccess iron.Scene.active.groups.remove(groupName);
				break;
			}
		}

		runOutput(0);
	}
}
