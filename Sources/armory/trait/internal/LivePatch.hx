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

	public static function patchNodeDelete(treeName: String, nodeName: String, outputDatas: Array<Array<Dynamic>>) {
		var tree = LogicTree.nodeTrees[treeName];
		if (tree == null) return;

		var node = tree.nodes[nodeName];
		if (node == null) return;

		// Remove this node from the outputs of connected nodes
		for (input in node.inputs) {
			var inNodeOutputs = input.node.outputs;

			// Default nodes don't have outputs when exported from Blender
			if (input.from < inNodeOutputs.length) {
				for (outNode in inNodeOutputs[input.from]) {
					if (outNode == node) {
						inNodeOutputs[input.from].remove(outNode);
					}
				}
			}

		}

		// Replace connected inputs of other nodes with default nodes
		for (outputNodes in node.outputs) {
			for (outNode in outputNodes) {
				for (outNodeInput in outNode.inputs) {
					if (outNodeInput.node == node) {
						var outputIndex = outNodeInput.from;
						var socketType = outputDatas[outputIndex][0];
						var socketValue = outputDatas[outputIndex][1];
						outNodeInput.node = createSocketDefaultNode(node.tree, socketType, socketValue);
					}
				}
			}
		}

		tree.nodes.remove(nodeName);
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
			newNode.addInput(createSocketDefaultNode(newNode.tree, inputData[0], inputData[1]), i++);
		}

		for (outputData in outputDatas) {
			newNode.addOutputs([createSocketDefaultNode(newNode.tree, outputData[0], outputData[1])]);
		}
	}

	static inline function createSocketDefaultNode(tree: LogicTree, socketType: String, value: Dynamic): LogicNode {
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
}
