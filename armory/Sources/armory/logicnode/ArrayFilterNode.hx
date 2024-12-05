package armory.logicnode;

import iron.math.Vec4;

class ArrayFilterNode extends LogicNode {

	public var property0: String;
	public var property1: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();
		
		var type: Dynamic;
		
		if(property0 == 'Item')
			type = inputs[1].get();
		else
			type = inputs[2].get();
			
		var prop: String = inputs[1].get();
		
		var arr: Array<Dynamic> = null;

		if(property0 == 'Item'){
			if(Std.isOfType(type, Vec4)){
				var value: Vec4 = inputs[1].get();
				switch(property1){
					case 'Equal': arr = ar.filter(item -> item.equals(value));
					case 'Not Equal': arr = ar.filter(item -> !item.equals(value));
					case 'Between': { 
						var value2: Vec4 = inputs[2].get();
						arr = ar.filter(item -> value.x <= item.x && value.y <= item.y && value.z <= item.z && item.x <= value2.x && item.y <= value2.y && item.z <= value2.z);
					}
				}
			}
			else if(Std.isOfType(type, String)){
				var value: String = inputs[1].get();
				switch(property1){
					case 'Equal': arr = ar.filter(item -> item == value);
					case 'Not Equal': arr = ar.filter(item -> item != value);
					case 'Contains': arr = ar.filter(item -> item.indexOf(value) >= 0);
					case 'Starts With': arr = ar.filter(item -> StringTools.startsWith(item, value));
					case 'Ends With': arr = ar.filter(item -> StringTools.endsWith(item, value));			
				}
			}
			else{
				var value = inputs[1].get();
				switch(property1){
					case 'Equal': arr = ar.filter(item -> item == value);
					case 'Not Equal': arr = ar.filter(item -> item != value);
					case 'Between': { var value2 = inputs[2].get(); arr = ar.filter(item -> value <= item && item <= value2); }
					case 'Less': arr = ar.filter(item -> item < value);
					case 'Less Equal': arr = ar.filter(item -> item <=  value);
					case 'Greater': arr = ar.filter(item -> item > value);
					case 'Greater Equal': arr = ar.filter(item -> item >= value);
				}
			}
		}
		else if(property0 == 'Item Field'){
			if(Std.isOfType(type, Vec4)){
				var value: Vec4 = inputs[2].get();
				switch(property1){
					case 'Equal': arr = ar.filter(item -> Reflect.field(item, prop).equals(value));
					case 'Not Equal': arr = ar.filter(item -> !Reflect.field(item, prop).equals(value));
					case 'Between': { 
						var value2: Vec4 = inputs[2].get();
						arr = ar.filter(item -> value.x <= Reflect.field(item, prop).x && value.y <= Reflect.field(item, prop).y && value.z <= Reflect.field(item, prop).z && Reflect.field(item, prop).x <= value2.x && Reflect.field(item, prop).y <= value2.y && Reflect.field(item, prop).z <= value2.z);
					}
				}
			}
			else if(Std.isOfType(type, String)){
				var value: String = inputs[2].get();
				switch(property1){
					case 'Equal': arr = ar.filter(item -> Reflect.field(item, prop) == value);
					case 'Not Equal': arr = ar.filter(item -> Reflect.field(item, prop) != value);
					case 'Contains': arr = ar.filter(item -> Reflect.field(item, prop).indexOf(value) >= 0);
					case 'Starts With': arr = ar.filter(item -> StringTools.startsWith(Reflect.field(item, prop), value));
					case 'Ends With': arr = ar.filter(item -> StringTools.endsWith(Reflect.field(item, prop), value));				
				}
			}
			else{
				var value: Dynamic = inputs[2].get();
				switch(property1){
					case 'Equal': arr = ar.filter(item -> Reflect.field(item, prop) == value);
					case 'Not Equal': arr = ar.filter(item -> Reflect.field(item, prop) != value);
					case 'Between': { var value2: Dynamic = inputs[2].get(); arr = ar.filter(item -> value <= Reflect.field(item, prop) && Reflect.field(item, prop) <= value2); }
					case 'Less': arr = ar.filter(item -> Reflect.field(item, prop) < value);
					case 'Less Equal': arr = ar.filter(item -> Reflect.field(item, prop) <= value);
					case 'Greater': arr = ar.filter(item -> Reflect.field(item, prop) > value);
					case 'Greater Equal': arr = ar.filter(item -> Reflect.field(item, prop) >= value);
				}
			}
		}
		else if(property0 == 'Item Property'){
			if(Std.isOfType(type, Vec4)){
					var value: Vec4 = inputs[2].get();
					switch(property1){
						case 'Equal': arr = ar.filter(item -> Reflect.field(item.properties.h, prop).equals(value));
						case 'Not Equal': arr = ar.filter(item -> !Reflect.field(item.properties.h, prop).equals(value));
						case 'Between': { 
							var value2: Vec4 = inputs[2].get();
							arr = ar.filter(item -> value.x <= Reflect.field(item.properties.h, prop).x && value.y <= Reflect.field(item.properties.h, prop).y && value.z <= Reflect.field(item.properties.h, prop).z && Reflect.field(item.properties.h, prop).x <= value2.x && Reflect.field(item.properties.h, prop).y <= value2.y && Reflect.field(item.properties.h, prop).z <= value2.z);
						}
					}
				}
				else if(Std.isOfType(type, String)){
					var value: String = inputs[2].get();
					switch(property1){
						case 'Equal': arr = ar.filter(item -> Reflect.field(item.properties.h, prop) == value);
						case 'Not Equal': arr = ar.filter(item -> Reflect.field(item.properties.h, prop) != value);
						case 'Contains': arr =  ar.filter(item -> Reflect.field(item.properties.h, prop).indexOf(value) >= 0);
						case 'Starts With': arr = ar.filter(item -> StringTools.startsWith(Reflect.field(item.properties.h, prop), value));
						case 'Ends With': arr = ar.filter(item -> StringTools.endsWith(Reflect.field(item.properties.h, prop), value));				
					}
				}
				else{
					var value: Dynamic = inputs[2].get();
					switch(property1){
						case 'Equal': arr = ar.filter(item -> Reflect.field(item.properties.h, prop) == value);
						case 'Not Equal': arr = ar.filter(item -> Reflect.field(item.properties.h, prop) != value);
						case 'Between': { var value2: Dynamic = inputs[2].get(); arr = ar.filter(item -> value <= Reflect.field(item.properties.h, prop) && Reflect.field(item.properties.h, prop) <= value2); }
						case 'Less': arr = ar.filter(item -> Reflect.field(item.properties.h, prop) < value);
						case 'Less Equal': arr = ar.filter(item -> Reflect.field(item.properties.h, prop) <= value);
						case 'Greater': arr = ar.filter(item -> Reflect.field(item.properties.h, prop) > value);
						case 'Greater Equal': arr = ar.filter(item -> Reflect.field(item.properties.h, prop) >= value);
					}
				}
		}
		
		return arr;

	}
}