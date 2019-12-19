package armory.logicnode;

class RemoveActiveSceneNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		iron.Scene.active.remove();
		runOutput(0);
	}
}
