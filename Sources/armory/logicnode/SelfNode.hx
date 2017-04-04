package armory.logicnode;

class SelfNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic { return tree.object; }
}
