const fs = require('fs');
const Recast = require("../haxerecast/recastjs/recast");

// Get mesh path and NavMesh config
const recast_settings = process.argv[3];
const path_mesh = './' + process.argv[2] + '.obj'

// Read OBJ file and build NavMesh
readObjFile(path_mesh, (error, vertices, vertexLength, indices, indexLength) => {
	if (error) {
		console.error('Error:', error);
	} else {
		buildNavMesh(vertices, vertexLength, indices, indexLength);
	}
});

// Parse OBJ file
function readObjFile(objFilePath, callback) {
  try {
	// Read the OBJ file
	const objFileContent = fs.readFileSync(objFilePath, 'utf-8');

	// Process the OBJ content
	const vertices = [];
	const indices = [];

	vertices.length

	const lines = objFileContent.split('\n');
	lines.forEach((line) => {
	  const parts = line.trim().split(/\s+/);

	  if (parts[0] === 'v') {
		// Vertex data
		const x = parseFloat(parts[1]);
		const y = parseFloat(parts[2]);
		const z = parseFloat(parts[3]);
		vertices.push(x, y, z);
	  } else if (parts[0] === 'f') {
		// Face data
		const faceIndices = parts.slice(1).map((vertex) => parseInt(vertex.split('/')[0]) - 1);
		indices.push(...faceIndices);
	  }
	});

	// Call the callback with the result
	callback(null, vertices, vertices.length, indices, indices.length);
  } catch (error) {
	callback(error);
  }
}

function buildNavMesh (vertices, vertexLength, indices, indexLength) {
	
	recastSettings = JSON.parse(recast_settings);

	Recast().then(function(Recast) {

		// Copy recast config settings
		var recastConfig = new Recast.rcConfig();
		recastConfig.width = recastSettings.width;
		recastConfig.height = recastSettings.height;
		if(recastSettings.tiledMesh) {
			recastConfig.tileSize = recastSettings.tileSize;
		}
		else {
			recastConfig.tileSize = 0;
		}
		recastConfig.borderSize = recastSettings.borderSize;
		recastConfig.cs = recastSettings.cellSize;
		recastConfig.ch = recastSettings.cellHeight;
		recastConfig.walkableSlopeAngle = recastSettings.walkableSlopeAngle;
		recastConfig.walkableHeight = recastSettings.walkableHeight;
		recastConfig.walkableClimb = recastSettings.walkableClimb;
		recastConfig.walkableRadius = recastSettings.walkableRadius;
		recastConfig.maxEdgeLen = recastSettings.maxEdgeLen;
		recastConfig.maxSimplificationError = recastSettings.maxSimplificationError;
		recastConfig.minRegionArea = recastSettings.minRegionArea;
		recastConfig.mergeRegionArea = recastSettings.mergeRegionArea;
		recastConfig.maxVertsPerPoly = recastSettings.maxVertsPerPoly;
		recastConfig.detailSampleDist = recastSettings.detailSampleDist;
		recastConfig.detailSampleMaxError = recastSettings.detailSampleMaxError;

		// Init NavMesh
		var navNesh = new Recast.NavMesh();
		// Build NavMesh
		navNesh.build(vertices, vertexLength, indices, indexLength, recastConfig);
		// Create debug NavMesh for visualization
		var debugNavMesh = navNesh.getDebugNavMesh();

		var trianglesCount = debugNavMesh.getTriangleCount();
		triangelVertices = []
		triangleFaces = []
		// Loop through triangles
		for(let runTriangle = 0; runTriangle < trianglesCount; runTriangle++) {
			var triangle = debugNavMesh.getTriangle(runTriangle);
			// Get triangle vertices
			var points = [triangle.getPoint(0),
						 triangle.getPoint(1),
						 triangle.getPoint(2)];

			// Get vertex positon
			for(var i in points) {
				// y, z interchanged
				triangelVertices.push([points[i].x, points[i].z, points[i].y]);
			}
			// Get triangle indices
			var face = [3 * runTriangle + 1, 
						3 * runTriangle + 2, 
						3 * runTriangle + 3];

			
			triangleFaces.push(face);
		}

		// Get OBJ format of triangles
		var navMeshObj = saveGeometryToObj(triangelVertices, triangleFaces);

		// Write to OBJ file
		fs.writeFile(path_mesh, navMeshObj, function (err) {
			if (err) throw err;
		});

	});
}

function saveGeometryToObj (vertices, faces) {
	var buffer = '';

	//Write Vertices
	for (var i in vertices) buffer += 'v ' + (vertices[i][0]) + ' ' + vertices[i][1] + ' ' + vertices[i][2] + '\n';

	//Write Faces
	for (var i in faces) buffer += 'f ' + (faces[i][0]) + ' ' + faces[i][1] + ' ' + faces[i][2] + '\n';

	return buffer;
}