package armory.logicnode;

import armory.trait.internal.NodeExecutor;

class SetVisibleNode extends Node {

	public static inline var _target = 0; // Target
	public static inline var _visible = 1; // Bool

	public function new() {
		super();
	}

	public override function inputChanged() {
		if (inputs[_target].target != null) {
			inputs[_target].target.visible = inputs[_visible].b;
		}
		super.inputChanged();
	}

	public static function create(target:iron.node.Node, visible:Bool):SetVisibleNode {
		var n = new SetVisibleNode();
		n.inputs.push(target);
		n.inputs.push(BoolNode.create(visible));
		return n;
	}
}
