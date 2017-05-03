package armory.logicnode;

import armory.system.Cycles;

class LogicTree extends armory.Trait {

	public var loopBreak = false; // Trigger break from loop nodes

	public static var packageName = "armory.logicnode";
	static var parsedNodes:Map<String, LogicNode> = null;
	static var canvas:TNodeCanvas;

	public function new() {
		super();
	}

	public static function fromCanvas(_canvas:TNodeCanvas):LogicTree {
		// notifyOnAdd(function({ }));

		canvas = _canvas;
		parsedNodes = new Map();
		// parsedLabels = new Map();
		
		var tree = new LogicTree();
		var rootNodes = getRootNodes(canvas.nodes);
		for (node in rootNodes) {
			buildNode(tree, node);
		}
		return tree;
	}

	static function buildNode(tree:LogicTree, node:TNode):LogicNode {
		// if (node.type == 'REROUTE') {
			// return buildNode(tree, node.inputs[0].links[0].from_node);
		// }

		// Get node name
		var name = '_' + safeSourceName(node.name);

		// Link nodes using labels
		// if (node.label != '') {
			// if node.label in parsedLabels:
				// return parsedLabels[node.label]
			// parsedLabels[node.label] = name
		// }

		// Check if node already exists
		if (parsedNodes.exists(name)) {
			return parsedNodes.get(name);
		}

		// Create node
		var lnode:LogicNode = createClassInstance(node.type, [tree]);
		parsedNodes.set(name, lnode);

		// Properties
		// for (i in 0...5) {
			// if hasattr(node, 'property' + str(i)):
				// f.write('\t\t' + name + '.property' + str(i) + ' = "' + getattr(node, 'property' + str(i)) + '";\n')
		// }
		
		// Create inputs
		for (inp in node.inputs) {
			// Is linked - find node
			var inpNode:LogicNode = null;
			var inpFrom = 0;
			var l = getInputLink(inp);
			if (l != null) {
				var n = getNode(l.from_id);
				inpNode = buildNode(tree, n);
				inpFrom = l.from_socket;
			}
			// Not linked - create node with default values
			else {
				inpNode = buildDefaultNode(inp, tree);
				inpFrom = 0;
			}
			// Add input
			lnode.addInput(inpNode, inpFrom);
		}

		// Create outputs
		for (out in node.outputs) {
			var outNodes = [];
			var ls = getOutputLinks(out);
			if (ls != null && ls.length > 0) {
				for (l in ls) {
					var n = getNode(l.to_id);
					outNodes.push(buildNode(tree, n));
				}
			}
			// Not linked - create node with default values
			else {
				outNodes.push(buildDefaultNode(out, tree));
			}
			// Add input
			lnode.addOutputs(outNodes);
		}

		return lnode;
	}

	static function createClassInstance(className:String, args:Array<Dynamic>):Dynamic {
		var cname = Type.resolveClass(packageName + '.' + className);
		if (cname == null) return null;
		return Type.createInstance(cname, args);
	}

	static function safeSourceName(s):String {
		return s;
	}

	static function getRootNodes(nodes:Array<TNode>):Array<TNode> {
		var roots:Array<TNode> = [];
		for (node in nodes) {
			// if (node.type == 'FRAME') continue;
			var linked = false;
			for (out in node.outputs) {
				var ls = getOutputLinks(out);
				if (ls != null && ls.length > 0) {
					linked = true;
					break;
				}
			}
			if (!linked) roots.push(node); // Assume node with no connected outputs as roots
		}
		return roots;
	}

	static function buildDefaultNode(inp:TNodeSocket, tree:LogicTree):LogicNode {
		
		if (inp.type == 'OBJECT') {
			return createClassInstance('ObjectNode', [tree, inp.default_value]);
		}
		else if (inp.type == 'VECTOR') {
			return createClassInstance('VectorNode', [tree, inp.default_value[0], inp.default_value[1], inp.default_value[2]]);
		}
		else if (inp.type == 'RGBA') {
			return createClassInstance('ColorNode', [tree, inp.default_value[0], inp.default_value[1], inp.default_value[2], inp.default_value[3]]);
		}
		else if (inp.type == 'RGB') {
			return createClassInstance('ColorNode', [tree, inp.default_value[0], inp.default_value[1], inp.default_value[2]]);
		}
		else if (inp.type == 'VALUE') {
			return createClassInstance('FloatNode', [tree, inp.default_value]);
		}
		else if (inp.type == 'INT') {
			return createClassInstance('IntegerNode', [tree, inp.default_value]);
		}
		else if (inp.type == 'BOOLEAN') {
			return createClassInstance('BooleanNode', [tree, inp.default_value]);
		}
		else if (inp.type == 'STRING') {
			return createClassInstance('StringNode', [tree, inp.default_value]);
		}
		else { // ACTION
			return createClassInstance('NullNode', [tree]);
		}
	}

	static function getNode(id: Int): TNode {
		for (n in canvas.nodes) if (n.id == id) return n;
		return null;
	}

	static function getLink(id: Int): TNodeLink {
		for (l in canvas.links) if (l.id == id) return l;
		return null;
	}

	static function getInputLink(inp: TNodeSocket): TNodeLink {
		for (l in canvas.links) {
			if (l.to_id == inp.node_id) {
				var node = getNode(inp.node_id);
				if (node.inputs.length <= l.to_socket) return null;
				if (node.inputs[l.to_socket] == inp) return l;
			}
		}
		return null;
	}

	static function getOutputLinks(out: TNodeSocket): Array<TNodeLink> {
		var ls:Array<TNodeLink> = null;
		for (l in canvas.links) {
			if (l.from_id == out.node_id) {
				var node = getNode(out.node_id);
				if (node.outputs.length <= l.from_socket) continue;
				if (node.outputs[l.from_socket] == out) {
					if (ls == null) ls = [];
					ls.push(l);
				}
			}
		}
		return ls;
	}
}
