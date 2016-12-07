package armory.logicnode;

import armory.trait.internal.NodeExecutor;

#if arm_navigation
import armory.trait.internal.Navigation;
#end

class GoToNode extends Node {

	public static inline var _trigger = 0; // Bool
	public static inline var _target = 1; // Target
	public static inline var _transform = 2; // Transform

	public function new() {
		super();
	}

	public override function inputChanged() {
		if (!inputs[_trigger].val || inputs[_target].target == null || inputs[_transform].matrix == null) return;

#if arm_navigation
		// Assume navmesh exists..
		var from = inputs[_target].target.transform.loc;
		var to = inputs[_transform].loc;
		Navigation.active.navMeshes[0].findPath(from, to, function(path:Array<iron.math.Vec4>) {
			
			var agent:armory.trait.NavAgent = inputs[_target].target.getTrait(armory.trait.NavAgent);
			agent.setPath(path);

			//super.inputChanged();
		});
#end
	}

	public static function create(trigger:Bool, target:iron.object.Object, transform:iron.object.Transform):GoToNode {
		var n = new GoToNode();
		n.inputs.push(BoolNode.create(trigger));
		n.inputs.push(target);
		n.inputs.push(transform);
		return n;
	}
}
