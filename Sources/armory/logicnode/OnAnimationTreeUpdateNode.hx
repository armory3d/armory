package armory.logicnode;

class OnAnimationTreeUpdateNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int):Dynamic {
		return function (value: Dynamic) {
			inputs[0].get()(value);
			runOutput(1);
		}
	}
}
