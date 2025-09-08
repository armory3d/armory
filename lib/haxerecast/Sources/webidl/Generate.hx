package webidl;
import webidl.Data;

class Generate {

	static var HEADER_EMSCRIPTEN = "

#include <emscripten.h>
#define HL_PRIM
#define HL_NAME(n)	EMSCRIPTEN_KEEPALIVE eb_##n
#define DEFINE_PRIM(ret, name, args)
#define _OPT(t) t*
#define _GET_OPT(value,t) *value


";

	static var HEADER_HL = "

#include <hl.h>
#define _IDL _BYTES
#define _OPT(t) vdynamic *
#define _GET_OPT(value,t) (value)->v.t


";

	static var HEADER_NO_GC = "

#define alloc_ref(r, _) r
#define alloc_ref_const(r,_) r
#define _ref(t)			t
#define _unref(v)		v
#define free_ref(v) delete (v)
#define HL_CONST const

	";

	static var HEADER_GC = "

template <typename T> struct pref {
	void *finalize;
	T *value;
};

#define _ref(t) pref<t>
#define _unref(v) v->value
#define alloc_ref(r,t) _alloc_ref(r,finalize_##t)
#define alloc_ref_const(r, _) _alloc_const(r)
#define HL_CONST

template<typename T> void free_ref( pref<T> *r ) {
	if( !r->finalize ) hl_error(\"delete() is not allowed on const value.\");
	delete r->value;
	r->value = NULL;
	r->finalize = NULL;
}

template<typename T> pref<T> *_alloc_ref( T *value, void (*finalize)( pref<T> * ) ) {
	pref<T> *r = (pref<T>*)hl_gc_alloc_finalizer(sizeof(pref<T>));
	r->finalize = finalize;
	r->value = value;
	return r;
}

template<typename T> pref<T> *_alloc_const( const T *value ) {
	pref<T> *r = (pref<T>*)hl_gc_alloc_noptr(sizeof(pref<T>));
	r->finalize = NULL;
	r->value = (T*)value;
	return r;
}

";

	static function initOpts( opts : Options ) {
		if( opts.outputDir == null )
			opts.outputDir = "";
		else if( !StringTools.endsWith(opts.outputDir,"/") )
			opts.outputDir += "/";
	}

	public static function generateCpp( opts : Options ) {

		initOpts(opts);

		var file = opts.idlFile;
		var content = sys.io.File.getBytes(file);
		var parse = new webidl.Parser();
		var decls = null;
		var gc = opts.autoGC;
		try {
			decls = parse.parseFile(file, new haxe.io.BytesInput(content));
		} catch( msg : String ) {
			throw msg + "(" + file+" line " + parse.line+")";
		}
		var output = new StringBuf();
		function add(str:String) {
			output.add(str.split("\r\n").join("\n") + "\n");
		}
		add("#ifdef EMSCRIPTEN");
		add("");
		add(StringTools.trim(HEADER_EMSCRIPTEN));
		add(StringTools.trim(HEADER_NO_GC));
		add("");
		add("#else");
		add("");
		add('#define HL_NAME(x) ${opts.nativeLib}_##x');
		add(StringTools.trim(HEADER_HL));
		add(StringTools.trim(gc ? HEADER_GC : HEADER_NO_GC));
		add("");
		add("#endif");
		if( opts.includeCode != null ) {
			add("");
			add(StringTools.trim(opts.includeCode));
		}
		add("");
		add('extern "C" {');
		add("");

		var typeNames = new Map();
		var enumNames = new Map();

		// ignore "JSImplementation" interfaces (?)
		for( d in decls.copy() )
			switch( d.kind ) {
			case DInterface(_, attrs, _):
				for( a in attrs )
					switch( a ) {
					case AJSImplementation(_):
						decls.remove(d);
						break;
					default:
					}
			default:
			}

		for( d in decls ) {
			switch( d.kind ) {
			case DInterface(name, attrs, _):
				var prefix = "";
				for( a in attrs )
					switch( a ) {
					case APrefix(name): prefix = name;
					default:
					}
				var fullName = "_ref(" + prefix + name+")*";
				typeNames.set(name, { full : fullName, constructor : prefix + name });
				if( attrs.indexOf(ANoDelete) >= 0 )
					continue;
				add('static void finalize_$name( $fullName _this ) { free_ref(_this); }');
				add('HL_PRIM void HL_NAME(${name}_delete)( $fullName _this ) {\n\tfree_ref(_this);\n}');
				add('DEFINE_PRIM(_VOID, ${name}_delete, _IDL);');
			case DEnum(name, values):
				enumNames.set(name, true);
				typeNames.set(name, { full : "int", constructor : null });
				add('static $name ${name}__values[] = { ${values.join(",")} };');
			case DImplements(_):
			}
		}

		function getEnumName( t : webidl.Data.Type ) {
			return switch( t ) {
			case TCustom(id): enumNames.exists(id) ? id : null;
			default: null;
			}
		}

		function makeType( t : webidl.Data.Type ) {
			return switch( t ) {
			case TFloat: "float";
			case TDouble: "double";
			case TShort: "short";
			case TInt: "int";
			case TVoid: "void";
			case TAny, TVoidPtr: "void*";
			case TArray(t): makeType(t) + "*";
			case TBool: "bool";
			case TCustom(id): typeNames.get(id).full;
			}
		}

		function defType( t ) {
			return switch( t ) {
			case TFloat: "_F32";
			case TDouble: "_F64";
			case TShort: "_I16";
			case TInt: "_I32";
			case TVoid: "_VOID";
			case TAny, TVoidPtr: "_BYTES";
			case TArray(t): "_BYTES";
			case TBool: "_BOOL";
			case TCustom(name): enumNames.exists(name) ? "_I32" : "_IDL";
			}
		}

		function dynamicAccess(t) {
			return switch( t ) {
			case TFloat: "f";
			case TDouble: "d";
			case TShort: "ui16";
			case TInt: "i";
			case TBool: "b";
			default: throw "assert";
			}
		}

		function makeTypeDecl( td : TypeAttr ) {
			var prefix = "";
			for( a in td.attr ) {
				switch( a ) {
				case AConst: prefix += "HL_CONST ";
				default:
				}
			}
			return prefix + makeType(td.t);
		}

		function isDyn( arg : { opt : Bool, t : TypeAttr } ) {
			return arg.opt && !arg.t.t.match(TCustom(_));
		}

		for( d in decls ) {
			switch( d.kind ) {
			case DInterface(name, attrs, fields):
				for( f in fields ) {
					switch( f.kind ) {
					case FMethod(margs, ret):
						var isConstr = f.name == name;
						var args = isConstr ? margs : [{ name : "_this", t : { t : TCustom(name), attr : [] }, opt : false }].concat(margs);
						var tret = isConstr ? { t : TCustom(name), attr : [] } : ret;
						var funName = name + "_" + (isConstr ? "new" + args.length : f.name + (args.length - 1));
						output.add('HL_PRIM ${makeTypeDecl(tret)} HL_NAME($funName)(');
						var first = true;
						for( a in args ) {
							if( first ) first = false else output.add(", ");
							if( isDyn(a) )
								output.add("_OPT("+makeType(a.t.t)+")");
							else
								output.add(makeType(a.t.t));
							output.add(" " + a.name);
						}
						add(') {');


						function addCall(margs : Array<{ name : String, opt : Bool, t : TypeAttr }> ) {
							var refRet = null;
							var enumName = getEnumName(tret.t);
							if( isConstr ) {
								refRet = name;
								output.add('return alloc_ref((new ${typeNames.get(refRet).constructor}(');
							} else {
								if( tret.t != TVoid ) output.add("return ");
								for( a in ret.attr ) {
									switch( a ) {
									case ARef, AValue:
										refRet = switch(tret.t) {
										case TCustom(id): id;
										default: throw "assert";
										}
										if( a == ARef && tret.attr.indexOf(AConst) >= 0 )
											output.add('alloc_ref_const(&('); // we shouldn't call delete() on this one !
										else
											output.add('alloc_ref(new ${typeNames.get(refRet).constructor}(');
									default:
									}
								}
								if( enumName != null )
									output.add('make__$enumName(');
								else if( refRet == null && ret.t.match(TCustom(_)) ) {
									refRet = switch(tret.t) {
									case TCustom(id): id;
									default: throw "assert";
									}
									if( tret.attr.indexOf(AConst) >= 0 )
										output.add('alloc_ref_const((');
									else
										output.add('alloc_ref((');
								}

								switch( f.name ) {
								case "op_mul":
									output.add("*_unref(_this) * (");
								case "op_add":
									output.add("*_unref(_this) + (");
								case "op_sub":
									output.add("*_unref(_this) - (");
								case "op_div":
									output.add("*_unref(_this) / (");
								case "op_mulq":
									output.add("*_unref(_this) *= (");
								default:
									output.add("_unref(_this)->" + f.name+"(");
								}
							}

							var first = true;
							for( a in margs ) {
								if( first ) first = false else output.add(", ");
								for( a in a.t.attr ) {
									switch( a ) {
									case ARef: output.add("*"); // unref
									default:
									}
								}
								var e = getEnumName(a.t.t);
								if( e != null )
									output.add('${e}__values[${a.name}]');
								else switch( a.t.t ) {
								case TCustom(_):
									output.add('_unref(${a.name})');
								default:
									if( isDyn(a) ) {
										output.add("_GET_OPT("+a.name+","+dynamicAccess(a.t.t)+")");
									} else
										output.add(a.name);
								}
							}

							if( enumName != null ) output.add(')');
							if( refRet != null ) output.add(')),$refRet');
							add(");");
						}

						var hasOpt = false;
						for( i in 0...margs.length )
							if( margs[i].opt ) {
								hasOpt = true;
								break;
							}
						if( hasOpt ) {

							for( i in 0...margs.length )
								if( margs[i].opt ) {
									add("\tif( !" + margs[i].name+" )");
									output.add("\t\t");
									addCall(margs.slice(0, i));
									add("\telse");
								}
							output.add("\t\t");
							addCall(margs);

						} else {
							output.add("\t");
							addCall(margs);
						}
						add('}');
						output.add('DEFINE_PRIM(${defType(tret.t)}, $funName,');
						for( a in args )
							output.add(' ' + (isDyn(a) ? "_NULL(" + defType(a.t.t)+")" : defType(a.t.t)));
						add(');');
						add('');


					case FAttribute(t):
						var isVal = t.attr.indexOf(AValue) >= 0;
						var tname = switch( t.t ) { case TCustom(id): id; default: null; };
						var isRef = tname != null;
						var enumName = getEnumName(t.t);
						var isConst = t.attr.indexOf(AConst) >= 0;

						if( enumName != null ) throw "TODO : enum attribute";

						add('HL_PRIM ${makeTypeDecl(t)} HL_NAME(${name}_get_${f.name})( ${typeNames.get(name).full} _this ) {');
						if( isVal ) {
							var fname = typeNames.get(tname).constructor;
							add('\treturn alloc_ref(new $fname(_unref(_this)->${f.name}),$tname);');
						} else if( isRef )
							add('\treturn alloc_ref${isConst?'_const':''}(_unref(_this)->${f.name},$tname);');
						else
							add('\treturn _unref(_this)->${f.name};');
						add('}');

						add('HL_PRIM ${makeTypeDecl(t)} HL_NAME(${name}_set_${f.name})( ${typeNames.get(name).full} _this, ${makeTypeDecl(t)} value ) {');
						add('\t_unref(_this)->${f.name} = ${isVal?"*":""}${isRef?"_unref":""}(value);');
						add('\treturn value;');
						add('}');

						var td = defType(t.t);
						add('DEFINE_PRIM($td,${name}_get_${f.name},_IDL);');
						add('DEFINE_PRIM($td,${name}_set_${f.name},_IDL $td);');
						add('');
					case DConst(_, _, _):
					}
				}

			case DEnum(_), DImplements(_):
			}
		}

		add("}"); // extern C

		sys.io.File.saveContent(opts.outputDir + opts.nativeLib+".cpp", output.toString());
	}

	static function command( cmd, args : Array<String> ) {
		Sys.println("> " + cmd + " " + args.join(" "));
		var ret = Sys.command(cmd, args);
		if( ret != 0 ) throw "Command '" + cmd + "' has exit with error code " + ret;
	}

	public static function generateJs( opts : Options, sources : Array<String>, ?params : Array<String> ) {
		if( params == null )
			params = [];

		initOpts(opts);

		var hasOpt = false;
		for( p in params )
			if( p.substr(0, 2) == "-O" )
				hasOpt = true;
		if( !hasOpt )
			params.push("-O2");

		var lib = opts.nativeLib;

		var emSdk = Sys.getEnv("EMSCRIPTEN");
		if( emSdk == null )
			throw "Missing EMSCRIPTEN environment variable. Install emscripten";
		var emcc = emSdk + "/emcc";

		// build sources BC files
		var outFiles = [];
		sources.push(lib+".cpp");
		for( cfile in sources ) {
			var out = opts.outputDir + cfile.substr(0, -4) + ".bc";
			var args = params.concat(["-c", cfile, "-o", out]);
			command( emcc, args);
			outFiles.push(out);
		}

		// link : because too many files, generate Makefile
		var tmp = opts.outputDir + "Makefile.tmp";
		var args = params.concat([
			"-s", 'EXPORT_NAME="\'$lib\'"', "-s", "MODULARIZE=1",
			"--memory-init-file", "0",
			"-o", '$lib.js'
		]);
		var output = "SOURCES = " + outFiles.join(" ") + "\n";
		output += "all:\n";
		output += "\t"+emcc+" $(SOURCES) " + args.join(" ");
		sys.io.File.saveContent(tmp, output);
		command("make", ["-f", tmp]);
		sys.FileSystem.deleteFile(tmp);
	}


}
