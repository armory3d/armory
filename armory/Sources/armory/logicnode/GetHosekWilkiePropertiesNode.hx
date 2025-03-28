package armory.logicnode;

import iron.math.Vec4;

class GetHosekWilkiePropertiesNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {

		var world = iron.Scene.active.world.raw;

		return switch (from) {
			case 0:
				world.turbidity;
			case 1:
				world.ground_albedo;
			case 2:
				new Vec4(world.sun_direction[0], world.sun_direction[1], world.sun_direction[2]);
			default: 
				null;
		}
		return null;
	}
}