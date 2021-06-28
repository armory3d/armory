package armory.trait.internal;

import armory.logicnode.LogicNode.LogicNodeInput;
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
#end
}
