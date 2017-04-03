package armory.logicnode;

import armory.trait.internal.Navigation;

class GoToLocationNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function run() {
		var object = inputs[1].get();
		var location = inputs[2].get();
		
		if (location == null) return;
		if (object == null) object = trait.object;

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
