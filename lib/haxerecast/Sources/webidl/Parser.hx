package webidl;
import webidl.Data;

private enum Token {
	TEof;
	TId( s : String );
	TPOpen;
	TPClose;
	TBrOpen;
	TBrClose;
	TBkOpen;
	TBkClose;
	TSemicolon;
	TComma;
	TOp( op : String );
	TString( str : String );
}


class Parser {

	public var line : Int;
	var input : haxe.io.Input;
	var char : Int;
	var ops : Array<Bool>;
	var idents : Array<Bool>;
	var tokens : Array<Token>;
	var pos = 0;
	var fileName : String;

	public function new() {
		var opChars = "+*/-=!><&|^%~";
		var identChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_";
		idents = new Array();
		ops = new Array();
		for( i in 0...identChars.length )
			idents[identChars.charCodeAt(i)] = true;
		for( i in 0...opChars.length )
			ops[opChars.charCodeAt(i)] = true;
	}

	public function parseFile( fileName : String, input : haxe.io.Input ) {
		this.fileName = fileName;
		pos = 0;
		line = 1;
		char = -1;
		tokens = [];
		this.input = input;
		var out = [];
		while( true ) {
			var tk = token();
			if( tk == TEof ) break;
			push(tk);
			out.push(parseDecl());
		}
		return out;
	}

	function parseDecl() {
		var attr = attributes();
		var pmin = this.pos;
		switch( token() ) {
		case TId("interface"):
			var name = ident();
			ensure(TBrOpen);
			var fields = [];
			while( true ) {
				var tk = token();
				if( tk == TBrClose ) break;
				push(tk);
				fields.push(parseField());
			}
			ensure(TSemicolon);
			return { pos : makePos(pmin), kind : DInterface(name, attr, fields) };
		case TId("enum"):
			var name = ident();
			ensure(TBrOpen);
			var values = [];
			if( !maybe(TBrClose) )
				while( true ) {
					switch( token() ) {
					case TString(str): values.push(str);
					case var tk: unexpected(tk);
					}
					switch( token() ) {
					case TBrClose: break;
					case TComma: continue;
					case var tk: unexpected(tk);
					}
				}
			ensure(TSemicolon);
			return { pos : makePos(pmin), kind : DEnum(name, values) };
		case TId(name):
			if( attr.length > 0 )
				throw "assert";
			ensure(TId("implements"));
			var intf = ident();
			ensure(TSemicolon);
			return { pos : makePos(pmin), kind : DImplements(name, intf) };

		case var tk:
			return unexpected(tk);
		}
	}

	function attributes() {
		if( !maybe(TBkOpen) )
			return [];
		var attrs = [];
		while( true ) {
			var attr = switch( ident() ) {
			case "Value": AValue;
			case "Ref": ARef;
			case "Const": AConst;
			case "NoDelete": ANoDelete;
			case "Prefix":
				ensure(TOp("="));
				APrefix(switch( token() ) { case TString(s): s; case var tk: unexpected(tk); });
			case "JSImplementation":
				ensure(TOp("="));
				AJSImplementation(switch( token() ) { case TString(s): s; case var tk: unexpected(tk); });
			case "Operator":
				ensure(TOp("="));
				AOperator(switch( token() ) { case TString(s): s; case var tk: unexpected(tk); });
			case var attr:
				error("Unsupported attribute " + attr);
				null;
			}
			attrs.push(attr);
			if( !maybe(TComma) ) break;
		}
		ensure(TBkClose);
		return attrs;
	}

	function type() : Type {
		var id = ident();
		var t = switch( id ) {
		case "void": TVoid;
		case "float": TFloat;
		case "double": TDouble;
		case "long", "int": TInt; // long ensures 32 bits
		case "short": TShort;
		case "boolean", "bool": TBool;
		case "any": TAny;
		case "VoidPtr": TVoidPtr;
		default: TCustom(id);
		};
		if( maybe(TBkOpen) ) {
			ensure(TBkClose);
			t = TArray(t);
		}
		return t;
	}

	function makePos( pmin : Int ) {
		return { file : fileName, line : line, pos : pmin };
	}

	function parseField() : Field {
		var attr = attributes();
		var pmin = this.pos;

		if( maybe(TId("attribute")) ) {
			var t = type();
			var name = ident();
			ensure(TSemicolon);
			return { name : name, kind : FAttribute({ t : t, attr : attr }), pos : makePos(pmin) };
		}

		if( maybe(TId("const")) ) {
			var type = type();
			var name = ident();
			ensure(TOp("="));
			var value = tokenString(token());
			ensure(TSemicolon);
			return { name: name, kind : DConst(name, type, value), pos : makePos(pmin) };
		}

		var tret = type();
		var name = ident();
		ensure(TPOpen);
		var args = [];
		if( !maybe(TPClose) ) {
			while( true ) {
				var attr = attributes();
				var opt = maybe(TId("optional"));
				var t = type();
				var name = ident();
				args.push({ name : name, t : { t : t, attr : attr }, opt : opt });
				switch( token() ) {
				case TPClose:
					break;
				case TComma:
					continue;
				case var tk:
					unexpected(tk);
				}
			}
		}
		ensure(TSemicolon);
		return { name : name, kind : FMethod(args, { attr : attr, t : tret }), pos : makePos(pmin) };
	}

	// --- Lexing

	function invalidChar(c:Int) {
		error("Invalid char "+c+"("+String.fromCharCode(c)+")");
	}

	function error( msg : String ) {
		throw msg+" line "+line;
	}

	function unexpected( tk ) : Dynamic {
		error("Unexpected " + tokenString(tk));
		return null;
	}

	function tokenString( tk ) {
		return switch( tk ) {
		case TEof: "<eof>";
		case TId(id): id;
		case TPOpen: "(";
		case TPClose: ")";
		case TBkOpen: "[";
		case TBkClose: "]";
		case TBrOpen: "{";
		case TBrClose: "}";
		case TComma: ",";
		case TSemicolon: ";";
		case TOp(op): op;
		case TString(str): '"' + str + '"';
		}
	}

	inline function push(tk) {
		tokens.push(tk);
	}

	function ensure(tk) {
		var t = token();
		if( t != tk && !std.Type.enumEq(t,tk) ) unexpected(t);
	}

	function maybe(tk) {
		var t = token();
		if( t == tk || std.Type.enumEq(t,tk) )
			return true;
		push(t);
		return false;
	}

	function ident() {
		var tk = token();
		switch( tk ) {
		case TId(id): return id;
		default:
			unexpected(tk);
			return null;
		}
	}

	function readChar() {
		pos++;
		return try input.readByte() catch( e : Dynamic ) 0;
	}

	function token() : Token {
		if( tokens.length > 0 )
			return tokens.shift();
		var char;
		if( this.char < 0 )
			char = readChar();
		else {
			char = this.char;
			this.char = -1;
		}
		while( true ) {
			switch( char ) {
			case 0: return TEof;
			case 32,9,13: // space, tab, CR
			case 10: line++; // LF
/*			case 48,49,50,51,52,53,54,55,56,57: // 0...9
				var n = (char - 48) * 1.0;
				var exp = 0.;
				while( true ) {
					char = readChar();
					exp *= 10;
					switch( char ) {
					case 48,49,50,51,52,53,54,55,56,57:
						n = n * 10 + (char - 48);
					case 46:
						if( exp > 0 ) {
							// in case of '...'
							if( exp == 10 && readChar() == 46 ) {
								push(TOp("..."));
								var i = Std.int(n);
								return TConst( (i == n) ? CInt(i) : CFloat(n) );
							}
							invalidChar(char);
						}
						exp = 1.;
					case 120: // x
						if( n > 0 || exp > 0 )
							invalidChar(char);
						// read hexa
						#if haxe3
						var n = 0;
						while( true ) {
							char = readChar();
							switch( char ) {
							case 48,49,50,51,52,53,54,55,56,57: // 0-9
								n = (n << 4) + char - 48;
							case 65,66,67,68,69,70: // A-F
								n = (n << 4) + (char - 55);
							case 97,98,99,100,101,102: // a-f
								n = (n << 4) + (char - 87);
							default:
								this.char = char;
								return TConst(CInt(n));
							}
						}
						#else
						var n = haxe.Int32.ofInt(0);
						while( true ) {
							char = readChar();
							switch( char ) {
							case 48,49,50,51,52,53,54,55,56,57: // 0-9
								n = haxe.Int32.add(haxe.Int32.shl(n,4), cast (char - 48));
							case 65,66,67,68,69,70: // A-F
								n = haxe.Int32.add(haxe.Int32.shl(n,4), cast (char - 55));
							case 97,98,99,100,101,102: // a-f
								n = haxe.Int32.add(haxe.Int32.shl(n,4), cast (char - 87));
							default:
								this.char = char;
								// we allow to parse hexadecimal Int32 in Neko, but when the value will be
								// evaluated by Interpreter, a failure will occur if no Int32 operation is
								// performed
								var v = try CInt(haxe.Int32.toInt(n)) catch( e : Dynamic ) CInt32(n);
								return TConst(v);
							}
						}
						#end
					default:
						this.char = char;
						var i = Std.int(n);
						return TConst( (exp > 0) ? CFloat(n * 10 / exp) : ((i == n) ? CInt(i) : CFloat(n)) );
					}
				}*/
			case 59: return TSemicolon;
			case 40: return TPOpen;
			case 41: return TPClose;
			case 44: return TComma;
/*			case 46:
				char = readChar();
				switch( char ) {
				case 48,49,50,51,52,53,54,55,56,57:
					var n = char - 48;
					var exp = 1;
					while( true ) {
						char = readChar();
						exp *= 10;
						switch( char ) {
						case 48,49,50,51,52,53,54,55,56,57:
							n = n * 10 + (char - 48);
						default:
							this.char = char;
							return TConst( CFloat(n/exp) );
						}
					}
				case 46:
					char = readChar();
					if( char != 46 )
						invalidChar(char);
					return TOp("...");
				default:
					this.char = char;
					return TDot;
				}*/
			case 123: return TBrOpen;
			case 125: return TBrClose;
			case 91: return TBkOpen;
			case 93: return TBkClose;
			case 39: return TString(readString(39));
			case 34: return TString(readString(34));
//			case 63: return TQuestion;
//			case 58: return TDoubleDot;
			case '='.code:
				char = readChar();
				if( char == '='.code )
					return TOp("==");
				else if ( char == '>'.code )
					return TOp("=>");
				this.char = char;
				return TOp("=");
			default:
				if( ops[char] ) {
					var op = String.fromCharCode(char);
					var prev = -1;
					while( true ) {
						char = readChar();
						if( !ops[char] || prev == '='.code ) {
							if( op.charCodeAt(0) == '/'.code )
								return tokenComment(op,char);
							this.char = char;
							return TOp(op);
						}
						prev = char;
						op += String.fromCharCode(char);
					}
				}
				if( idents[char] ) {
					var id = String.fromCharCode(char);
					while( true ) {
						char = readChar();
						if( !idents[char] ) {
							this.char = char;
							return TId(id);
						}
						id += String.fromCharCode(char);
					}
				}
				invalidChar(char);
			}
			char = readChar();
		}
		return null;
	}

	function tokenComment( op : String, char : Int ) {
		var c = op.charCodeAt(1);
		var s = input;
		if( c == '/'.code ) { // comment
			try {
				while( char != '\r'.code && char != '\n'.code ) {
					pos++;
					char = s.readByte();
				}
				this.char = char;
			} catch( e : Dynamic ) {
			}
			return token();
		}
		if( c == '*'.code ) { /* comment */
			var old = line;
			if( op == "/**/" ) {
				this.char = char;
				return token();
			}
			try {
				while( true ) {
					while( char != '*'.code ) {
						if( char == '\n'.code ) line++;
						pos++;
						char = s.readByte();
					}
					pos++;
					char = s.readByte();
					if( char == '/'.code )
						break;
				}
			} catch( e : Dynamic ) {
				line = old;
				error("Unterminated comment");
			}
			return token();
		}
		this.char = char;
		return TOp(op);
	}

	function readString( until ) {
		var c = 0;
		var b = new haxe.io.BytesOutput();
		var esc = false;
		var old = line;
		var s = input;
		while( true ) {
			try {
				pos++;
				c = s.readByte();
			} catch( e : Dynamic ) {
				line = old;
				error("Unterminated string");
			}
			if( esc ) {
				esc = false;
				switch( c ) {
				case 'n'.code: b.writeByte(10);
				case 'r'.code: b.writeByte(13);
				case 't'.code: b.writeByte(9);
				case "'".code, '"'.code, '\\'.code: b.writeByte(c);
				case '/'.code: b.writeByte(c);
				default: invalidChar(c);
				}
			} else if( c == 92 )
				esc = true;
			else if( c == until )
				break;
			else {
				if( c == 10 ) line++;
				b.writeByte(c);
			}
		}
		return b.getBytes().toString();
	}

}
