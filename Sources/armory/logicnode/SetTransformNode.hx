package armory.logicnode;

import armory.trait.internal.NodeExecutor;

class SetTransformNode extends Node {

	public static inline var _trigger = 0; // Bool
	public static inline var _target = 1; // Target
	public static inline var _transform = 2; // Transform

	public function new() {
		super();
	}

	public override function inputChanged() {
		if (!inputs[_trigger].val || inputs[_target].target == null || inputs[_transform].matrix == null) return;

		inputs[_target].target.transform.setMatrix(inputs[_transform].matrix);

		super.inputChanged();
	}

	public static function create(trigger:Bool, target:iron.object.Object, transform:iron.object.Transform):SetTransformNode {
		var n = new SetTransformNode();
		n.inputs.push(BoolNode.create(trigger));
		n.inputs.push(target);
		n.inputs.push(transform);
		return n;
	}
}
