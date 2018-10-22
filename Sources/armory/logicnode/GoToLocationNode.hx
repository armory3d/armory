package armory.logicnode;

import armory.trait.navigation.Navigation;
import iron.object.Object;
import iron.math.Vec4;

class GoToLocationNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var location:Vec4 = inputs[2].get();
		
		if (object == null || location == null) return;

#if arm_navigation
		// Assume navmesh exists..
		var from = object.transform.world.getLoc();
		var to = location;
		Navigation.active.navMeshes[0].findPath(from, to, function(path:Array<iron.math.Vec4>) {
			var agent:armory.trait.NavAgent = object.getTrait(armory.trait.NavAgent);
			agent.setPath(path);
		});
#end

		runOutput(0);
	}
}
