package armory.network;

import haxe.io.Bytes;

class Utf8Encoder {
	static public function encode(str:String):Bytes {
		// @TODO: Proper utf8 encoding!
		return Bytes.ofString(str);
	}

	static public function decode(data:Bytes):String {
		// @TODO: Proper utf8 decoding!
		return data.toString();
	}
}
