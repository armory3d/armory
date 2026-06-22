package armory.logicnode;

#if arm_patch @:keep @:keepSub #end
class LogicNode {

	var tree: LogicTree;
	var inputs: Array<LogicNodeLink> = [];
	var outputs: Array<Array<LogicNodeLink>> = [];

	#if (arm_debug || arm_patch)
	public var name = "";

		#if (arm_debug)
		public function watch(b: Bool) { // Watch in debug console
			var nodes = armory.trait.internal.DebugConsole.watchNodes;
			b ? nodes.push(this) : nodes.remove(this);
		}
		#end
	#end

	public function new(tree: LogicTree) {
		this.tree = tree;
	}

	/**
		Resize the inputs array to a given size to minimize dynamic
		reallocation and over-allocation later.
	**/
	inline function preallocInputs(amount: Int) {
		this.inputs.resize(amount);
	}

	/**
		Resize the outputs array to a given size to minimize dynamic
		reallocation and over-allocation later.
	**/
	inline function preallocOutputs(amount: Int) {
		this.outputs.resize(amount);
		for (i in 0...outputs.length) {
			outputs[i] = [];
		}
	}

	/**
		Add a link between to nodes to the tree.
	**/
	public static function addLink(fromNode: LogicNode, toNode: LogicNode, fromIndex: Int, toIndex: Int): LogicNodeLink {
		var link = new LogicNodeLink(fromNode, toNode, fromIndex, toIndex);

		if (toNode.inputs.length <= toIndex) {
			toNode.inputs.resize(toIndex + 1);
		}
		toNode.inputs[toIndex] = link;

		var fromNodeOuts = fromNode.outputs;
		var outLen = fromNodeOuts.length;
		if (outLen <= fromIndex) {
			fromNodeOuts.resize(fromIndex + 1);

			// Initialize with empty arrays
			for (i in outLen...fromIndex + 1) {
				fromNodeOuts[i] = [];
			}
		}
		fromNodeOuts[fromIndex].push(link);

		return link;
	}

	#if arm_patch
	/**
		Removes a link from the tree.
	**/
	static function removeLink(link: LogicNodeLink) {
		link.fromNode.outputs[link.fromIndex].remove(link);

		// Reuse the same link and connect a default input node to it.
		// That's why this function is only available in arm_patch mode, we need
		// access to the link's type and value.
		link.fromNode = LogicNode.createSocketDefaultNode(link.toNode.tree, link.toType, link.toValue);
		link.fromIndex = 0;
	}

	/**
		Removes all inputs and their links from this node.
		Warning: this function changes the amount of node inputs to 0!
	**/
	function clearInputs() {
		for (link in inputs) {
			link.fromNode.outputs[link.fromIndex].remove(link);
		}
		inputs.resize(0);
	}

	/**
		Removes all outputs and their links from this node.
		Warning: this function changes the amount of node inputs to 0!
	**/
	function clearOutputs() {
		for (links in outputs) {
			for (link in links) {
				var defaultNode = LogicNode.createSocketDefaultNode(tree, link.toType, link.toValue);
				link.fromNode = defaultNode;
				link.fromIndex = 0;
				defaultNode.outputs[0] = [link];
			}
		}
		outputs.resize(0);
	}

	/**
		Creates a default node for a socket so that get() and set() can be
		used without null checks.
		Loosely equivalent to `make_logic.build_default_node()` in Python.
	**/
	static inline function createSocketDefaultNode(tree: LogicTree, socketType: String, value: Dynamic): LogicNode {
		// Make sure to not add these nodes to the LogicTree.nodes array as they
		// won't be garbage collected then if unlinked later.
		return switch (socketType) {
			case "VECTOR": new armory.logicnode.VectorNode(tree, value[0], value[1], value[2]);
			case "RGBA": new armory.logicnode.ColorNode(tree, value[0], value[1], value[2], value[3]);
			case "RGB": new armory.logicnode.ColorNode(tree, value[0], value[1], value[2]);
			case "VALUE": new armory.logicnode.FloatNode(tree, value);
			case "INT": new armory.logicnode.IntegerNode(tree, value);
			case "BOOLEAN": new armory.logicnode.BooleanNode(tree, value);
			case "STRING": new armory.logicnode.StringNode(tree, value);
			case "NONE": new armory.logicnode.NullNode(tree);
			case "OBJECT": new armory.logicnode.ObjectNode(tree, value);
			default: new armory.logicnode.DynamicNode(tree, value);
		}
	}
	#end

	/**
	   Called when this node is activated.
	   @param from impulse index
	**/
	function run(from: Int) {}

	/**
	   Call to activate node connected to the output.
	   @param i output index
	**/
	function runOutput(i: Int) {
		if (i >= outputs.length) return;
		for (outLink in outputs[i]) {
			outLink.toNode.run(outLink.toIndex);
		}
	}

	@:allow(armory.logicnode.LogicNodeLink)
	function get(from: Int): Dynamic { return this; }

	@:allow(armory.logicnode.LogicNodeLink)
	function set(value: Dynamic) {}
}

@:allow(armory.logicnode.LogicNode)
@:allow(armory.logicnode.LogicTree)
class LogicNodeLink {

	var fromNode: LogicNode;
	var toNode: LogicNode;
	var fromIndex: Int;
	var toIndex: Int;

	#if arm_patch
	var fromType: String;
	var toType: String;
	var toValue: Dynamic;
	#end

	inline function new(fromNode: LogicNode, toNode: LogicNode, fromIndex: Int, toIndex: Int) {
		this.fromNode = fromNode;
		this.toNode = toNode;
		this.fromIndex = fromIndex;
		this.toIndex = toIndex;
	}

	inline function get(): Dynamic {
		return fromNode.get(fromIndex);
	}

	inline function set(value: Dynamic) {
		fromNode.set(value);
	}
}
