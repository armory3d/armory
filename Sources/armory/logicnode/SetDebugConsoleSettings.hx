package armory.logicnode;
import armory.trait.internal.DebugConsole;

class SetDebugConsoleSettings extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_debug
		var visible: Dynamic = inputs[1].get();
		armory.trait.internal.DebugConsole.setVisible(visible);

		var scale: Dynamic = inputs[2].get();
		if ((scale >= 0.3) && (scale <= 10.0))
			armory.trait.internal.DebugConsole.setScale(scale);

		switch (property0) {
		case "left":
			return armory.trait.internal.DebugConsole.setPosition(PositionStateEnum.Left);
		case "center":
			return armory.trait.internal.DebugConsole.setPosition(PositionStateEnum.Center);
		case "right":
			return armory.trait.internal.DebugConsole.setPosition(PositionStateEnum.Right);
		}
		#end
		runOutput(0);
	}
}
