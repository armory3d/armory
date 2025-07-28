package iron.object;

#if arm_gpu_particles
typedef ParticleSystem = iron.object.GPUParticleSystem;
#elseif arm_cpu_particles
typedef ParticleSystem = iron.object.CPUParticleSystem;
#else
class ParticleSystem { public function new() { } }
#end