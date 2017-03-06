package armory.logicnode;

class Node {

	var trait:armory.Trait;
	var inputs:Array<Node> = [];
	var outputs:Array<Node> = [];

	public function new(trait:armory.Trait) {
		this.trait = trait;
	}

	public function addInput(node:Node) {
		inputs.push(node);
		node.outputs.push(this);
	}

	function run() { for (o in outputs) o.run(); }

	function get():Dynamic { return this; }
}
