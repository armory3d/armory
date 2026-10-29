package iron.object;

#if arm_particles
import kha.FastFloat;
import iron.data.ParticleData;

interface ParticleSystem {
	var data: ParticleData;
	var speed: FastFloat;
	function start(): Void;
	function pause(): Void;
	function resume(): Void;
	function stop(): Void;
	function remove(): Void;
}
#end
