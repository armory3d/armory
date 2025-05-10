package armory.logicnode;

#if arm_physics
import armory.trait.physics.PhysicsWorld;
#end
import armory.trait.navigation.Navigation;
import iron.object.Object;
import iron.math.Vec4;

class GoToLocationNode extends LogicNode {

	var object: Object;
	var location: Vec4;
	var speed: Float;
	var turnDuration: Float;
	var heightOffset: Float;
	var useRaycast: Bool;
	var rayCastDepth: Float;
	var rayCastMask: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		object = inputs[1].get();
		location = inputs[2].get();
		speed = inputs[3].get();
		turnDuration = inputs[4].get();
		heightOffset = inputs[5].get();
		useRaycast = inputs[6].get();
		rayCastDepth = inputs[7].get();
		rayCastMask = inputs[8].get();

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
			agent.heightOffset = heightOffset;
			agent.tickPos = tickPos;
			agent.tickRot = tickRot;
			agent.setPath(path);
		});
#end

		runOutput(0);
	}

	function tickPos(){
		#if arm_physics
		if(useRaycast) setAgentHeight();
		#end
		runOutput(1);
	}

	function tickRot(){
		runOutput(2);
	}

	function setAgentHeight(){
		#if arm_physics
		var fromLoc = object.transform.world.getLoc();
		var toLoc = fromLoc.clone();
		toLoc.z += rayCastDepth;
		var hit = PhysicsWorld.active.rayCast(fromLoc, toLoc, rayCastMask);
		if(hit != null) object.transform.loc.z = hit.pos.z + heightOffset;
		#end
	}
}
