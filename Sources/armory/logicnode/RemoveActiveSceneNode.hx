package armory.logicnode;

class RemoveActiveSceneNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(node:LogicNode) {

		iron.Scene.active.remove();
		runOutputs(0);
	}
}
