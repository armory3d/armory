package armory.logicnode;

class LogicNode {

	var tree:LogicTree;
	var inputs:Array<LogicNodeInput> = [];
	var outputs:Array<Array<LogicNode>> = [];

	#if arm_debug
	public var name = "";
	public function watch(b:Bool) { // Watch in debug console
		var nodes = armory.trait.internal.DebugConsole.watchNodes;
		b ? nodes.push(this) : nodes.remove(this);
	}
	#end

	public function new(tree:LogicTree) {
		this.tree = tree;
	}

	public function addInput(node:LogicNode, from:Int) {
		inputs.push(new LogicNodeInput(node, from));
	}

	public function addOutputs(nodes:Array<LogicNode>) {
		outputs.push(nodes);
	}

	function run() { for (ar in outputs) for (o in ar) o.run(); }

	function runOutputs(i:Int) { if (i < outputs.length) for (o in outputs[i]) o.run(); }

	@:allow(armory.logicnode.LogicNodeInput)
	function get(from:Int):Dynamic { return this; }

	@:allow(armory.logicnode.LogicNodeInput)
	function set(value:Dynamic) { }
}

class LogicNodeInput {

	@:allow(armory.logicnode.LogicNode)
	var node:LogicNode;
	var from:Int; // Socket index

	public function new(node:LogicNode, from:Int) {
		this.node = node;
		this.from = from;
	}

	@:allow(armory.logicnode.LogicNode)
	function get():Dynamic {
		return node.get(from);
	}

	@:allow(armory.logicnode.LogicNode)
	function set(value:Dynamic) {
		node.set(value);
	}
}
