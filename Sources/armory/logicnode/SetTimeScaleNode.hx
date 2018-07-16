package armory.logicnode;

class SetTimeScaleNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(node:LogicNode) {
		var f:Float = inputs[1].get();
		iron.system.Time.scale = f;
		super.run(this);
	}
}
