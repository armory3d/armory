package armory.logicnode;

class LogicTree extends iron.Trait {

	#if arm_patch
	/**
		Stores all trait instances of the tree via its name.
	**/
	public static var nodeTrees = new Map<String, Array<LogicTree>>();

	/**
		[node name => logic node] for later node replacement for live patching.
	**/
	public var nodes: Map<String, LogicNode>;
	#end

	public var loopBreak = false; // Trigger break from loop nodes
	public var loopContinue = false; // Trigger Continue from loop nodes

	public function new() {
		super();

		#if arm_patch
		nodes = new Map<String, LogicNode>();
		#end
	}

	public function add() {}

	public var paused = false;

	public function pause() {
		if (paused) return;
		paused = true;

		if (_update != null) for (f in _update) iron.App.removeUpdate(f);
		if (_lateUpdate != null) for (f in _lateUpdate) iron.App.removeLateUpdate(f);
	}

	public function resume() {
		if (!paused) return;
		paused = false;

		if (_update != null) for (f in _update) iron.App.notifyOnUpdate(f);
		if (_lateUpdate != null) for (f in _lateUpdate) iron.App.notifyOnLateUpdate(f);
	}
}
