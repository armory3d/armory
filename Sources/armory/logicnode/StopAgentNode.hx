package armory.logicnode;

import iron.object.Object;

class StopAgentNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();

		if (object == null) return;

#if arm_navigation
		var agent: armory.trait.NavAgent = object.getTrait(armory.trait.NavAgent);
		agent.stop();
#end

		runOutput(0);
	}
}
