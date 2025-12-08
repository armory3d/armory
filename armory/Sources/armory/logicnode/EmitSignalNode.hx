package armory.logicnode;

import armory.system.Signal;

class EmitSignalNode extends LogicNode {
	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var signal: Signal = inputs[1].get();
		if (signal == null)
			return;

		var args: Array<Any> = [];
		for (i in 2...inputs.length) {
			args.push(inputs[i].get());
		}

		Reflect.callMethod(signal, Reflect.field(signal, "emit"), args);
		runOutput(0);
	}
}
