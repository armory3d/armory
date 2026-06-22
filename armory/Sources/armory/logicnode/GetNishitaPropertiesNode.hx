package armory.logicnode;

import iron.math.Vec4;

class GetNishitaPropertiesNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		
	var world = iron.Scene.active.world.raw;

		return switch (from) {
			case 0:
				world.nishita_density[0];
			case 1:
				world.nishita_density[1];
			case 2:
				world.nishita_density[2];
			case 3:
				new Vec4(world.sun_direction[0], world.sun_direction[1], world.sun_direction[2]);
			default: 
				null;
		}
		return null;
	}
}