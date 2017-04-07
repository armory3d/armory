package armory.logicnode;

import armory.trait.internal.Navigation;
import armory.object.Object;
import armory.math.Vec4;

class GoToLocationNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var location:Vec4 = inputs[2].get();
		
		if (location == null) return;
		if (object == null) object = tree.object;

#if arm_navigation
		// Assume navmesh exists..
		var from = object.transform.loc;
		var to = location;
		Navigation.active.navMeshes[0].findPath(from, to, function(path:Array<iron.math.Vec4>) {
			var agent:armory.trait.NavAgent = object.getTrait(armory.trait.NavAgent);
			agent.setPath(path);
		});
#end

		super.run();
	}
}
