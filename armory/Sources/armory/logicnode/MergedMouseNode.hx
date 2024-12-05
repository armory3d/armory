package armory.logicnode;

#if arm_debug
import armory.trait.internal.DebugConsole;
#end

class MergedMouseNode extends LogicNode {

	public var property0: String;
	public var property1: String;
	public var property2: Bool;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		#if arm_debug
			if (!property2 && DebugConsole.isDebugConsoleHovered && property0 != "moved") return;
		#end

		var mouse = iron.system.Input.getMouse();
		var b = false;
		switch (property0) {
		case "started":
			b = mouse.started(property1);
		case "down":
			b = mouse.down(property1);
		case "released":
			b = mouse.released(property1);
		case "moved":
			b = mouse.moved;
		}
		if (b) runOutput(0);
	}

	override function get(from: Int): Dynamic {
		#if arm_debug
			if (!property2 && DebugConsole.isDebugConsoleHovered && property0 != "moved") return false;
		#end

		var mouse = iron.system.Input.getMouse();
		switch (property0) {
		case "started":
			return mouse.started(property1);
		case "down":
			return mouse.down(property1);
		case "released":
			return mouse.released(property1);
		case "moved":
			return mouse.moved;
		}
		return false;
	}
}
