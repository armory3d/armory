package armory.logicnode;

class Node {

	var tree:LogicTree;
	var inputs:Array<NodeInput> = [];
	var outputs:Array<Array<Node>> = [];

	public function new(tree:LogicTree) {
		this.tree = tree;
	}

	public function addInput(node:Node, from:Int) {
		inputs.push(new NodeInput(node, from));
	}

	public function addOutputs(nodes:Array<Node>) {
		outputs.push(nodes);
	}

	function run() { for (ar in outputs) for (o in ar) o.run(); }

	function runOutputs(i:Int) { for (o in outputs[i]) o.run(); }

	@:allow(armory.logicnode.NodeInput)
	function get(from:Int):Dynamic { return this; }

	@:allow(armory.logicnode.NodeInput)
	function set(value:Dynamic) { }
}

class NodeInput {

	@:allow(armory.logicnode.Node)
	var node:Node;
	var from:Int; // Socket index

	public function new(node:Node, from:Int) {
		this.node = node;
		this.from = from;
	}

	@:allow(armory.logicnode.Node)
	function get():Dynamic {
		return node.get(from);
	}

	@:allow(armory.logicnode.Node)
	function set(value:Dynamic) {
		node.set(value);
	}
}
