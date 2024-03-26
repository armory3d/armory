package armory.logicnode;

import armory.renderpath.Nishita;
import iron.math.Vec4;

class SetNishitaPropertiesNode extends LogicNode {

	public var property0:String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		var world = iron.Scene.active.world;

		if(property0 == 'Density'){
			world.raw.nishita_density[0] = inputs[1].get();
			world.raw.nishita_density[1] = inputs[2].get();
			world.raw.nishita_density[2] = inputs[3].get();
		}
		
		if(property0 == 'Air')
			world.raw.nishita_density[0] = inputs[1].get();

		if(property0 == 'Dust')
			world.raw.nishita_density[1] = inputs[1].get();

		if(property0 == 'Ozone')
			world.raw.nishita_density[2] = inputs[1].get();

		if(property0 == 'Sun Direction'){
			var vec:Vec4 = inputs[1].get();
			world.raw.sun_direction[0] = vec.x;
			world.raw.sun_direction[1] = vec.y;
			world.raw.sun_direction[2] = vec.z;
		}

		Nishita.recompute(world);

		runOutput(0);
		
	}
}
