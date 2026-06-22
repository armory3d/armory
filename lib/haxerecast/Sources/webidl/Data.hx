package webidl;

typedef Data = Array<Definition>;

typedef Position = {
	var file : String;
	var line : Int;
	var pos : Int;
}

typedef Definition = {
	var pos : Position;
	var kind : DefinitionKind;
}

enum DefinitionKind {
	DInterface( name : String, attrs : Array<Attrib>, fields : Array<Field> );
	DImplements( type : String, interfaceName : String );
	DEnum( name : String, values : Array<String> );
}

typedef Field = {
	var name : String;
	var kind : FieldKind;
	var pos : Position;
}

enum FieldKind {
	FMethod( args : Array<FArg>, ret : TypeAttr );
	FAttribute( t : TypeAttr );
	DConst( name : String, type : Type, value : String );
}

typedef FArg = { name : String, opt : Bool, t : TypeAttr };
typedef TypeAttr = { var t : Type; var attr : Array<Attrib>; };

enum Type {
	TVoid;
	TInt;
	TShort;
	TFloat;
	TDouble;
	TBool;
	TAny;
	TVoidPtr;
	TCustom( id : String );
	TArray( t : Type );
}

enum Attrib {
	// fields
	AValue;
	ARef;
	AConst;
	AOperator( op : String );
	// interfaces
	ANoDelete;
	APrefix( prefix : String );
	AJSImplementation( name : String );
}
