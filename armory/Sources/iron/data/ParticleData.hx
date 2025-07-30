package iron.data;

import iron.data.SceneFormat;

class ParticleData {

	public var name: String;
	public var raw: TParticleData;

	public function new(raw: TParticleData, done: ParticleData->Void) {
		this.raw = raw;
		this.name = raw.name;

		done(this);
	}

	public static function parse(name: String, id: String, done: ParticleData->Void) {
		Data.getSceneRaw(name, function(format: TSceneFormat) {
			var raw: TParticleData = Data.getParticleRawByName(format.particle_datas, id);
			if (raw == null) {
				trace('Particle data "$id" not found!');
				done(null);
			}
			new ParticleData(raw, done);
		});
	}
}
