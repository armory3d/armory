package armory.logicnode;

#if arm_navigation
import armory.trait.navigation.Navigation;
#end

import iron.object.Object;
import iron.math.Vec4;

class CrowdGoToLocationNode extends LogicNode {

	var object: Object;
	var location: Vec4;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		object = inputs[1].get();
		location = inputs[2].get();

		assert(Error, object != null, "The object input not be null");
		assert(Error, location != null, "The location to navigate to must not be null");

#if arm_navigation
		assert(Error, Navigation.active.navMeshes.length > 0, "No Navigation Mesh Present");
		var crowdAgent: armory.trait.NavCrowd = object.getTrait(armory.trait.NavCrowd);
		assert(Error, crowdAgent != null, "Object does not have a NavCrowd trait");
		crowdAgent.crowdAgentGoto(location);
#end
		runOutput(0);
	}
}
