package armory.logicnode;

import iron.system.Input;

#if arm_debug
import armory.trait.internal.DebugConsole;
#end

class GetMouseStartedNode extends LogicNode {

	public var property0: Bool;

	var m = Input.getMouse();
	var buttonStarted: Null<String>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		buttonStarted = null;

		#if arm_debug
			if (!property0 && DebugConsole.isDebugConsoleHovered) return;
		#end

		for (b in Mouse.buttons) {
			if (m.started(b)) {
				buttonStarted = b;
				break;
			}
		}

		if (buttonStarted != null) {
			runOutput(0);
		}
	}

	override function get(from: Int) {
		return buttonStarted;
	}
}
