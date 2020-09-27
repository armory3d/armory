package armory.logicnode;

class GetSystemName extends LogicNode {
   
	// New (constructor)
	public function new(tree: LogicTree) {
		super(tree);		
	}

    public static function equalsCI(a : String, b : String) return a.toLowerCase() == b.toLowerCase();
	
    // Get - out
	override function get(from: Int): Dynamic {
        switch (from) {
            // Out value - Value (string)
			case 0: return kha.System.systemId;
			case 1: return equalsCI(kha.System.systemId, 'Windows');
			case 2: return equalsCI(kha.System.systemId, 'Linux');
			case 3: return equalsCI(kha.System.systemId, 'Mac');
			case 4: return equalsCI(kha.System.systemId, 'HTML5');
			case 5: return equalsCI(kha.System.systemId, 'Android');
		}
		return null;
	}
}