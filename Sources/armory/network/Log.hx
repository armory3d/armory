package armory.network;

class Log {
	public static inline var INFO:Int =  0x000001;
	public static inline var DEBUG:Int = 0x000010;
	public static inline var DATA:Int =  0x000100;

	public static var mask:Int = 0;

	#if sys
	public static var logFn:Dynamic->Void = Sys.println;
	#elseif js
	public static var logFn:Dynamic->Void = js.html.Console.log;
	#end

	public static function info(data:String, id:String = null) {
		if (mask & INFO != INFO) {
			return;
		}

		if (id != null) {
			logFn('INFO  :: ID-${id} :: ${data}');
		} else {
			logFn('INFO  :: ${data}');
		}
	}

	public static function debug(data:String, id:String = null) {
		if (mask & DEBUG != DEBUG) {
			return;
		}

		if (id != null) {
			logFn('DEBUG :: ID-${id} :: ${data}');
		} else {
			logFn('DEBUG :: ${data}');
		}
	}

	public static function data(data:String, id:String = null) {
		if (mask & DATA != DATA) {
			return;
		}

		if (id != null) {
			logFn('DATA  :: ID-${id}\n------------------------------\n${data}\n------------------------------');
		} else {
			logFn('${data}');
		}
	}
}
