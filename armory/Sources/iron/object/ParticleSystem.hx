package iron.object;

#if arm_particles
import kha.FastFloat;
import iron.data.ParticleData;

/**
	A particle system of a `MeshObject`, simulated on the CPU
	(`ParticleSystemCPU`) or the GPU (`ParticleSystemGPU`) as set per
	particle system in Blender.
**/
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
