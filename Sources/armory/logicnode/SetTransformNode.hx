package armory.logicnode;

import armory.trait.internal.NodeExecutor;

class SetTransformNode extends Node {

	public static inline var _target = 0; // Target
	public static inline var _transform = 1; // Transform

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);

		executor.notifyOnNodeInit(init);
	}

	function init() {
		var target:iron.node.Node = inputs[_target].target;
		if (target != null) {
			var matrix:iron.math.Mat4 = inputs[_transform].matrix;
			target.transform.prependMatrix(matrix);
		}
	}

	public override function inputChanged() {
		if (inputs[_target].target == null) { // Target not attached, check next time
			executor.notifyOnNodeInit(init);
		}
		else {
			inputs[_target].target.transform.dirty = true;
		}

		super.inputChanged();
	}

	public static function create(target:iron.node.Node, transform:iron.node.Transform):SetTransformNode {
		var n = new SetTransformNode();
		n.inputs.push(target);
		n.inputs.push(transform);
		return n;
	}
}
