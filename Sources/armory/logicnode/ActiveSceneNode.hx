package armory.logicnode;

class ActiveSceneNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic { return iron.Scene.active.raw.name; }
}
