package armory.trait.internal;

import iron.Trait;
import armory.trait.physics.RigidBody;

#if arm_terrain

class TerrainPhysics extends Trait {

	public function new() {
		super();
		notifyOnInit(init);
	}

	function init() {
		var stream = iron.Scene.active.terrainStream;
		stream.notifyOnReady(function() {
			for (sector in stream.sectors) {
				// Heightmap to bytes
				var tex = stream.heightTextures[sector.uid];
				var p = tex.getPixels();
				var b = haxe.io.Bytes.alloc(tex.width * tex.height);
				for (i in 0...b.length) b.set(i, p.get(i * 4));

				// Shape.Terrain, mass
				var rb = new RigidBody(7, 0);
				rb.heightData = b;
				sector.addTrait(rb);
			}
		});
	}
}

#end
