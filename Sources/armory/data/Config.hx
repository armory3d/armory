package armory.data;

class Config {

	public static var raw:TConfig = null;

	public static function load(done:Void->Void) {
		iron.data.Data.getBlob('config.arm', function(blob:kha.Blob) {
			raw = haxe.Json.parse(blob.toString());
			done();
		});
	}

	public static function save() {
		var path = iron.data.Data.dataPath + 'config.arm';
		var bytes = haxe.io.Bytes.ofString(haxe.Json.stringify(raw));
		#if kha_krom
		Krom.fileSaveBytes(path, bytes.getData());
		#elseif kha_kore
		sys.io.File.saveBytes(path, bytes);
		#end
	}

	// public static function reset() {}
}

typedef TConfig = {
	@:optional var debug_console:Null<Bool>;
	@:optional var window_mode:Null<Int>; // window, fullscreen
	@:optional var window_w:Null<Int>;
	@:optional var window_h:Null<Int>;
	@:optional var window_resizable:Null<Bool>;
	@:optional var window_maximizable:Null<Bool>;
	@:optional var window_minimizable:Null<Bool>;
	@:optional var window_vsync:Null<Bool>;
	@:optional var window_msaa:Null<Int>;
	@:optional var window_scale:Null<Float>;
	@:optional var rp_supersample:Null<Float>;
	@:optional var rp_shadowmap:Null<Int>; // size
	@:optional var rp_ssgi:Null<Bool>;
	@:optional var rp_ssr:Null<Bool>;
	@:optional var rp_bloom:Null<Bool>;
	@:optional var rp_motionblur:Null<Bool>;
	@:optional var rp_gi:Null<Bool>;
}
