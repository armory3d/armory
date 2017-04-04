package armory.logicnode;

class NullNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic { return null; }
}
