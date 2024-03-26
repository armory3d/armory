package armory.logicnode;

import armory.renderpath.HosekWilkie;
import iron.math.Vec4;

class SetHosekWilkiePropertiesNode extends LogicNode {

	public var property0:String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		var world = iron.Scene.active.world;

		if(property0 == 'Turbidity/Ground Albedo'){
			world.raw.turbidity = inputs[1].get();
			world.raw.ground_albedo = inputs[2].get();
		}

		if(property0 == 'Turbidity')
			world.raw.turbidity = inputs[1].get();
		
		if(property0 == 'Ground Albedo')
			world.raw.ground_albedo = inputs[1].get();

		if(property0 == 'Sun Direction'){
			var vec:Vec4 = inputs[1].get();
			world.raw.sun_direction[0] = vec.x;
			world.raw.sun_direction[1] = vec.y;
			world.raw.sun_direction[2] = vec.z;
		}

		HosekWilkie.recompute(world);

		runOutput(0);
		
	}
}
