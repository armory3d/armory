
const int maxLights = 16;
const int maxLightsCluster = 8;
const float clusterNear = 3.0;
const vec3 clusterSlices = vec3(16, 16, 16);

int getClusterI(vec2 tc, float depthl, vec2 cameraPlane) {
	int sliceZ = 0;
	if (depthl >= clusterNear) {
		float z = log(depthl - clusterNear + 1.0) / log(cameraPlane.y - clusterNear + 1.0);
		sliceZ = int(z * (clusterSlices.z - 1)) + 1;
	}
	return int(tc.x * clusterSlices.x) +
		   int(int(tc.y * clusterSlices.y) * clusterSlices.x) +
		   int(sliceZ * clusterSlices.x * clusterSlices.y);
}
