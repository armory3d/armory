package armory.network;

import haxe.io.Bytes;

#if js
typedef BinaryType = js.html.BinaryType;
#else

@:enum abstract BinaryType(String) {
	var ARRAYBUFFER = "arraybuffer";

	@:to public function toString() {
		return this;
	}
}

#end

enum MessageType {
	BytesMessage(content: Buffer);
	StrMessage(content: String);
}
