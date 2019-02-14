package armory.trait.internal;

class LivePatch extends iron.Trait {

#if arm_patch

	static var patchId = 0;

	public function new() {
		super();
		notifyOnUpdate(update);
	}

	function update() {
		kha.Assets.loadBlobFromPath("krom.patch", function(b:kha.Blob) {
			if (b.length == 0) return;
			var lines = b.toString().split('\n');
			var id = Std.parseInt(lines[0]);
			if (id > patchId) {
				patchId = id;
				js.Lib.eval(lines[1]);
			}
		});
	}

#else

	public function new() { super(); }

#end
}
