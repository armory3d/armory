package armory.logicnode;

class OnRender2DNode extends LogicNode {
	/**
		The current kha g2 object if the executed code is called inside the
		render2D callback of a OnRender2DNode, else `null`.
	**/
	public static var g(default, null): Null<kha.graphics2.Graphics> = null;

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnRender2D(onRender2D);
	}

	function onRender2D(g: kha.graphics2.Graphics) {
		OnRender2DNode.g = g;
		runOutput(0);
		OnRender2DNode.g = null;
	}

	public static inline function ensure2DContext(nodeClassName: String) {
		assert(Error, OnRender2DNode.g != null,
			'$nodeClassName must be executed inside of a render2D callback. Please consult the documentation of this node.'
		);
	}
}
