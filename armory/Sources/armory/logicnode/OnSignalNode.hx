package armory.logicnode;

import armory.system.Signal;

class OnSignalNode extends LogicNode {
	var emittedArgs: Array<Dynamic> = [];
	var connectedSignal: Signal = null;
	var callback: haxe.Constraints.Function = null;

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnInit(init);
		tree.notifyOnRemove(onRemove);
	}

	function init() {
		var signal: Signal = inputs[0].get();
		if (signal == null)
			return;

		connectedSignal = signal;
		callback = onSignal;
		signal.connect(callback);
	}

	function onSignal(...args: Any) {
		emittedArgs = [];
		for (arg in args) {
			emittedArgs.push(arg);
		}
		runOutput(0);
	}

	override function get(from: Int): Any {
		var argIndex: Int = from - 1;
		if (argIndex >= 0 && argIndex < emittedArgs.length) {
			return emittedArgs[argIndex];
		}
		return null;
	}

	function onRemove() {
		if (connectedSignal != null && callback != null) {
			connectedSignal.disconnect(callback);
			connectedSignal = null;
			callback = null;
		}
	}
}
