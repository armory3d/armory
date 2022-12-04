package armory.network;

import armory.network.uuid.Uuid;

class Util {
	public static function generateUUID():String {
		return Uuid.v1();
	}
}
