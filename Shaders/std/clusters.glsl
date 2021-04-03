
const vec3 clusterSlices = vec3(16, 16, 16);

int getClusterI(vec2 tc, float viewz, vec2 cameraPlane) {
	int sliceZ = 0;
	float cnear = clusterNear + cameraPlane.x;
	if (viewz >= cnear) {
		float z = log(viewz - cnear + 1.0) / log(cameraPlane.y - cnear + 1.0);
		sliceZ = int(z * (clusterSlices.z - 1)) + 1;
	}
	// address gap between near plane and cluster near offset
	else if (viewz >= cameraPlane.x) {
		sliceZ = 1;
	}
	return int(tc.x * clusterSlices.x) +
		   int(int(tc.y * clusterSlices.y) * clusterSlices.x) +
		   int(sliceZ * clusterSlices.x * clusterSlices.y);
}
