package armory.logicnode;

class SetWorldStrengthNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		iron.Scene.active.world.raw.probe.strength = inputs[1].get();

		runOutput(0);
		
	}
}
