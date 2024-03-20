package armory.logicnode;

#if arm_debug
import armory.trait.internal.DebugConsole;
#end

class GetDebugConsoleSettings extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		switch(from) {
			case 0: return #if arm_debug true #else false #end;
			case 1: return #if arm_debug DebugConsole.getVisible() #else false #end;
			case 2: return #if arm_debug DebugConsole.isDebugConsoleHovered #else false #end;
			case 3: return #if arm_debug DebugConsole.getScale() #else 1.0 #end;
			case 4:
				#if arm_debug
				switch (DebugConsole.getPosition()) {
					case PositionStateEnum.Left: return "Left";
					case PositionStateEnum.Center: return "Center";
					case PositionStateEnum.Right: return "Right";
				}
				#else
				return "";
				#end
		}
		return null;
	}
}
