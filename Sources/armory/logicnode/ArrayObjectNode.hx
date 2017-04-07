package armory.logicnode;

import armory.object.Object;

class ArrayObjectNode extends Node {

	public var value:Array<Object> = [];
	var initialized = false;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		if (!initialized) {
			initialized = true;
			for (inp in inputs) {
				var val:Object = inp.get();
				value.push(val);
			}
		}

		return from == 0 ? value : value.length;
	}

	override function set(value:Dynamic) {
		this.value = value;
	}
}
