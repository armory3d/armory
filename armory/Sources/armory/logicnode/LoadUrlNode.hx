// This node does not work with Krom. "Browser compilation only" node.

package armory.logicnode;

import kha.System;

class LoadUrlNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		System.loadUrl(inputs[1].get());
	}
}
