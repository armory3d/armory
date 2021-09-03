package armory.logicnode;

import iron.object.Object;

class GetAgentDataNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Float {
		var object: Object = inputs[0].get();

		assert(Error, object != null, "The object to naviagte should not be null");

#if arm_navigation
		var agent: armory.trait.NavAgent = object.getTrait(armory.trait.NavAgent);
		assert(Error, agent != null, "The object does not have NavAgent Trait");
		if(from == 0) return agent.speed;
		else return agent.turnDuration;
#else
		return null;
#end
	}
}