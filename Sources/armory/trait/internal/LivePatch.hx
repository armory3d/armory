package armory.trait.internal;

import armory.logicnode.LogicNode;
import armory.logicnode.LogicTree;


#if arm_patch @:expose("LivePatch") #end
@:access(armory.logicnode.LogicNode)
class LivePatch extends iron.Trait {

#if !arm_patch
	public function new() { super(); }
#else

	static var patchId = 0;

	public function new() {
		super();
		notifyOnUpdate(update);
	}

	function update() {
		kha.Assets.loadBlobFromPath("krom.patch", function(b: kha.Blob) {
			if (b.length == 0) return;
			var lines = b.toString().split("\n");
			var id = Std.parseInt(lines[0]);
			if (id > patchId) {
				patchId = id;
				js.Lib.eval(lines[1]);
			}
		});
	}

	public static function patchCreateNodeLink(treeName: String, fromNodeName: String, toNodeName: String, fromIndex: Int, toIndex: Int) {
		var tree = LogicTree.nodeTrees[treeName];
		if (tree == null) return;

		var fromNode = tree.nodes[fromNodeName];
		var toNode = tree.nodes[toNodeName];
		if (fromNode == null || toNode == null) return;

		// Don't add a connection twice
		if (!fromNode.outputs[fromIndex].contains(toNode)) {
			fromNode.outputs[fromIndex].push(toNode);
		}
		toNode.inputs[toIndex] = new LogicNodeInput(fromNode, fromIndex);
	}

	public static function patchUpdateNodeProp(treeName: String, nodeName: String, propName: String, value: Dynamic) {
		var tree = LogicTree.nodeTrees[treeName];
		if (tree == null) return;

		var node = tree.nodes[nodeName];
		if (node == null) return;

		Reflect.setField(node, propName, value);
	}

	public static function patchUpdateNodeInputVal(treeName: String, nodeName: String, socketIndex: Int, value: Dynamic) {
		var tree = LogicTree.nodeTrees[treeName];
		if (tree == null) return;

		var node = tree.nodes[nodeName];
		if (node == null) return;

		@:privateAccess node.inputs[socketIndex].set(value);
	}

	public static function patchNodeCopy(treeName: String, nodeName: String, newNodeName: String, copyProps: Array<String>, inputDatas: Array<Array<Dynamic>>, outputDatas: Array<Array<Dynamic>>) {
		var tree = LogicTree.nodeTrees[treeName];
		if (tree == null) return;

		var node = tree.nodes[nodeName];
		if (node == null) return;

		// No further constructor parameters required here, all variable nodes
		// use optional further parameters and all values are set later in this
		// function.
		var newNode = Type.createInstance(Type.getClass(node), [tree]);
		newNode.name = newNodeName;
		tree.nodes[newNodeName] = newNode;

		for (propName in copyProps) {
			Reflect.setField(newNode, propName, Reflect.field(node, propName));
		}

		var i = 0;
		for (inputData in inputDatas) {
			newNode.addInput(createSocketDefaultNode(newNode, inputData[0], inputData[1]), i++);
		}

		for (outputData in outputDatas) {
			newNode.addOutputs([createSocketDefaultNode(newNode, outputData[0], outputData[1])]);
		}
	}

	static inline function createSocketDefaultNode(node: LogicNode, inputType: String, value: Dynamic): LogicNode {
		return switch (inputType) {
			case "VECTOR":
				new armory.logicnode.VectorNode(node.tree, value[0], value[1], value[2]);
			case "RGBA":
				new armory.logicnode.ColorNode(node.tree, value[0], value[1], value[2], value[3]);
			case "RGB":
				new armory.logicnode.ColorNode(node.tree, value[0], value[1], value[2]);
			case "VALUE":
				new armory.logicnode.FloatNode(node.tree, value);
			case "INT":
				new armory.logicnode.IntegerNode(node.tree, value);
			case "BOOLEAN":
				new armory.logicnode.BooleanNode(node.tree, value);
			case "STRING":
				new armory.logicnode.StringNode(node.tree, value);
			case "NONE":
				new armory.logicnode.NullNode(node.tree);
			case "OBJECT":
				new armory.logicnode.ObjectNode(node.tree, value);
			default:
				new armory.logicnode.DynamicNode(node.tree, value);
		}
	}
#end
}
