package armory.logicnode;

import armory.trait.internal.NodeExecutor;

class GetTransformNode extends TransformNode {

	public static inline var _target = 0; // Target

	public function new() {
		super(false);
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);

		executor.notifyOnNodeInit(init);
	}

	public override function inputChanged() {
		var t = inputs[_target].target;
		if (t != null && matrix == null) {
			var tr = t.transform;
			matrix = tr.matrix;
			loc = tr.loc;
			rot = tr.rot;
			scale = tr.scale;
			super.inputChanged();
		}
	}

	function init() {
		inputChanged();
	}

	public static function create(target:iron.object.Object):GetTransformNode {
		var n = new GetTransformNode();
		n.inputs.push(target);
		return n;
	}
}
