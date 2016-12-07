package armory.logicnode;

import iron.math.Vec4;

class LocationNode extends Node {
	
	public var loc:Vec4 = null;

	public function new() {
		super();
		loc = new Vec4();
	}

	public static function create():LocationNode {
		var n = new LocationNode();
		return n;
	}
}
