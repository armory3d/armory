package iron.data;

import iron.data.SceneFormat;

class CameraData {

	public var name: String;
	public var raw: TCameraData;

	public function new(raw: TCameraData, done: CameraData->Void) {
		this.raw = raw;
		this.name = raw.name;
		done(this);
	}

	public static function parse(name: String, id: String, done: CameraData->Void) {
		Data.getSceneRaw(name, function(format: TSceneFormat) {
			var raw: TCameraData = Data.getCameraRawByName(format.camera_datas, id);
			if (raw == null) {
				trace('Camera data "$id" not found!');
				done(null);
			}
			new CameraData(raw, done);
		});
	}
}
