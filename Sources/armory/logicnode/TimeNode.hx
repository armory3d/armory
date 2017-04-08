package armory.logicnode;

class TimeNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		return armory.system.Time.time();
	}
}
