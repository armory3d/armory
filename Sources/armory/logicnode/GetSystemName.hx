package armory.logicnode;

class GetSystemName extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var systemName: String = kha.System.systemId;

		return switch (from) {
			case 0: systemName;
			case 1: equalsCI(systemName, 'Windows');
			case 2: equalsCI(systemName, 'Linux');
			case 3: equalsCI(systemName, 'Mac');
			case 4: equalsCI(systemName, 'HTML5');
			case 5: equalsCI(systemName, 'Android');
			default: null;
		}
	}

	static inline function equalsCI(a: String, b: String): Bool {
		return a.toLowerCase() == b.toLowerCase();
	}
}
