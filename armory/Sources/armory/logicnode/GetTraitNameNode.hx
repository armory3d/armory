package armory.logicnode;

import iron.Trait;

class GetTraitNameNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var trait: Dynamic = inputs[0].get();
        if (trait == null) return null;
       	switch (from) { 
			// Name
			case 0: {
			// Check CanvasScript
			var cname = cast Type.resolveClass("armory.trait.internal.CanvasScript");
			if (Std.isOfType(trait, cname)) {
				return trait.cnvName;
			}
			// Check WasmScript
			var cname = cast Type.resolveClass("armory.trait.internal.WasmScript");
			if (Std.isOfType(trait, cname)) {
				return trait.wasmName;
			}
			// Other
            var res_arr = (Type.getClassName(Type.getClass(trait))).split(".");
            return res_arr[res_arr.length - 1];
			}
			// Class Type
			case 1: {
				var cname = Type.getClassName(Type.getClass(trait));
				if (cname.indexOf("CanvasScript") > -1) return "Canvas";
				if (cname.indexOf("WasmScript") > -1) return "Wasm";
				if (cname.indexOf("armory.trait.") > -1) return "Bundle";
				if (cname.indexOf("arm.node.") > -1) return "LogicNode";
				if (cname.indexOf("Trait") > -1) return "Haxe";
				return null;
			}
		}
		return null;
	}
}
