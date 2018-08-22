package armory.system;

using haxe.EnumTools;

import haxe.macro.Type;
import haxe.macro.Context;

/**
	Contains macros for helping with modding.
**/
class Modding {
	/**
		Bind/expose classes and methods to the modding languages.
	**/
	static public function bindClasses(patternStr:String) {
        var pattern = new EReg(patternStr, "g");
		Context.onAfterTyping(function (types:Array<ModuleType>) {
			for (module in types) {
				var moduleRef:Ref<ModuleType> = module.getParameters()[0];
				var className = moduleRef.toString();
				var baseModule:BaseType = cast moduleRef.get();

                if (pattern.match(className)) {
                    // Expose classes to Javascript
                    if (Context.defined('js')) {
                        baseModule.meta.add(":expose", [], baseModule.pos);
                    }
                }
			}
		});
	}

	//
	// Macros below modified slightly from the haxe.macro.Compiler class
	// from the standard library.
	//

	/**
		Generate only the classes that match the given regex pattern.
	**/
	static public function generateOnlyClasses( patternStr : String ) {
		var pattern = new EReg(patternStr, "g");
		Context.onGenerate(function(types) {
			for( t in types ) {
				var b : BaseType, name;
				switch( t ) {
				case TInst(c, _):
					name = c.toString();
					b = c.get();
				case TEnum(e, _):
					name = e.toString();
					b = e.get();
				default: continue;
				}
				var classPath = '${b.pack.join(".")}.$name';

				// If pattern is not matched, exclude class from compilation.
				if( !pattern.match(classPath) )
					excludeBaseType(b);
			}
		});
	}

	/**
		Exclude a class or an enum without changing it to `@:nativeGen`.
	**/
	static private function excludeBaseType( baseType : BaseType ) : Void {
		if (!baseType.isExtern) {
			var meta = baseType.meta;
			if (!meta.has(":nativeGen")) {
				meta.add(":hxGen", [], baseType.pos);
			}
			baseType.exclude();
		}
	}
}