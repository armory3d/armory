package armory.logicnode;

import armory.math.Vec4;

class ArrayColorNode extends Node {

	public var value:Array<Vec4> = [];
	var initialized = false;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		if (!initialized) {
			initialized = true;
			for (inp in inputs) {
				var val:Vec4 = inp.get();
				value.push(val);
			}
		}

		return from == 0 ? value : value.length;
	}

	override function set(value:Dynamic) {
		this.value = value;
	}
}
