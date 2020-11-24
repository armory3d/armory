package armory.logicnode;
import armory.trait.internal.DebugConsole;

class GetDebugConsoleSettings extends LogicNode {
   
	public function new(tree: LogicTree) {
		super(tree);	
	}

	override function get(from: Int): Dynamic {
        #if arm_debug
        switch(from) {
            case 0: return armory.trait.internal.DebugConsole.getVisible();
            case 1: return armory.trait.internal.DebugConsole.getScale();
            case 2: {
                switch (armory.trait.internal.DebugConsole.getPosition()) {
		        case PositionStateEnum.LEFT: return "Left";
		        case PositionStateEnum.CENTER: return "Center";
		        case PositionStateEnum.RIGHT: return "Right";
		        }
            }
        }
		#end        
		return null;
	}
}
