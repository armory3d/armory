package armory.logicnode;

class GetWorldStrengthNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		return iron.Scene.active.world.raw.probe.strength;
	}
}