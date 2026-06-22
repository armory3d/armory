// This node does not work with Krom. "Browser compilation only" node.

package armory.logicnode;

import kha.System;

class DetectMobileBrowserNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		if (from == 0) {
			#if kha_html5
			return kha.SystemImpl.mobile;
			#else
			return false;
			#end
		} 
		return null;
	}
}