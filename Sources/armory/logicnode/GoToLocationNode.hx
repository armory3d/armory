package armory.logicnode;

import armory.trait.navigation.Navigation;
import iron.object.Object;
import iron.math.Vec4;

class GoToLocationNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var location: Vec4 = inputs[2].get();
		var speed: Float = inputs[3].get();
		var turnDuration: Float = inputs[4].get();

		assert(Error, object != null, "The object input not be null");
		assert(Error, location != null, "The location to navigate to must not be null");
		assert(Error, speed != null, "Speed of Nav Agent should not be null");
		assert(Warning, speed >= 0, "Speed of Nav Agent should be positive");
		assert(Error, turnDuration != null, "Turn Duration of Nav Agent should not be null");
		assert(Warning, turnDuration >= 0, "Turn Duration of Nav Agent should be positive");

#if arm_navigation
		var from = object.transform.world.getLoc();
		var to = location;

		assert(Error, Navigation.active.navMeshes.length > 0, "No Navigation Mesh Present");
		Navigation.active.navMeshes[0].findPath(from, to, function(path: Array<iron.math.Vec4>) {
			var agent: armory.trait.NavAgent = object.getTrait(armory.trait.NavAgent);
			assert(Error, agent != null, "Object does not have a NavAgent trait");
			agent.speed = speed;
			agent.turnDuration = turnDuration;
			agent.setPath(path);
		});
#end

		runOutput(0);
	}
}
