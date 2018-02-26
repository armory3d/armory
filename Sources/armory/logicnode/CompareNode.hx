package armory.logicnode;

class CompareNode extends LogicNode {

	public var property0:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Bool {

		var v1:Dynamic = inputs[0].get();
		var v2:Dynamic = inputs[1].get();
		var r:Bool = false;
		switch (property0) {
		case "Equal":
			r = v1 == v2;
		case "Not Equal":
			r = v1 != v2;
		case "Less Than":
			r = v1 < v2;
		case "Less Than or Equal":
			r = v1 <= v2;
		case "Greater Than":
			r = v1 > v2;
		case "Greater Than or Equal":
			r = v1 >= v2;
		}

		return r;
	}
}
