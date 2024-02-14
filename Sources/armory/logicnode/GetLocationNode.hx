package armory.logicnode;

import iron.object.Object;

class GetLocationNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();
		var relative: Bool = inputs[1].get();

		return GetObjectLocation(  object, relative );
	}

	//STATIC CLASS
	public static function GetObjectLocation(  object : Object, relative : Bool  ) {
	
		if (object == null) return null;
	
		var loc = object.transform.world.getLoc();
	
		if (relative && object.parent != null) {
			loc.sub(object.parent.transform.world.getLoc()); // Add parent location influence
	
			// Convert loc to parent local space
			var dotX:Float = loc.dot(object.parent.transform.right());
			var dotY:Float = loc.dot(object.parent.transform.look());
			var dotZ:Float = loc.dot(object.parent.transform.up());
			loc.set(dotX, dotY, dotZ);
		}
	
		return loc;
	}
}
