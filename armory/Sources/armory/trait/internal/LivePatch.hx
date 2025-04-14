package armory.trait.internal;

import armory.logicnode.LogicNode;
import armory.logicnode.LogicTree;


#if arm_patch @:expose("LivePatch") #end
@:access(armory.logicnode.LogicNode)
@:access(armory.logicnode.LogicNodeLink)
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
		if (!LogicTree.nodeTrees.exists(treeName)) return;
		var trees = LogicTree.nodeTrees[treeName];

		for (tree in trees) {
			var fromNode = tree.nodes[fromNodeName];
			var toNode = tree.nodes[toNodeName];
			if (fromNode == null || toNode == null) return;

			LogicNode.addLink(fromNode, toNode, fromIndex, toIndex);
		}
	}

	public static function patchSetNodeLinks(treeName: String, nodeName: String, inputDatas: Array<Dynamic>, outputDatas: Array<Array<Dynamic>>) {
		if (!LogicTree.nodeTrees.exists(treeName)) return;
		var trees = LogicTree.nodeTrees[treeName];

		for (tree in trees) {
			var node = tree.nodes[nodeName];
			if (node == null) return;

			node.clearInputs();
			node.clearOutputs();

			for (inputData in inputDatas) {
				var fromNode: LogicNode;
				var fromIndex: Int;

				if (inputData.isLinked) {
					fromNode = tree.nodes[inputData.fromNode];
					if (fromNode == null) continue;
					fromIndex = inputData.fromIndex;
				}
				else {
					fromNode = LogicNode.createSocketDefaultNode(node.tree, inputData.socketType, inputData.socketValue);
					fromIndex = 0;
				}

				LogicNode.addLink(fromNode, node, fromIndex, inputData.toIndex);
			}

			for (outputData in outputDatas) {
				for (linkData in outputData) {
					var toNode: LogicNode;
					var toIndex: Int;

					if (linkData.isLinked) {
						toNode = tree.nodes[linkData.toNode];
						if (toNode == null) continue;
						toIndex = linkData.toIndex;
					}
					else {
						toNode = LogicNode.createSocketDefaultNode(node.tree, linkData.socketType, linkData.socketValue);
						toIndex = 0;
					}

					LogicNode.addLink(node, toNode, linkData.fromIndex, toIndex);
				}
			}
		}
	}

	public static function patchUpdateNodeProp(treeName: String, nodeName: String, propName: String, value: Dynamic) {
		if (!LogicTree.nodeTrees.exists(treeName)) return;
		var trees = LogicTree.nodeTrees[treeName];

		for (tree in trees) {
			var node = tree.nodes[nodeName];
			if (node == null) return;

			Reflect.setField(node, propName, value);
		}
	}

	public static function patchUpdateNodeInputVal(treeName: String, nodeName: String, socketIndex: Int, value: Dynamic) {
		if (!LogicTree.nodeTrees.exists(treeName)) return;
		var trees = LogicTree.nodeTrees[treeName];

		for (tree in trees) {
			var node = tree.nodes[nodeName];
			if (node == null) return;

			node.inputs[socketIndex].set(value);
		}
	}

	public static function patchNodeDelete(treeName: String, nodeName: String) {
		if (!LogicTree.nodeTrees.exists(treeName)) return;
		var trees = LogicTree.nodeTrees[treeName];

		for (tree in trees) {
			var node = tree.nodes[nodeName];
			if (node == null) return;

			node.clearOutputs();
			node.clearInputs();
			tree.nodes.remove(nodeName);
		}
	}

	public static function patchNodeCreate(treeName: String, nodeName: String, nodeType: String, propDatas: Array<Array<Dynamic>>, inputDatas: Array<Array<Dynamic>>, outputDatas: Array<Array<Dynamic>>) {
		if (!LogicTree.nodeTrees.exists(treeName)) return;
		var trees = LogicTree.nodeTrees[treeName];

		for (tree in trees) {
			// No further constructor parameters required here, all variable nodes
			// use optional further parameters and all values are set later in this
			// function.
			var newNode: LogicNode = Type.createInstance(Type.resolveClass(nodeType), [tree]);
			newNode.name = nodeName;
			tree.nodes[nodeName] = newNode;

			for (propData in propDatas) {
				Reflect.setField(newNode, propData[0], propData[1]);
			}

			var i = 0;
			for (inputData in inputDatas) {
				LogicNode.addLink(LogicNode.createSocketDefaultNode(newNode.tree, inputData[0], inputData[1]), newNode, 0, i++);
			}

			i = 0;
			for (outputData in outputDatas) {
				LogicNode.addLink(newNode, LogicNode.createSocketDefaultNode(newNode.tree, outputData[0], outputData[1]), i++, 0);
			}
		}
	}

	public static function patchNodeCopy(treeName: String, nodeName: String, newNodeName: String, copyProps: Array<String>, inputDatas: Array<Array<Dynamic>>, outputDatas: Array<Array<Dynamic>>) {
		if (!LogicTree.nodeTrees.exists(treeName)) return;
		var trees = LogicTree.nodeTrees[treeName];

		for (tree in trees) {
			var node = tree.nodes[nodeName];
			if (node == null) return;

			// No further constructor parameters required here, all variable nodes
			// use optional further parameters and all values are set later in this
			// function.
			var newNode: LogicNode = Type.createInstance(Type.getClass(node), [tree]);
			newNode.name = newNodeName;
			tree.nodes[newNodeName] = newNode;

			for (propName in copyProps) {
				Reflect.setField(newNode, propName, Reflect.field(node, propName));
			}

			var i = 0;
			for (inputData in inputDatas) {
				LogicNode.addLink(LogicNode.createSocketDefaultNode(newNode.tree, inputData[0], inputData[1]), newNode, 0, i++);
			}

			i = 0;
			for (outputData in outputDatas) {
				LogicNode.addLink(newNode, LogicNode.createSocketDefaultNode(newNode.tree, outputData[0], outputData[1]), i++, 0);
			}
		}
	}

#end
}
