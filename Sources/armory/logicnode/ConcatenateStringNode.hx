package armory.logicnode;

class ConcatenateStringNode extends LogicNode {

	public var value:String;

	public function new(tree:LogicTree, value = "") {
		super(tree);
		this.value = value;
	}

	override function get(from:Int):Dynamic {
		if (inputs.length > 0) {
			value = "";
            for (i in 0...inputs.length) {
				value += inputs[i].get();
			}
			return value;
		}
		return value;
	}
}