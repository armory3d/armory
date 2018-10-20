package armory.system;

using haxe.EnumTools;

import haxe.macro.Type;
import haxe.macro.Context;

/**
	Contains macros for helping with modding.
**/
class Modding {

#if !macro

    /**
     * Load all mods referenced in a file. Each line in the file should be the name of a
     * mod to enable.
     * 
     * @param modListFile The path to the file containing the mod list
     * @param done Callback for when mods are finished
	 * @param onload Callback called for each mod loaded
     */
    static public function loadModsFromListFile(modListFile:String, done:() -> Void, onLoad:(modName:String) -> Void = null) {
		iron.data.Data.getBlob(modListFile, (blob:kha.Blob) -> {
			var modList = blob.toString().split("\n");
			for (mod in modList) {
				if (mod == "") break;
				// Load Mod code
				trace('Loading mod: $mod');

				iron.data.Data.getBlob('Mods/$mod/krom.js', (b:kha.Blob) -> {
					var code = b.toString();
					untyped __js__("(1, eval)({0})", code);
					if (onLoad != null) onLoad(mod);
				});
			}
		});
		done();
    }
#elseif macro
	/**
	 * Expose a package to modding languages. This allows mods to reference
	 * functions and classes in that package and all subpackages.
	 * 
	 * @param package The name of the package to be exposed.
	 */
	static public function exposePack(pack:String) {
		Context.onAfterTyping(function (types:Array<ModuleType>) {
			for (module in types) {
				var moduleRef:Ref<ModuleType> = module.getParameters()[0];
				var className = moduleRef.toString();
				var baseModule:BaseType = cast moduleRef.get();

                if (StringTools.startsWith(className, pack)) {
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
	 * Generate only the classes that match the given regex pattern.
	 */
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
	 * Exclude a class or an enum without changing it to `@:nativeGen`.
	 */
	static private function excludeBaseType( baseType : BaseType ) : Void {
		if (!baseType.isExtern) {
			var meta = baseType.meta;
			if (!meta.has(":nativeGen")) {
				meta.add(":hxGen", [], baseType.pos);
			}
			baseType.exclude();
		}
	}
#end
}
