package iron.data;

import iron.data.SceneFormat;

class ProbeData {

#if rp_probes

	public var raw: TProbeData;

	public function new(raw: TProbeData, done: ProbeData->Void) {
		this.raw = raw;
		done(this);
	}

	public static function parse(name: String, id: String, done: ProbeData->Void) {
		Data.getSceneRaw(name, function(format: TSceneFormat) {
			var raw: TProbeData = Data.getProbeRawByName(format.probe_datas, id);
			if (raw == null) {
				trace('Probe data "$id" not found!');
				done(null);
			}
			new ProbeData(raw, done);
		});
	}
#end
}
