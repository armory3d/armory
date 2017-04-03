package armory.logicnode;

class GateNode extends Node {

	public var property0:String;

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function run() {

		var v1 = inputs[1].get();
		var v2 = inputs[2].get();
		var cond = false;

		switch (property0) {
		case "Equal":
			cond = v1 == v2;
		case "Not Equal":
			cond = v1 != v2;
		case "Greater":
			cond = v1 > v2;
		case "Greater Equal":
			cond = v1 >= v2;
		case "Less":
			cond = v1 < v2;
		case "Less Equal":
			cond = v1 <= v2;
		}

		if (cond) super.run();
	}
}
