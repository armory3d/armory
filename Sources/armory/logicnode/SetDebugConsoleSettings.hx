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
		case "Left":
			return armory.trait.internal.DebugConsole.setPosition(PositionStateEnum.LEFT);
		case "Center":
			return armory.trait.internal.DebugConsole.setPosition(PositionStateEnum.CENTER);
		case "Right":
			return armory.trait.internal.DebugConsole.setPosition(PositionStateEnum.RIGHT);
		}
		#end
		runOutput(0);
	}
}