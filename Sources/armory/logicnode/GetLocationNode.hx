package armory.logicnode;

import armory.trait.internal.NodeExecutor;

class GetLocationNode extends LocationNode {

	public static inline var _target = 0; // Target

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);

		executor.notifyOnNodeInit(init);
	}

	public override function inputChanged() {
		var t = inputs[_target].target;
		if (t != null && loc == null) {
			var tr = t.transform;
			loc = tr.loc;
			super.inputChanged();
		}
	}

	function init() {
		inputChanged();
	}

	public static function create(target:iron.object.Object):GetLocationNode {
		var n = new GetLocationNode();
		n.inputs.push(target);
		return n;
	}
}
