package armory.logicnode;

class GetSystemName extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);		
	}

	public static function equalsCI(a : String, b : String) return a.toLowerCase() == b.toLowerCase();

	override function get(from: Int): Dynamic {

		return switch (from) {
			case 0: systemName;
			case 1: equalsCI(kha.System.systemId, 'Windows');
			case 2: equalsCI(kha.System.systemId, 'Linux');
			case 3: equalsCI(kha.System.systemId, 'Mac');
			case 4: equalsCI(kha.System.systemId, 'HTML5');
			case 5: equalsCI(kha.System.systemId, 'Android');
			default: null;
		}

	}
}
