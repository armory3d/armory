package armory.logicnode;
import iron.object.Object;
import iron.math.Vec4;
import armory.system.Event;


class CreateMapNode extends LogicNode {
  public var property0: String;
  public var property1: String;
  public var map: Map<Dynamic,Dynamic>;


	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		if(property0 == "string"){
        switch (property1) {
            case "string":
            		map = new Map<String, String>();
					runOutput(0);
            case "vector":
            		map = new Map<String, Vec4>();
					runOutput(0);
            case "float":
            		map = new Map<String, Float>();
					runOutput(0);
            case "integer":
            		map = new Map<String, Int>();
					runOutput(0);
            case "boolean":
            		map = new Map<String, Bool>();
					runOutput(0);
            case "dynamic":
            		map = new Map<String, Dynamic>();
					runOutput(0);
            default: throw "Failed to create Map";
        }
		} else if (property0 == "int"){
        switch (property1) {
            case "string":
            		map = new Map<Int, String>();
					runOutput(0);
            case "vector":
            		map = new Map<Int, Vec4>();
					runOutput(0);
            case "float":
            		map = new Map<Int, Float>();
					runOutput(0);
            case "integer":
            		map = new Map<Int, Int>();
					runOutput(0);
            case "boolean":
            		map = new Map<Int, Bool>();
					runOutput(0);
            case "dynamic":
            		map = new Map<Int, Dynamic>();
					runOutput(0);
            default: throw "Failed to create Map";
        }
		} else if (property0 == "enumvalue"){
        switch (property1) {
            case "string":
            		map = new Map<EnumValue,String>();
					runOutput(0);
            case "vector":
            		map = new Map<EnumValue,Vec4>();
					runOutput(0);
            case "float":
            		map = new Map<EnumValue,Float>();
					runOutput(0);
            case "integer":
            		map = new Map<EnumValue,Int>();
					runOutput(0);
            case "boolean":
            		map = new Map<EnumValue,Bool>();
					runOutput(0);
            case "dynamic":
            		map = new Map<EnumValue,Dynamic>();
					runOutput(0);
            default: throw "Failed to create Map";
        }
		} else if (property0 == "object"){
        switch (property1) {
            case "string":
            		map = new Map<{},String>();
					runOutput(0);
            case "vector":
            		map = new Map<{},Vec4>();
					runOutput(0);
            case "float":
            		map = new Map<{},Float>();
					runOutput(0);
            case "integer":
            		map = new Map<{},Int>();
					runOutput(0);
            case "boolean":
            		map = new Map<{},Bool>();
					runOutput(0);
            case "dynamic":
            		map = new Map<{},Dynamic>();
					runOutput(0);
            default: throw "Failed to create Map";
        }
		}
	}

	override function get(from: Int): Map<Dynamic,Dynamic> {
        return map;
    }

}

