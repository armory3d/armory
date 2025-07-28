package iron.object;

#if arm_gpu_particles
typedef ParticleSystem = ParticleSystemGPU;
#elseif arm_cpu_particles
typedef ParticleSystem = ParticleSystemCPU;
#else
class ParticleSystem { public function new() { } }
#end