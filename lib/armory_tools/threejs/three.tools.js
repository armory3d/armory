var THREE = require("./three.min");

// BufferGeometryUtils.js
/**
 * @author spite / http://www.clicktorelease.com/
 * @author mrdoob / http://mrdoob.com/
 */

THREE.BufferGeometryUtils = {

	fromGeometry: function geometryToBufferGeometry( geometry, settings ) {

		if ( geometry instanceof THREE.BufferGeometry ) {

			return geometry;

		}

		settings = settings || { 'vertexColors': THREE.NoColors };

		var vertices = geometry.vertices;
		var faces = geometry.faces;
		var faceVertexUvs = geometry.faceVertexUvs;
		var vertexColors = settings.vertexColors;
		var hasFaceVertexUv = faceVertexUvs[ 0 ].length > 0;
		var hasFaceVertexNormals = faces[ 0 ].vertexNormals.length == 3;

		var bufferGeometry = new THREE.BufferGeometry();

		bufferGeometry.attributes = {

			position: {
				itemSize: 3,
				array: new Float32Array( faces.length * 3 * 3 )
			},
			normal: {
				itemSize: 3,
				array: new Float32Array( faces.length * 3 * 3 )
			}

		}

		var positions = bufferGeometry.attributes.position.array;
		var normals = bufferGeometry.attributes.normal.array;

		if ( vertexColors !== THREE.NoColors ) {

			bufferGeometry.attributes.color = {
				itemSize: 3,
				array: new Float32Array( faces.length * 3 * 3 )
			};

			var colors = bufferGeometry.attributes.color.array;

		}

		if ( hasFaceVertexUv === true ) {

			bufferGeometry.attributes.uv = {
				itemSize: 2,
				array: new Float32Array( faces.length * 3 * 2 )
			};

			var uvs = bufferGeometry.attributes.uv.array;

		}

		for ( var i = 0, i2 = 0, i3 = 0; i < faces.length; i ++, i2 += 6, i3 += 9 ) {

			var face = faces[ i ];

			var a = vertices[ face.a ];
			var b = vertices[ face.b ];
			var c = vertices[ face.c ];

			positions[ i3     ] = a.x;
			positions[ i3 + 1 ] = a.y;
			positions[ i3 + 2 ] = a.z;
			
			positions[ i3 + 3 ] = b.x;
			positions[ i3 + 4 ] = b.y;
			positions[ i3 + 5 ] = b.z;
			
			positions[ i3 + 6 ] = c.x;
			positions[ i3 + 7 ] = c.y;
			positions[ i3 + 8 ] = c.z;

			if ( hasFaceVertexNormals === true ) {

				var na = face.vertexNormals[ 0 ];
				var nb = face.vertexNormals[ 1 ];
				var nc = face.vertexNormals[ 2 ];

				normals[ i3     ] = na.x;
				normals[ i3 + 1 ] = na.y;
				normals[ i3 + 2 ] = na.z;

				normals[ i3 + 3 ] = nb.x;
				normals[ i3 + 4 ] = nb.y;
				normals[ i3 + 5 ] = nb.z;

				normals[ i3 + 6 ] = nc.x;
				normals[ i3 + 7 ] = nc.y;
				normals[ i3 + 8 ] = nc.z;

			} else {

				var n = face.normal;

				normals[ i3     ] = n.x;
				normals[ i3 + 1 ] = n.y;
				normals[ i3 + 2 ] = n.z;

				normals[ i3 + 3 ] = n.x;
				normals[ i3 + 4 ] = n.y;
				normals[ i3 + 5 ] = n.z;

				normals[ i3 + 6 ] = n.x;
				normals[ i3 + 7 ] = n.y;
				normals[ i3 + 8 ] = n.z;

			}

			if ( vertexColors === THREE.FaceColors ) {

				var fc = face.color;

				colors[ i3     ] = fc.r;
				colors[ i3 + 1 ] = fc.g;
				colors[ i3 + 2 ] = fc.b;

				colors[ i3 + 3 ] = fc.r;
				colors[ i3 + 4 ] = fc.g;
				colors[ i3 + 5 ] = fc.b;

				colors[ i3 + 6 ] = fc.r;
				colors[ i3 + 7 ] = fc.g;
				colors[ i3 + 8 ] = fc.b;

			} else if ( vertexColors === THREE.VertexColors ) {

				var vca = face.vertexColors[ 0 ];
				var vcb = face.vertexColors[ 1 ];
				var vcc = face.vertexColors[ 2 ];

				colors[ i3     ] = vca.r;
				colors[ i3 + 1 ] = vca.g;
				colors[ i3 + 2 ] = vca.b;

				colors[ i3 + 3 ] = vcb.r;
				colors[ i3 + 4 ] = vcb.g;
				colors[ i3 + 5 ] = vcb.b;

				colors[ i3 + 6 ] = vcc.r;
				colors[ i3 + 7 ] = vcc.g;
				colors[ i3 + 8 ] = vcc.b;

			}

			if ( hasFaceVertexUv === true ) {

				var uva = faceVertexUvs[ 0 ][ i ][ 0 ];
				var uvb = faceVertexUvs[ 0 ][ i ][ 1 ];
				var uvc = faceVertexUvs[ 0 ][ i ][ 2 ];

				uvs[ i2     ] = uva.x;
				uvs[ i2 + 1 ] = uva.y;
			
				uvs[ i2 + 2 ] = uvb.x;
				uvs[ i2 + 3 ] = uvb.y;
			
				uvs[ i2 + 4 ] = uvc.x;
				uvs[ i2 + 5 ] = uvc.y;

			}

		}

		bufferGeometry.computeBoundingSphere();

		return bufferGeometry;

	}

}

// ConvexGeometry.js
// @author qiao / https://github.com/qiao

THREE.ConvexGeometry = function( vertices ) {

	THREE.Geometry.call( this );

	var faces = [ [ 0, 1, 2 ], [ 0, 2, 1 ] ]; 

	for ( var i = 3; i < vertices.length; i++ ) {

		addPoint( i );

	}


	function addPoint( vertexId ) {

		var vertex = vertices[ vertexId ].clone();

		var mag = vertex.length();
		vertex.x += mag * randomOffset();
		vertex.y += mag * randomOffset();
		vertex.z += mag * randomOffset();

		var hole = [];

		for ( var f = 0; f < faces.length; ) {

			var face = faces[ f ];

			// for each face, if the vertex can see it,
			// then we try to add the face's edges into the hole.
			if ( visible( face, vertex ) ) {

				for ( var e = 0; e < 3; e++ ) {

					var edge = [ face[ e ], face[ ( e + 1 ) % 3 ] ];
					var boundary = true;

					// remove duplicated edges.
					for ( var h = 0; h < hole.length; h++ ) {

						if ( equalEdge( hole[ h ], edge ) ) {

							hole[ h ] = hole[ hole.length - 1 ];
							hole.pop();
							boundary = false;
							break;

						}

					}

					if ( boundary ) {

						hole.push( edge );

					}

				}

				// remove faces[ f ]
				faces[ f ] = faces[ faces.length - 1 ];
				faces.pop();

			} else { // not visible

				f++;

			}
		}

		// construct the new faces formed by the edges of the hole and the vertex
		for ( var h = 0; h < hole.length; h++ ) {

			faces.push( [ 
				hole[ h ][ 0 ],
				hole[ h ][ 1 ],
				vertexId
			] );

		}
	}

	/**
	 * Whether the face is visible from the vertex
	 */
	function visible( face, vertex ) {

		var va = vertices[ face[ 0 ] ];
		var vb = vertices[ face[ 1 ] ];
		var vc = vertices[ face[ 2 ] ];

		var n = normal( va, vb, vc );

		// distance from face to origin
		var dist = n.dot( va );

		return n.dot( vertex ) >= dist; 

	}

	/**
	 * Face normal
	 */
	function normal( va, vb, vc ) {

		var cb = new THREE.Vector3();
		var ab = new THREE.Vector3();

		cb.subVectors( vc, vb );
		ab.subVectors( va, vb );
		cb.cross( ab );

		cb.normalize();

		return cb;

	}

	/**
	 * Detect whether two edges are equal.
	 * Note that when constructing the convex hull, two same edges can only
	 * be of the negative direction.
	 */
	function equalEdge( ea, eb ) {

		return ea[ 0 ] === eb[ 1 ] && ea[ 1 ] === eb[ 0 ]; 

	}

	/**
	 * Create a random offset between -1e-6 and 1e-6.
	 */
	function randomOffset() {

		return ( Math.random() - 0.5 ) * 2 * 1e-6;

	}


	/**
	 * XXX: Not sure if this is the correct approach. Need someone to review.
	 */
	function vertexUv( vertex ) {

		var mag = vertex.length();
		return new THREE.Vector2( vertex.x / mag, vertex.y / mag );

	}

	// Push vertices into `this.vertices`, skipping those inside the hull
	var id = 0;
	var newId = new Array( vertices.length ); // map from old vertex id to new id

	for ( var i = 0; i < faces.length; i++ ) {

		 var face = faces[ i ];

		 for ( var j = 0; j < 3; j++ ) {

				if ( newId[ face[ j ] ] === undefined ) {

						newId[ face[ j ] ] = id++;
						this.vertices.push( vertices[ face[ j ] ] );

				}

				face[ j ] = newId[ face[ j ] ];

		 }

	}

	// Convert faces into instances of THREE.Face3
	for ( var i = 0; i < faces.length; i++ ) {

		this.faces.push( new THREE.Face3( 
				faces[ i ][ 0 ],
				faces[ i ][ 1 ],
				faces[ i ][ 2 ]
		) );

	}

	// Compute UVs
	for ( var i = 0; i < this.faces.length; i++ ) {

		var face = this.faces[ i ];

		this.faceVertexUvs[ 0 ].push( [
			vertexUv( this.vertices[ face.a ] ),
			vertexUv( this.vertices[ face.b ] ),
			vertexUv( this.vertices[ face.c ])
		] );

	}

	this.computeFaceNormals();
	this.computeVertexNormals();

};

THREE.ConvexGeometry.prototype = Object.create( THREE.Geometry.prototype );

// SceneUtils.js
/**
 * @author alteredq / http://alteredqualia.com/
 */

THREE.SceneUtils = {

	createMultiMaterialObject: function ( geometry, materials ) {

		var group = new THREE.Group();

		for ( var i = 0, l = materials.length; i < l; i ++ ) {

			group.add( new THREE.Mesh( geometry, materials[ i ] ) );

		}

		return group;

	},

	detach: function ( child, parent, scene ) {

		console.warn( 'THREE.SceneUtils: detach() has been deprecated. Use scene.attach( child ) instead.' );

		scene.attach( child );

	},

	attach: function ( child, scene, parent ) {

		console.warn( 'THREE.SceneUtils: attach() has been deprecated. Use parent.attach( child ) instead.' );

		parent.attach( child );

	}

};

module.exports = THREE
