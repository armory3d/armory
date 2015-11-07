# =============================================================
# 
#  Open Game Engine Exchange
#  http://opengex.org/
# 
#  Export plugin for Blender
#  by Eric Lengyel
#
#  Version 1.1.2.2
# 
#  Copyright 2015, Terathon Software LLC
# 
#  This software is licensed under the Creative Commons
#  Attribution-ShareAlike 3.0 Unported License:
# 
#  http://creativecommons.org/licenses/by-sa/3.0/deed.en_US
# 
#  Adapted to Lue Rendering Engine
#  http://lue3d.org/
#  by Lubos Lenco
#
# =============================================================


bl_info = {
	"name": "Lue format (.json)",
	"description": "Lue Exporter",
	"author": "Eric Lengyel, adapted by Lubos Lenco",
	"version": (1, 0, 0, 0),
	"location": "File > Import-Export",
	"wiki_url": "http://lue3d.org/",
	"category": "Import-Export"}


import bpy
import math
import json
from bpy_extras.io_utils import ExportHelper


kNodeTypeNode = 0
kNodeTypeBone = 1
kNodeTypeGeometry = 2
kNodeTypeLight = 3
kNodeTypeCamera = 4

kAnimationSampled = 0
kAnimationLinear = 1
kAnimationBezier = 2

kExportEpsilon = 1.0e-6


structIdentifier = ["node", "bone_node", "geometry_node", "light_node", "camera_node"]


subtranslationName = ["xpos", "ypos", "zpos"]
subrotationName = ["xrot", "yrot", "zrot"]
subscaleName = ["xscl", "yscl", "zscl"]
deltaSubtranslationName = ["dxpos", "dypos", "dzpos"]
deltaSubrotationName = ["dxrot", "dyrot", "dzrot"]
deltaSubscaleName = ["dxscl", "dyscl", "dzscl"]
axisName = ["x", "y", "z"]

class ExportVertex:
	__slots__ = ("hash", "vertexIndex", "faceIndex", "position", "normal", "color", "texcoord0", "texcoord1")

	def __init__(self):
		self.color = [1.0, 1.0, 1.0]
		self.texcoord0 = [0.0, 0.0]
		self.texcoord1 = [0.0, 0.0]

	def __eq__(self, v):
		if (self.hash != v.hash):
			return (False)
		if (self.position != v.position):
			return (False)
		if (self.normal != v.normal):
			return (False)
		if (self.color != v.color):
			return (False)
		if (self.texcoord0 != v.texcoord0):
			return (False)
		if (self.texcoord1 != v.texcoord1):
			return (False)
		return (True)

	def Hash(self):
		h = hash(self.position[0])
		h = h * 21737 + hash(self.position[1])
		h = h * 21737 + hash(self.position[2])
		h = h * 21737 + hash(self.normal[0])
		h = h * 21737 + hash(self.normal[1])
		h = h * 21737 + hash(self.normal[2])
		h = h * 21737 + hash(self.color[0])
		h = h * 21737 + hash(self.color[1])
		h = h * 21737 + hash(self.color[2])
		h = h * 21737 + hash(self.texcoord0[0])
		h = h * 21737 + hash(self.texcoord0[1])
		h = h * 21737 + hash(self.texcoord1[0])
		h = h * 21737 + hash(self.texcoord1[1])
		self.hash = h

class Object:
    def to_JSON(self):
        #if bpy.data.worlds[0]['TargetMinimize'] == True:
        #    return json.dumps(self, default=lambda o: o.__dict__, separators=(',',':'))
        #else:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class LueExporter(bpy.types.Operator, ExportHelper):
	"""Export to Lue format"""
	bl_idname = "export_scene.lue"
	bl_label = "Export Lue"
	filename_ext = ".json"

	option_export_selection = bpy.props.BoolProperty(name = "Export Selection Only", description = "Export only selected objects", default = False)
	option_sample_animation = bpy.props.BoolProperty(name = "Force Sampled Animation", description = "Always export animation as per-frame samples", default = False)

	def WriteColor(self, color):
		return [color[0], color[1], color[2]]

	def WriteMatrix(self, matrix):
		return [matrix[0][0], matrix[1][0], matrix[2][0], matrix[3][0],
		 	 	matrix[0][1], matrix[1][1], matrix[2][1], matrix[3][1],
		 	 	matrix[0][2], matrix[1][2], matrix[2][2], matrix[3][2],
		 	 	matrix[0][3], matrix[1][3], matrix[2][3], matrix[3][3]]

	def WriteMatrixFlat(self, matrix):
		return [matrix[0][0], matrix[1][0], matrix[2][0], matrix[3][0],
		 	 	matrix[0][1], matrix[1][1], matrix[2][1], matrix[3][1],
		 	 	matrix[0][2], matrix[1][2], matrix[2][2], matrix[3][2],
		 	 	matrix[0][3], matrix[1][3], matrix[2][3], matrix[3][3]]

	def WriteVector2D(self, vector):
		return [vector[0], vector[1]]

	def WriteVector3D(self, vector):
		return [vector[0], vector[1], vector[2]]

	def WriteVertexArray2D(self, vertexArray, attrib):
		va = []
		count = len(vertexArray)
		k = 0

		lineCount = count >> 3
		for i in range(lineCount):
			for j in range(7):
				va += self.WriteVector2D(getattr(vertexArray[k], attrib))
				k += 1

			va += self.WriteVector2D(getattr(vertexArray[k], attrib))
			k += 1

		count &= 7
		if (count != 0):
			for j in range(count - 1):
				va += self.WriteVector2D(getattr(vertexArray[k], attrib))
				k += 1

			va += self.WriteVector2D(getattr(vertexArray[k], attrib))

		return va

	def WriteVertexArray3D(self, vertexArray, attrib):
		va = []
		count = len(vertexArray)
		k = 0

		lineCount = count >> 3
		for i in range(lineCount):

			for j in range(7):
				va += self.WriteVector3D(getattr(vertexArray[k], attrib))
				k += 1

			va += self.WriteVector3D(getattr(vertexArray[k], attrib))
			k += 1

		count &= 7
		if (count != 0):
			for j in range(count - 1):
				va += self.WriteVector3D(getattr(vertexArray[k], attrib))
				k += 1

			va += self.WriteVector3D(getattr(vertexArray[k], attrib))

		return va

	def WriteInt(self, i):
		return i

	def WriteFloat(self, f):
		return f

	def WriteTriangle(self, triangleIndex, indexTable):
		i = triangleIndex * 3
		return [indexTable[i], indexTable[i + 1], indexTable[i + 2]]


	def WriteTriangleArray(self, count, indexTable):
		va = []
		triangleIndex = 0

		lineCount = count >> 4
		for i in range(lineCount):

			for j in range(15):
				va += self.WriteTriangle(triangleIndex, indexTable)
				triangleIndex += 1

			va += self.WriteTriangle(triangleIndex, indexTable)
			triangleIndex += 1

		count &= 15
		if (count != 0):

			for j in range(count - 1):
				va += self.WriteTriangle(triangleIndex, indexTable)
				triangleIndex += 1

			va += self.WriteTriangle(triangleIndex, indexTable)

		return va





	@staticmethod
	def GetNodeType(node):
		if (node.type == "MESH"):
			if (len(node.data.polygons) != 0):
				return (kNodeTypeGeometry)
		elif (node.type == "LAMP"):
			type = node.data.type
			if ((type == "SUN") or (type == "POINT") or (type == "SPOT")):
				return (kNodeTypeLight)
		elif (node.type == "CAMERA"):
			return (kNodeTypeCamera)

		return (kNodeTypeNode)

	@staticmethod
	def GetShapeKeys(mesh):
		shapeKeys = mesh.shape_keys
		if ((shapeKeys) and (len(shapeKeys.key_blocks) > 1)):
			return (shapeKeys)

		return (None)

	def FindNode(self, name):
		for nodeRef in self.nodeArray.items():
			if (nodeRef[0].name == name):
				return (nodeRef)
		return (None)

	@staticmethod
	def ClassifyAnimationCurve(fcurve):
		linearCount = 0
		bezierCount = 0

		for key in fcurve.keyframe_points:
			interp = key.interpolation
			if (interp == "LINEAR"):
				linearCount += 1
			elif (interp == "BEZIER"):
				bezierCount += 1
			else:
				return (kAnimationSampled)

		if (bezierCount == 0):
			return (kAnimationLinear)
		elif (linearCount == 0):
			return (kAnimationBezier)
			
		return (kAnimationSampled)

	@staticmethod
	def AnimationKeysDifferent(fcurve):
		keyCount = len(fcurve.keyframe_points)
		if (keyCount > 0):
			key1 = fcurve.keyframe_points[0].co[1]

			for i in range(1, keyCount):
				key2 = fcurve.keyframe_points[i].co[1]
				if (math.fabs(key2 - key1) > kExportEpsilon):
					return (True)

		return (False)


	@staticmethod
	def AnimationTangentsNonzero(fcurve):
		keyCount = len(fcurve.keyframe_points)
		if (keyCount > 0):
			key = fcurve.keyframe_points[0].co[1]
			left = fcurve.keyframe_points[0].handle_left[1]
			right = fcurve.keyframe_points[0].handle_right[1]
			if ((math.fabs(key - left) > kExportEpsilon) or (math.fabs(right - key) > kExportEpsilon)):
				return (True)

			for i in range(1, keyCount):
				key = fcurve.keyframe_points[i].co[1]
				left = fcurve.keyframe_points[i].handle_left[1]
				right = fcurve.keyframe_points[i].handle_right[1]
				if ((math.fabs(key - left) > kExportEpsilon) or (math.fabs(right - key) > kExportEpsilon)):
					return (True)

		return (False)

	@staticmethod
	def MatricesDifferent(m1, m2):
		for i in range(4):
			for j in range(4):
				if (math.fabs(m1[i][j] - m2[i][j]) > kExportEpsilon):
					return (True)

		return (False)

	@staticmethod
	def CollectBoneAnimation(armature, name):
		path = "pose.bones[\"" + name + "\"]."
		curveArray = []

		if (armature.animation_data):
			action = armature.animation_data.action
			if (action):
				for fcurve in action.fcurves:
					if (fcurve.data_path.startswith(path)):
						curveArray.append(fcurve)

		return (curveArray)

	@staticmethod
	def AnimationPresent(fcurve, kind):
		if (kind != kAnimationBezier):
			return (LueExporter.AnimationKeysDifferent(fcurve))

		return ((LueExporter.AnimationKeysDifferent(fcurve)) or (LueExporter.AnimationTangentsNonzero(fcurve)))


	@staticmethod
	def DeindexMesh(mesh, materialTable):

		# This function deindexes all vertex positions, colors, and texcoords.
		# Three separate ExportVertex structures are created for each triangle.

		vertexArray = mesh.vertices
		exportVertexArray = []
		faceIndex = 0

		for face in mesh.tessfaces:
			k1 = face.vertices[0]
			k2 = face.vertices[1]
			k3 = face.vertices[2]

			v1 = vertexArray[k1]
			v2 = vertexArray[k2]
			v3 = vertexArray[k3]

			exportVertex = ExportVertex()
			exportVertex.vertexIndex = k1
			exportVertex.faceIndex = faceIndex
			exportVertex.position = v1.co
			exportVertex.normal = v1.normal if (face.use_smooth) else face.normal
			exportVertexArray.append(exportVertex)

			exportVertex = ExportVertex()
			exportVertex.vertexIndex = k2
			exportVertex.faceIndex = faceIndex
			exportVertex.position = v2.co
			exportVertex.normal = v2.normal if (face.use_smooth) else face.normal
			exportVertexArray.append(exportVertex)

			exportVertex = ExportVertex()
			exportVertex.vertexIndex = k3
			exportVertex.faceIndex = faceIndex
			exportVertex.position = v3.co
			exportVertex.normal = v3.normal if (face.use_smooth) else face.normal
			exportVertexArray.append(exportVertex)

			materialTable.append(face.material_index)

			if (len(face.vertices) == 4):
				k1 = face.vertices[0]
				k2 = face.vertices[2]
				k3 = face.vertices[3]

				v1 = vertexArray[k1]
				v2 = vertexArray[k2]
				v3 = vertexArray[k3]

				exportVertex = ExportVertex()
				exportVertex.vertexIndex = k1
				exportVertex.faceIndex = faceIndex
				exportVertex.position = v1.co
				exportVertex.normal = v1.normal if (face.use_smooth) else face.normal
				exportVertexArray.append(exportVertex)

				exportVertex = ExportVertex()
				exportVertex.vertexIndex = k2
				exportVertex.faceIndex = faceIndex
				exportVertex.position = v2.co
				exportVertex.normal = v2.normal if (face.use_smooth) else face.normal
				exportVertexArray.append(exportVertex)

				exportVertex = ExportVertex()
				exportVertex.vertexIndex = k3
				exportVertex.faceIndex = faceIndex
				exportVertex.position = v3.co
				exportVertex.normal = v3.normal if (face.use_smooth) else face.normal
				exportVertexArray.append(exportVertex)

				materialTable.append(face.material_index)

			faceIndex += 1

		colorCount = len(mesh.tessface_vertex_colors)
		if (colorCount > 0):
			colorFace = mesh.tessface_vertex_colors[0].data
			vertexIndex = 0
			faceIndex = 0

			for face in mesh.tessfaces:
				cf = colorFace[faceIndex]
				exportVertexArray[vertexIndex].color = cf.color1
				vertexIndex += 1
				exportVertexArray[vertexIndex].color = cf.color2
				vertexIndex += 1
				exportVertexArray[vertexIndex].color = cf.color3
				vertexIndex += 1

				if (len(face.vertices) == 4):
					exportVertexArray[vertexIndex].color = cf.color1
					vertexIndex += 1
					exportVertexArray[vertexIndex].color = cf.color3
					vertexIndex += 1
					exportVertexArray[vertexIndex].color = cf.color4
					vertexIndex += 1

				faceIndex += 1

		texcoordCount = len(mesh.tessface_uv_textures)
		if (texcoordCount > 0):
			texcoordFace = mesh.tessface_uv_textures[0].data
			vertexIndex = 0
			faceIndex = 0

			for face in mesh.tessfaces:
				tf = texcoordFace[faceIndex]
				exportVertexArray[vertexIndex].texcoord0 = tf.uv1
				vertexIndex += 1
				exportVertexArray[vertexIndex].texcoord0 = tf.uv2
				vertexIndex += 1
				exportVertexArray[vertexIndex].texcoord0 = tf.uv3
				vertexIndex += 1

				if (len(face.vertices) == 4):
					exportVertexArray[vertexIndex].texcoord0 = tf.uv1
					vertexIndex += 1
					exportVertexArray[vertexIndex].texcoord0 = tf.uv3
					vertexIndex += 1
					exportVertexArray[vertexIndex].texcoord0 = tf.uv4
					vertexIndex += 1

				faceIndex += 1

			if (texcoordCount > 1):
				texcoordFace = mesh.tessface_uv_textures[1].data
				vertexIndex = 0
				faceIndex = 0

				for face in mesh.tessfaces:
					tf = texcoordFace[faceIndex]
					exportVertexArray[vertexIndex].texcoord1 = tf.uv1
					vertexIndex += 1
					exportVertexArray[vertexIndex].texcoord1 = tf.uv2
					vertexIndex += 1
					exportVertexArray[vertexIndex].texcoord1 = tf.uv3
					vertexIndex += 1

					if (len(face.vertices) == 4):
						exportVertexArray[vertexIndex].texcoord1 = tf.uv1
						vertexIndex += 1
						exportVertexArray[vertexIndex].texcoord1 = tf.uv3
						vertexIndex += 1
						exportVertexArray[vertexIndex].texcoord1 = tf.uv4
						vertexIndex += 1

					faceIndex += 1

		for ev in exportVertexArray:
			ev.Hash()

		return (exportVertexArray)

	@staticmethod
	def FindExportVertex(bucket, exportVertexArray, vertex):
		for index in bucket:
			if (exportVertexArray[index] == vertex):
				return (index)

		return (-1)

	@staticmethod
	def UnifyVertices(exportVertexArray, indexTable):

		# This function looks for identical vertices having exactly the same position, normal,
		# color, and texcoords. Duplicate vertices are unified, and a new index table is returned.

		bucketCount = len(exportVertexArray) >> 3
		if (bucketCount > 1):

			# Round down to nearest power of two.

			while True:
				count = bucketCount & (bucketCount - 1)
				if (count == 0):
					break
				bucketCount = count
		else:
			bucketCount = 1

		hashTable = [[] for i in range(bucketCount)]
		unifiedVertexArray = []

		for i in range(len(exportVertexArray)):
			ev = exportVertexArray[i]
			bucket = ev.hash & (bucketCount - 1)
			index = LueExporter.FindExportVertex(hashTable[bucket], exportVertexArray, ev)
			if (index < 0):
				indexTable.append(len(unifiedVertexArray))
				unifiedVertexArray.append(ev)
				hashTable[bucket].append(i)
			else:
				indexTable.append(indexTable[index])

		return (unifiedVertexArray)







	def ExportBone(self, armature, bone, scene, o):
		nodeRef = self.nodeArray.get(bone)
		
		if (nodeRef):
			o.type = structIdentifier[nodeRef["nodeType"]]
			o.id = nodeRef["structName"]

			#name = bone.name
			#if (name != ""):
			#	o.name = name

			self.ExportBoneTransform(armature, bone, scene, o)

		o.nodes = [] # TODO
		for subnode in bone.children:
			so = Object()
			self.ExportBone(armature, subnode, scene, so)
			o.nodes.append(so)

		# Export any ordinary nodes that are parented to this bone.

		boneSubnodeArray = self.boneParentArray.get(bone.name)
		if (boneSubnodeArray):
			poseBone = None
			if (not bone.use_relative_parent):
				poseBone = armature.pose.bones.get(bone.name)

			for subnode in boneSubnodeArray:
				self.ExportNode(subnode, scene, poseBone, o)
		



	def ExportNodeSampledAnimation(self, node, scene, o):

		# This function exports animation as full 4x4 matrices for each frame.
		
		currentFrame = scene.frame_current
		currentSubframe = scene.frame_subframe

		animationFlag = False
		m1 = node.matrix_local.copy()

		for i in range(self.beginFrame, self.endFrame):
			scene.frame_set(i)
			m2 = node.matrix_local
			if (LueExporter.MatricesDifferent(m1, m2)):
				animationFlag = True
				break

		if (animationFlag):
			o.animation = Object() # TODO: multiple tracks?

			o.animation.track = Object()
			o.animation.track.target = "transform"

			o.animation.track.time = Object()

			o.animation.track.time = Object()
			o.animation.track.time.values = []

			for i in range(self.beginFrame, self.endFrame):
				o.animation.track.time.values.append(self.WriteFloat((i - self.beginFrame) * self.frameTime))

			o.animation.track.time.values.append(self.WriteFloat(self.endFrame * self.frameTime))

			o.animation.track.value = Object()
			o.animation.track.value.values = []

			for i in range(self.beginFrame, self.endFrame):
				scene.frame_set(i)
				o.animation.track.value.values.append(self.WriteMatrixFlat(node.matrix_local))

			scene.frame_set(self.endFrame)
			o.animation.track.value.values.append(self.WriteMatrixFlat(node.matrix_local))

		scene.frame_set(currentFrame, currentSubframe)


	def ExportBoneSampledAnimation(self, poseBone, scene, o):

		# This function exports bone animation as full 4x4 matrices for each frame.

		currentFrame = scene.frame_current
		currentSubframe = scene.frame_subframe

		animationFlag = False
		m1 = poseBone.matrix.copy()

		for i in range(self.beginFrame, self.endFrame):
			scene.frame_set(i)
			m2 = poseBone.matrix
			if (LueExporter.MatricesDifferent(m1, m2)):
				animationFlag = True
				break

		if (animationFlag):
			o.animation = Object()
			o.animation.track = Object()
			o.animation.track.target = "transform"
			o.animation.track.time = Object()
			o.animation.track.time.values = []

			for i in range(self.beginFrame, self.endFrame):
				o.animation.track.time.values.append(self.WriteFloat((i - self.beginFrame) * self.frameTime))

			o.animation.track.time.values.append(self.WriteFloat(self.endFrame * self.frameTime))

			o.animation.track.value = Object()
			o.animation.track.value.values = []

			parent = poseBone.parent
			if (parent):
				for i in range(self.beginFrame, self.endFrame):
					scene.frame_set(i)
					o.animation.track.value.values.append(self.WriteMatrixFlat(parent.matrix.inverted() * poseBone.matrix))

				scene.frame_set(self.endFrame)
				o.animation.track.value.values.append(self.WriteMatrixFlat(parent.matrix.inverted() * poseBone.matrix))

			else:
				for i in range(self.beginFrame, self.endFrame):
					scene.frame_set(i)
					o.animation.track.value.values.append(self.WriteMatrixFlat(poseBone.matrix))

				scene.frame_set(self.endFrame)
				o.animation.track.value.values.append(self.WriteMatrixFlat(poseBone.matrix))

		scene.frame_set(currentFrame, currentSubframe)
		


	def ExportNodeTransform(self, node, scene, o):
		posAnimCurve = [None, None, None]
		rotAnimCurve = [None, None, None]
		sclAnimCurve = [None, None, None]
		posAnimKind = [0, 0, 0]
		rotAnimKind = [0, 0, 0]
		sclAnimKind = [0, 0, 0]

		deltaPosAnimCurve = [None, None, None]
		deltaRotAnimCurve = [None, None, None]
		deltaSclAnimCurve = [None, None, None]
		deltaPosAnimKind = [0, 0, 0]
		deltaRotAnimKind = [0, 0, 0]
		deltaSclAnimKind = [0, 0, 0]

		positionAnimated = False
		rotationAnimated = False
		scaleAnimated = False
		posAnimated = [False, False, False]
		rotAnimated = [False, False, False]
		sclAnimated = [False, False, False]

		deltaPositionAnimated = False
		deltaRotationAnimated = False
		deltaScaleAnimated = False
		deltaPosAnimated = [False, False, False]
		deltaRotAnimated = [False, False, False]
		deltaSclAnimated = [False, False, False]

		mode = node.rotation_mode
		sampledAnimation = ((self.sampleAnimationFlag) or (mode == "QUATERNION") or (mode == "AXIS_ANGLE"))

		if ((not sampledAnimation) and (node.animation_data)):
			action = node.animation_data.action
			if (action):
				for fcurve in action.fcurves:
					kind = LueExporter.ClassifyAnimationCurve(fcurve)
					if (kind != kAnimationSampled):
						if (fcurve.data_path == "location"):
							for i in range(3):
								if ((fcurve.array_index == i) and (not posAnimCurve[i])):
									posAnimCurve[i] = fcurve
									posAnimKind[i] = kind
									if (LueExporter.AnimationPresent(fcurve, kind)):
										posAnimated[i] = True
						elif (fcurve.data_path == "delta_location"):
							for i in range(3):
								if ((fcurve.array_index == i) and (not deltaPosAnimCurve[i])):
									deltaPosAnimCurve[i] = fcurve
									deltaPosAnimKind[i] = kind
									if (LueExporter.AnimationPresent(fcurve, kind)):
										deltaPosAnimated[i] = True
						elif (fcurve.data_path == "rotation_euler"):
							for i in range(3):
								if ((fcurve.array_index == i) and (not rotAnimCurve[i])):
									rotAnimCurve[i] = fcurve
									rotAnimKind[i] = kind
									if (LueExporter.AnimationPresent(fcurve, kind)):
										rotAnimated[i] = True
						elif (fcurve.data_path == "delta_rotation_euler"):
							for i in range(3):
								if ((fcurve.array_index == i) and (not deltaRotAnimCurve[i])):
									deltaRotAnimCurve[i] = fcurve
									deltaRotAnimKind[i] = kind
									if (LueExporter.AnimationPresent(fcurve, kind)):
										deltaRotAnimated[i] = True
						elif (fcurve.data_path == "scale"):
							for i in range(3):
								if ((fcurve.array_index == i) and (not sclAnimCurve[i])):
									sclAnimCurve[i] = fcurve
									sclAnimKind[i] = kind
									if (LueExporter.AnimationPresent(fcurve, kind)):
										sclAnimated[i] = True
						elif (fcurve.data_path == "delta_scale"):
							for i in range(3):
								if ((fcurve.array_index == i) and (not deltaSclAnimCurve[i])):
									deltaSclAnimCurve[i] = fcurve
									deltaSclAnimKind[i] = kind
									if (LueExporter.AnimationPresent(fcurve, kind)):
										deltaSclAnimated[i] = True
						elif ((fcurve.data_path == "rotation_axis_angle") or (fcurve.data_path == "rotation_quaternion") or (fcurve.data_path == "delta_rotation_quaternion")):
							sampledAnimation = True
							break
					else:
						sampledAnimation = True
						break

		positionAnimated = posAnimated[0] | posAnimated[1] | posAnimated[2]
		rotationAnimated = rotAnimated[0] | rotAnimated[1] | rotAnimated[2]
		scaleAnimated = sclAnimated[0] | sclAnimated[1] | sclAnimated[2]

		deltaPositionAnimated = deltaPosAnimated[0] | deltaPosAnimated[1] | deltaPosAnimated[2]
		deltaRotationAnimated = deltaRotAnimated[0] | deltaRotAnimated[1] | deltaRotAnimated[2]
		deltaScaleAnimated = deltaSclAnimated[0] | deltaSclAnimated[1] | deltaSclAnimated[2]

		if ((sampledAnimation) or ((not positionAnimated) and (not rotationAnimated) and (not scaleAnimated) and (not deltaPositionAnimated) and (not deltaRotationAnimated) and (not deltaScaleAnimated))):

			# If there's no keyframe animation at all, then write the node transform as a single 4x4 matrix.
			# We might still be exporting sampled animation below.

			o.transform = Object()

			if (sampledAnimation):
				o.transform.target = "transform"

			o.transform.values = self.WriteMatrix(node.matrix_local)

			if (sampledAnimation):
				self.ExportNodeSampledAnimation(node, scene, o)

		else:
			structFlag = False

			deltaTranslation = node.delta_location
			if (deltaPositionAnimated):

				# When the delta location is animated, write the x, y, and z components separately
				# so they can be targeted by different tracks having different sets of keys.

				for i in range(3):
					pos = deltaTranslation[i]
					if ((deltaPosAnimated[i]) or (math.fabs(pos) > kExportEpsilon)):
						# self.IndentWrite(B"Translation %", 0, structFlag)
						# self.Write(deltaSubtranslationName[i])
						# self.Write(B" (kind = \"")
						# self.Write(axisName[i])
						# self.Write(B"\")\n")
						# self.IndentWrite(B"{\n")
						# self.IndentWrite(B"float {", 1)
						# self.WriteFloat(pos)
						# self.Write(B"}")
						# self.IndentWrite(B"}\n", 0, True)

						structFlag = True

			elif ((math.fabs(deltaTranslation[0]) > kExportEpsilon) or (math.fabs(deltaTranslation[1]) > kExportEpsilon) or (math.fabs(deltaTranslation[2]) > kExportEpsilon)):
				# self.IndentWrite(B"Translation\n")
				# self.IndentWrite(B"{\n")
				# self.IndentWrite(B"float[3] {", 1)
				# self.WriteVector3D(deltaTranslation)
				# self.Write(B"}")
				# self.IndentWrite(B"}\n", 0, True)

				structFlag = True

			translation = node.location
			if (positionAnimated):

				# When the location is animated, write the x, y, and z components separately
				# so they can be targeted by different tracks having different sets of keys.

				for i in range(3):
					pos = translation[i]
					if ((posAnimated[i]) or (math.fabs(pos) > kExportEpsilon)):
						# self.IndentWrite(B"Translation %", 0, structFlag)
						# self.Write(subtranslationName[i])
						# self.Write(B" (kind = \"")
						# self.Write(axisName[i])
						# self.Write(B"\")\n")
						# self.IndentWrite(B"{\n")
						# self.IndentWrite(B"float {", 1)
						# self.WriteFloat(pos)
						# self.Write(B"}")
						# self.IndentWrite(B"}\n", 0, True)

						structFlag = True

			elif ((math.fabs(translation[0]) > kExportEpsilon) or (math.fabs(translation[1]) > kExportEpsilon) or (math.fabs(translation[2]) > kExportEpsilon)):
				# self.IndentWrite(B"Translation\n")
				# self.IndentWrite(B"{\n")
				# self.IndentWrite(B"float[3] {", 1)
				# self.WriteVector3D(translation)
				# self.Write(B"}")
				# self.IndentWrite(B"}\n", 0, True)

				structFlag = True

			if (deltaRotationAnimated):

				# When the delta rotation is animated, write three separate Euler angle rotations
				# so they can be targeted by different tracks having different sets of keys.

				for i in range(3):
					axis = ord(mode[2 - i]) - 0x58
					angle = node.delta_rotation_euler[axis]
					if ((deltaRotAnimated[axis]) or (math.fabs(angle) > kExportEpsilon)):
						# self.IndentWrite(B"Rotation %", 0, structFlag)
						# self.Write(deltaSubrotationName[axis])
						# self.Write(B" (kind = \"")
						# self.Write(axisName[axis])
						# self.Write(B"\")\n")
						# self.IndentWrite(B"{\n")
						# self.IndentWrite(B"float {", 1)
						# self.WriteFloat(angle)
						# self.Write(B"}")
						# self.IndentWrite(B"}\n", 0, True)

						structFlag = True

			else:

				# When the delta rotation is not animated, write it in the representation given by
				# the node's current rotation mode. (There is no axis-angle delta rotation.)

				if (mode == "QUATERNION"):
					quaternion = node.delta_rotation_quaternion
					if ((math.fabs(quaternion[0] - 1.0) > kExportEpsilon) or (math.fabs(quaternion[1]) > kExportEpsilon) or (math.fabs(quaternion[2]) > kExportEpsilon) or (math.fabs(quaternion[3]) > kExportEpsilon)):
						# self.IndentWrite(B"Rotation (kind = \"quaternion\")\n", 0, structFlag)
						# self.IndentWrite(B"{\n")
						# self.IndentWrite(B"float[4] {", 1)
						# self.WriteQuaternion(quaternion)
						# self.Write(B"}")
						# self.IndentWrite(B"}\n", 0, True)

						structFlag = True

				else:
					for i in range(3):
						axis = ord(mode[2 - i]) - 0x58
						angle = node.delta_rotation_euler[axis]
						if (math.fabs(angle) > kExportEpsilon):
							# self.IndentWrite(B"Rotation (kind = \"", 0, structFlag)
							# self.Write(axisName[axis])
							# self.Write(B"\")\n")
							# self.IndentWrite(B"{\n")
							# self.IndentWrite(B"float {", 1)
							# self.WriteFloat(angle)
							# self.Write(B"}")
							# self.IndentWrite(B"}\n", 0, True)

							structFlag = True

			if (rotationAnimated):

				# When the rotation is animated, write three separate Euler angle rotations
				# so they can be targeted by different tracks having different sets of keys.

				for i in range(3):
					axis = ord(mode[2 - i]) - 0x58
					angle = node.rotation_euler[axis]
					if ((rotAnimated[axis]) or (math.fabs(angle) > kExportEpsilon)):
						# self.IndentWrite(B"Rotation %", 0, structFlag)
						# self.Write(subrotationName[axis])
						# self.Write(B" (kind = \"")
						# self.Write(axisName[axis])
						# self.Write(B"\")\n")
						# self.IndentWrite(B"{\n")
						# self.IndentWrite(B"float {", 1)
						# self.WriteFloat(angle)
						# self.Write(B"}")
						# self.IndentWrite(B"}\n", 0, True)

						structFlag = True

			else:

				# When the rotation is not animated, write it in the representation given by
				# the node's current rotation mode.

				if (mode == "QUATERNION"):
					quaternion = node.rotation_quaternion
					if ((math.fabs(quaternion[0] - 1.0) > kExportEpsilon) or (math.fabs(quaternion[1]) > kExportEpsilon) or (math.fabs(quaternion[2]) > kExportEpsilon) or (math.fabs(quaternion[3]) > kExportEpsilon)):
						# self.IndentWrite(B"Rotation (kind = \"quaternion\")\n", 0, structFlag)
						# self.IndentWrite(B"{\n")
						# self.IndentWrite(B"float[4] {", 1)
						# self.WriteQuaternion(quaternion)
						# self.Write(B"}")
						# self.IndentWrite(B"}\n", 0, True)

						structFlag = True

				elif (mode == "AXIS_ANGLE"):
					if (math.fabs(node.rotation_axis_angle[0]) > kExportEpsilon):
						# self.IndentWrite(B"Rotation (kind = \"axis\")\n", 0, structFlag)
						# self.IndentWrite(B"{\n")
						# self.IndentWrite(B"float[4] {", 1)
						# self.WriteVector4D(node.rotation_axis_angle)
						# self.Write(B"}")
						# self.IndentWrite(B"}\n", 0, True)

						structFlag = True

				else:
					for i in range(3):
						axis = ord(mode[2 - i]) - 0x58
						angle = node.rotation_euler[axis]
						if (math.fabs(angle) > kExportEpsilon):
							# self.IndentWrite(B"Rotation (kind = \"", 0, structFlag)
							# self.Write(axisName[axis])
							# self.Write(B"\")\n")
							# self.IndentWrite(B"{\n")
							# self.IndentWrite(B"float {", 1)
							# self.WriteFloat(angle)
							# self.Write(B"}")
							# self.IndentWrite(B"}\n", 0, True)

							structFlag = True

			deltaScale = node.delta_scale
			if (deltaScaleAnimated):

				# When the delta scale is animated, write the x, y, and z components separately
				# so they can be targeted by different tracks having different sets of keys.

				for i in range(3):
					scl = deltaScale[i]
					if ((deltaSclAnimated[i]) or (math.fabs(scl) > kExportEpsilon)):
						# self.IndentWrite(B"Scale %", 0, structFlag)
						# self.Write(deltaSubscaleName[i])
						# self.Write(B" (kind = \"")
						# self.Write(axisName[i])
						# self.Write(B"\")\n")
						# self.IndentWrite(B"{\n")
						# self.IndentWrite(B"float {", 1)
						# self.WriteFloat(scl)
						# self.Write(B"}")
						# self.IndentWrite(B"}\n", 0, True)

						structFlag = True

			elif ((math.fabs(deltaScale[0] - 1.0) > kExportEpsilon) or (math.fabs(deltaScale[1] - 1.0) > kExportEpsilon) or (math.fabs(deltaScale[2] - 1.0) > kExportEpsilon)):
				# self.IndentWrite(B"Scale\n", 0, structFlag)
				# self.IndentWrite(B"{\n")
				# self.IndentWrite(B"float[3] {", 1)
				# self.WriteVector3D(deltaScale)
				# self.Write(B"}")
				# self.IndentWrite(B"}\n", 0, True)

				structFlag = True

			scale = node.scale
			if (scaleAnimated):

				# When the scale is animated, write the x, y, and z components separately
				# so they can be targeted by different tracks having different sets of keys.

				for i in range(3):
					scl = scale[i]
					if ((sclAnimated[i]) or (math.fabs(scl) > kExportEpsilon)):
						# self.IndentWrite(B"Scale %", 0, structFlag)
						# self.Write(subscaleName[i])
						# self.Write(B" (kind = \"")
						# self.Write(axisName[i])
						# self.Write(B"\")\n")
						# self.IndentWrite(B"{\n")
						# self.IndentWrite(B"float {", 1)
						# self.WriteFloat(scl)
						# self.Write(B"}")
						# self.IndentWrite(B"}\n", 0, True)

						structFlag = True

			elif ((math.fabs(scale[0] - 1.0) > kExportEpsilon) or (math.fabs(scale[1] - 1.0) > kExportEpsilon) or (math.fabs(scale[2] - 1.0) > kExportEpsilon)):
				# self.IndentWrite(B"Scale\n", 0, structFlag)
				# self.IndentWrite(B"{\n")
				# self.IndentWrite(B"float[3] {", 1)
				# self.WriteVector3D(scale)
				# self.Write(B"}")
				# self.IndentWrite(B"}\n", 0, True)

				structFlag = True

			# Export the animation tracks.
			
			#o.animation = Object()
			'''
			self.IndentWrite(B"Animation (begin = ", 0, True)
			self.WriteFloat((action.frame_range[0] - self.beginFrame) * self.frameTime)
			self.Write(B", end = ")
			self.WriteFloat((action.frame_range[1] - self.beginFrame) * self.frameTime)
			self.Write(B")\n")
			self.IndentWrite(B"{\n")
			self.indentLevel += 1

			structFlag = False

			if (positionAnimated):
				for i in range(3):
					if (posAnimated[i]):
						self.ExportAnimationTrack(posAnimCurve[i], posAnimKind[i], subtranslationName[i], structFlag)
						structFlag = True

			if (rotationAnimated):
				for i in range(3):
					if (rotAnimated[i]):
						self.ExportAnimationTrack(rotAnimCurve[i], rotAnimKind[i], subrotationName[i], structFlag)
						structFlag = True

			if (scaleAnimated):
				for i in range(3):
					if (sclAnimated[i]):
						self.ExportAnimationTrack(sclAnimCurve[i], sclAnimKind[i], subscaleName[i], structFlag)
						structFlag = True

			if (deltaPositionAnimated):
				for i in range(3):
					if (deltaPosAnimated[i]):
						self.ExportAnimationTrack(deltaPosAnimCurve[i], deltaPosAnimKind[i], deltaSubtranslationName[i], structFlag)
						structFlag = True

			if (deltaRotationAnimated):
				for i in range(3):
					if (deltaRotAnimated[i]):
						self.ExportAnimationTrack(deltaRotAnimCurve[i], deltaRotAnimKind[i], deltaSubrotationName[i], structFlag)
						structFlag = True

			if (deltaScaleAnimated):
				for i in range(3):
					if (deltaSclAnimated[i]):
						self.ExportAnimationTrack(deltaSclAnimCurve[i], deltaSclAnimKind[i], deltaSubscaleName[i], structFlag)
						structFlag = True
			'''



	def ProcessBone(self, bone):
		if ((self.exportAllFlag) or (bone.select)):
			#self.nodeArray[bone] = {"nodeType" : kNodeTypeBone, "structName" : "node" + str(len(self.nodeArray) + 1)}
			self.nodeArray[bone] = {"nodeType" : kNodeTypeBone, "structName" : bone.name}

		for subnode in bone.children:
			self.ProcessBone(subnode)


	def ProcessNode(self, node):
		if ((self.exportAllFlag) or (node.select)):
			type = LueExporter.GetNodeType(node)
			#self.nodeArray[node] = {"nodeType" : type, "structName" : "node" + str(len(self.nodeArray) + 1)}
			self.nodeArray[node] = {"nodeType" : type, "structName" : node.name}

			if (node.parent_type == "BONE"):
				boneSubnodeArray = self.boneParentArray.get(node.parent_bone)
				if (boneSubnodeArray):
					boneSubnodeArray.append(node)
				else:
					self.boneParentArray[node.parent_bone] = [node]

			if (node.type == "ARMATURE"):
				skeleton = node.data
				if (skeleton):
					for bone in skeleton.bones:
						if (not bone.parent):
							self.ProcessBone(bone)

		for subnode in node.children:
			self.ProcessNode(subnode)


	def ProcessSkinnedMeshes(self):
		for nodeRef in self.nodeArray.items():
			if (nodeRef[1]["nodeType"] == kNodeTypeGeometry):
				armature = nodeRef[0].find_armature()
				if (armature):
					for bone in armature.data.bones:
						boneRef = self.FindNode(bone.name)
						if (boneRef):

							# If a node is used as a bone, then we force its type to be a bone.

							boneRef[1]["nodeType"] = kNodeTypeBone



	def ExportBoneTransform(self, armature, bone, scene, o):

		curveArray = self.CollectBoneAnimation(armature, bone.name)
		animation = ((len(curveArray) != 0) or (self.sampleAnimationFlag))

		transform = bone.matrix_local.copy()
		parentBone = bone.parent
		if (parentBone):
			transform = parentBone.matrix_local.inverted() * transform

		poseBone = armature.pose.bones.get(bone.name)
		if (poseBone):
			transform = poseBone.matrix.copy()
			parentPoseBone = poseBone.parent
			if (parentPoseBone):
				transform = parentPoseBone.matrix.inverted() * transform


		o.transform = Object();

		#if (animation):
		#	self.Write(B" %transform")

		o.transform.values = self.WriteMatrix(transform)

		if ((animation) and (poseBone)):
			self.ExportBoneSampledAnimation(poseBone, scene, o)



	def ExportMaterialRef(self, material, index, o):
		if (not material in self.materialArray):
			self.materialArray[material] = {"structName" : material.name}

		o.material_refs.append(self.materialArray[material]["structName"])



	def ExportNode(self, node, scene, poseBone = None, parento = None):

		# This function exports a single node in the scene and includes its name,
		# object reference, material references (for geometries), and transform.
		# Subnodes are then exported recursively.

		if (node.name[0] == "."):
			return; # Do not export nodes prefixed with '.'

		nodeRef = self.nodeArray.get(node)
		if (nodeRef):
			type = nodeRef["nodeType"]

			o = Object()
			o.type = structIdentifier[type]
			o.id = nodeRef["structName"]

			if (type == kNodeTypeGeometry):
				if (node.hide_render):
					o.visible = False

			# Export the node's name if it has one.

			##name = node.name
			##if (name != ""):
			##	o.name = name

			# Export the object reference and material references.

			object = node.data

			if (type == kNodeTypeGeometry):
				if (not object in self.geometryArray):
					#self.geometryArray[object] = {"structName" : "geometry" + str(len(self.geometryArray) + 1), "nodeTable" : [node]}
					self.geometryArray[object] = {"structName" : object.name, "nodeTable" : [node]}
				else:
					self.geometryArray[object]["nodeTable"].append(node)

				o.object_ref = self.geometryArray[object]["structName"]
				o.material_refs = []

				for i in range(len(node.material_slots)):
					self.ExportMaterialRef(node.material_slots[i].material, i, o)

				shapeKeys = LueExporter.GetShapeKeys(object)
				#if (shapeKeys):
				#	self.ExportMorphWeights(node, shapeKeys, scene, o)
				# TODO

			elif (type == kNodeTypeLight):
				if (not object in self.lightArray):
					#self.lightArray[object] = {"structName" : "light" + str(len(self.lightArray) + 1), "nodeTable" : [node]}
					self.lightArray[object] = {"structName" : object.name, "nodeTable" : [node]}
				else:
					self.lightArray[object]["nodeTable"].append(node)

				o.object_ref = self.lightArray[object]["structName"]

			elif (type == kNodeTypeCamera):
				if (not object in self.cameraArray):
					#self.cameraArray[object] = {"structName" : "camera" + str(len(self.cameraArray) + 1), "nodeTable" : [node]}
					self.cameraArray[object] = {"structName" : object.name, "nodeTable" : [node]}
				else:
					self.cameraArray[object]["nodeTable"].append(node)

				o.object_ref = self.cameraArray[object]["structName"]

			if (poseBone):

				# If the node is parented to a bone and is not relative, then undo the bone's transform.

				o.transform = Object()
				o.transform.values = self.WriteMatrix(poseBone.matrix.inverted())

			# Export the transform. If the node is animated, then animation tracks are exported here.

			self.ExportNodeTransform(node, scene, o)

			if (node.type == "ARMATURE"):
				skeleton = node.data
				if (skeleton):
					o.nodes = []
					for bone in skeleton.bones:
						if (not bone.parent):
							co = Object() # TODO
							self.ExportBone(node, bone, scene, co)
							o.nodes.append(co)

			if (parento == None):
				self.output.nodes.append(o)
			else:
				parento.nodes.append(o)


		o.traits = [] # TODO: export only for geometry nodes and nodes
		if not hasattr(o, 'nodes'):
			o.nodes = []
		for subnode in node.children:
			if (subnode.parent_type != "BONE"):
				self.ExportNode(subnode, scene, None, o)








	def ExportSkin(self, node, armature, exportVertexArray, om):

		# This function exports all skinning data, which includes the skeleton
		# and per-vertex bone influence data.

		om.skin = Object()

		# Write the skin bind pose transform.

		om.skin.transform = Object()
		om.skin.transform.values = self.WriteMatrix(node.matrix_world)

		# Export the skeleton, which includes an array of bone node references
		# and and array of per-bone bind pose transforms.

		om.skin.skeleton = Object()

		# Write the bone node reference array.

		om.skin.skeleton.bone_ref_array = []

		boneArray = armature.data.bones
		boneCount = len(boneArray)

		#self.IndentWrite(B"ref\t\t\t// ")
		#self.WriteInt(boneCount)

		for i in range(boneCount):
			boneRef = self.FindNode(boneArray[i].name)
			if (boneRef):
				om.skin.skeleton.bone_ref_array.append(boneRef[1]["structName"])
			else:
				om.skin.skeleton.bone_ref_array.append("null")

		# Write the bind pose transform array.

		om.skin.skeleton.transforms = []

		#self.IndentWrite(B"float[16]\t// ")
		#self.WriteInt(boneCount)

		for i in range(boneCount):
			om.skin.skeleton.transforms.append(self.WriteMatrixFlat(armature.matrix_world * boneArray[i].matrix_local))

		# Export the per-vertex bone influence data.

		groupRemap = []

		for group in node.vertex_groups:
			groupName = group.name
			for i in range(boneCount):
				if (boneArray[i].name == groupName):
					groupRemap.append(i)
					break
			else:
				groupRemap.append(-1)

		boneCountArray = []
		boneIndexArray = []
		boneWeightArray = []

		meshVertexArray = node.data.vertices
		for ev in exportVertexArray:
			boneCount = 0
			totalWeight = 0.0
			for element in meshVertexArray[ev.vertexIndex].groups:
				boneIndex = groupRemap[element.group]
				boneWeight = element.weight
				if ((boneIndex >= 0) and (boneWeight != 0.0)):
					boneCount += 1
					totalWeight += boneWeight
					boneIndexArray.append(boneIndex)
					boneWeightArray.append(boneWeight)
			boneCountArray.append(boneCount)

			if (totalWeight != 0.0):
				normalizer = 1.0 / totalWeight
				for i in range(-boneCount, 0):
					boneWeightArray[i] *= normalizer

		# Write the bone count array. There is one entry per vertex.

		om.skin.bone_count_array = boneCountArray

		#self.IndentWrite(B"unsigned_int16\t\t// ")
		#self.WriteInt(len(boneCountArray))
		#self.WriteIntArray(boneCountArray)

		# Write the bone index array. The number of entries is the sum of the bone counts for all vertices.

		om.skin.bone_index_array = boneIndexArray

		# Write the bone weight array. The number of entries is the sum of the bone counts for all vertices.

		om.skin.bone_weight_array = boneWeightArray










	def ExportGeometry(self, objectRef, scene):

		# This function exports a single geometry object.

		o = Object()

		o.id = objectRef[1]["structName"]
		#self.WriteNodeTable(objectRef) #//
		# TODO

		node = objectRef[1]["nodeTable"][0]
		mesh = objectRef[0]

		structFlag = False;

		# Save the morph state if necessary.

		activeShapeKeyIndex = node.active_shape_key_index
		showOnlyShapeKey = node.show_only_shape_key
		currentMorphValue = []

		shapeKeys = LueExporter.GetShapeKeys(mesh)
		if (shapeKeys):
			node.active_shape_key_index = 0
			node.show_only_shape_key = True

			baseIndex = 0
			relative = shapeKeys.use_relative
			if (relative):
				morphCount = 0
				baseName = shapeKeys.reference_key.name
				for block in shapeKeys.key_blocks:
					if (block.name == baseName):
						baseIndex = morphCount
						break
					morphCount += 1

			morphCount = 0
			for block in shapeKeys.key_blocks:
				currentMorphValue.append(block.value)
				block.value = 0.0

				if (block.name != ""):
					# self.IndentWrite(B"Morph (index = ", 0, structFlag)
					# self.WriteInt(morphCount)

					# if ((relative) and (morphCount != baseIndex)):
					# 	self.Write(B", base = ")
					# 	self.WriteInt(baseIndex)

					# self.Write(B")\n")
					# self.IndentWrite(B"{\n")
					# self.IndentWrite(B"Name {string {\"", 1)
					# self.Write(bytes(block.name, "UTF-8"))
					# self.Write(B"\"}}\n")
					# self.IndentWrite(B"}\n")
					structFlag = True

				morphCount += 1

			shapeKeys.key_blocks[0].value = 1.0
			mesh.update()

		om = Object()
		om.primitive = "triangles"

		armature = node.find_armature()
		applyModifiers = (not armature)

		# Apply all modifiers to create a new mesh with tessfaces.

		# We don't apply modifiers for a skinned mesh because we need the vertex positions
		# before they are deformed by the armature modifier in order to export the proper
		# bind pose. This does mean that modifiers preceding the armature modifier are ignored,
		# but the Blender API does not provide a reasonable way to retrieve the mesh at an
		# arbitrary stage in the modifier stack.

		exportMesh = node.to_mesh(scene, applyModifiers, "RENDER", True, False)

		# Triangulate mesh and remap vertices to eliminate duplicates.

		materialTable = []
		exportVertexArray = LueExporter.DeindexMesh(exportMesh, materialTable)
		triangleCount = len(materialTable)

		indexTable = []
		unifiedVertexArray = LueExporter.UnifyVertices(exportVertexArray, indexTable)
		vertexCount = len(unifiedVertexArray)

		# Write the position array.

		om.vertex_arrays = []

		pa = Object()
		pa.attrib = "position"
		pa.size = 3
		pa.values = self.WriteVertexArray3D(unifiedVertexArray, "position")
		#self.WriteInt(vertexCount)
		om.vertex_arrays.append(pa)

		# Write the normal array.

		na = Object()
		na.attrib = "normal"
		na.size = 3
		na.values = self.WriteVertexArray3D(unifiedVertexArray, "normal")
		om.vertex_arrays.append(na)

		# Write the color array if it exists.

		colorCount = len(exportMesh.tessface_vertex_colors)
		if (colorCount > 0):
			ca = Object()
			ca.attrib = "color"
			ca.size = 3
			ca.values = self.WriteVertexArray3D(unifiedVertexArray, "color")
			om.vertex_arrays.append(ca)

		# Write the texcoord arrays.

		texcoordCount = len(exportMesh.tessface_uv_textures)
		if (texcoordCount > 0):
			ta = Object()
			ta.attrib = "texcoord"
			ta.size = 2
			ta.values = self.WriteVertexArray2D(unifiedVertexArray, "texcoord0")
			om.vertex_arrays.append(ta)

			if (texcoordCount > 1):
				ta2 = Object()
				ta2.attrib = "texcoord[1]"
				ta2.size = 2
				ta2.values = self.WriteVertexArray2D(unifiedVertexArray, "texcoord1")
				om.vertex_arrays.append(ta2)

		# If there are multiple morph targets, export them here.
		'''
		if (shapeKeys):
			shapeKeys.key_blocks[0].value = 0.0
			for m in range(1, len(currentMorphValue)):
				shapeKeys.key_blocks[m].value = 1.0
				mesh.update()

				node.active_shape_key_index = m
				morphMesh = node.to_mesh(scene, applyModifiers, "RENDER", True, False)

				# Write the morph target position array.

				self.IndentWrite(B"VertexArray (attrib = \"position\", morph = ", 0, True)
				self.WriteInt(m)
				self.Write(B")\n")
				self.IndentWrite(B"{\n")
				self.indentLevel += 1

				self.IndentWrite(B"float[3]\t\t// ")
				self.WriteInt(vertexCount)
				self.IndentWrite(B"{\n", 0, True)
				self.WriteMorphPositionArray3D(unifiedVertexArray, morphMesh.vertices)
				self.IndentWrite(B"}\n")

				self.indentLevel -= 1
				self.IndentWrite(B"}\n\n")

				# Write the morph target normal array.

				self.IndentWrite(B"VertexArray (attrib = \"normal\", morph = ")
				self.WriteInt(m)
				self.Write(B")\n")
				self.IndentWrite(B"{\n")
				self.indentLevel += 1

				self.IndentWrite(B"float[3]\t\t// ")
				self.WriteInt(vertexCount)
				self.IndentWrite(B"{\n", 0, True)
				self.WriteMorphNormalArray3D(unifiedVertexArray, morphMesh.vertices, morphMesh.tessfaces)
				self.IndentWrite(B"}\n")

				self.indentLevel -= 1
				self.IndentWrite(B"}\n")

				bpy.data.meshes.remove(morphMesh)
		'''
		# Write the index arrays.

		om.index_arrays = []

		maxMaterialIndex = 0
		for i in range(len(materialTable)):
			index = materialTable[i]
			if (index > maxMaterialIndex):
				maxMaterialIndex = index

		if (maxMaterialIndex == 0):
			
			# There is only one material, so write a single index array.

			ia = Object()
			ia.size = 3
			ia.values = self.WriteTriangleArray(triangleCount, indexTable)
			ia.material = self.WriteInt(0)
			om.index_arrays.append(ia)
		
		else:

			# If there are multiple material indexes, then write a separate index array for each one.

			materialTriangleCount = [0 for i in range(maxMaterialIndex + 1)]
			for i in range(len(materialTable)):
				materialTriangleCount[materialTable[i]] += 1

			for m in range(maxMaterialIndex + 1):
				if (materialTriangleCount[m] != 0):
					materialIndexTable = []
					for i in range(len(materialTable)):
						if (materialTable[i] == m):
							k = i * 3
							materialIndexTable.append(indexTable[k])
							materialIndexTable.append(indexTable[k + 1])
							materialIndexTable.append(indexTable[k + 2])

					ia = Object()
					ia.size = 3
					ia.values = self.WriteTriangleArray(materialTriangleCount[m], materialIndexTable)
					ia.material = self.WriteInt(m)
					om.index_arrays.append(ia)
		
		# If the mesh is skinned, export the skinning data here.

		if (armature):
			self.ExportSkin(node, armature, unifiedVertexArray, om)

		# Restore the morph state.

		if (shapeKeys):
			node.active_shape_key_index = activeShapeKeyIndex
			node.show_only_shape_key = showOnlyShapeKey

			for m in range(len(currentMorphValue)):
				shapeKeys.key_blocks[m].value = currentMorphValue[m]

			mesh.update()

		# Delete the new mesh that we made earlier.

		bpy.data.meshes.remove(exportMesh)

		o.mesh = om
		self.output.geometry_resources.append(o)


	def ExportLight(self, objectRef):

		# This function exports a single light object.

		o = Object()
		o.id = objectRef[1]["structName"]

		object = objectRef[0]
		type = object.type

		pointFlag = False
		spotFlag = False

		if (type == "SUN"):
			o.type = "sun"
		elif (type == "POINT"):
			o.type = "point"
			#pointFlag = True
		else:
			o.type = "spot"
			#pointFlag = True
			#spotFlag = True

		#if (not object.use_shadow):
		#	self.Write(B", shadow = false")

		#self.WriteNodeTable(objectRef)

		# Export the light's color, and include a separate intensity if necessary.

		# lc = Object()
		# lc.attrib = "light"
		# lc.size = 3
		# lc.values = self.WriteColor(object.color)
		# o.color = lc
		o.color = self.WriteColor(object.color)

		'''
		intensity = object.energy
		if (intensity != 1.0):
			self.IndentWrite(B"Param (attrib = \"intensity\") {float {")
			self.WriteFloat(intensity)
			self.Write(B"}}\n")

		if (pointFlag):

			# Export a separate attenuation function for each type that's in use.

			falloff = object.falloff_type

			if (falloff == "INVERSE_LINEAR"):
				self.IndentWrite(B"Atten (curve = \"inverse\")\n", 0, True)
				self.IndentWrite(B"{\n")

				self.IndentWrite(B"Param (attrib = \"scale\") {float {", 1)
				self.WriteFloat(object.distance)
				self.Write(B"}}\n")

				self.IndentWrite(B"}\n")

			elif (falloff == "INVERSE_SQUARE"):
				self.IndentWrite(B"Atten (curve = \"inverse_square\")\n", 0, True)
				self.IndentWrite(B"{\n")

				self.IndentWrite(B"Param (attrib = \"scale\") {float {", 1)
				self.WriteFloat(math.sqrt(object.distance))
				self.Write(B"}}\n")

				self.IndentWrite(B"}\n")

			elif (falloff == "LINEAR_QUADRATIC_WEIGHTED"):
				if (object.linear_attenuation != 0.0):
					self.IndentWrite(B"Atten (curve = \"inverse\")\n", 0, True)
					self.IndentWrite(B"{\n")

					self.IndentWrite(B"Param (attrib = \"scale\") {float {", 1)
					self.WriteFloat(object.distance)
					self.Write(B"}}\n")

					self.IndentWrite(B"Param (attrib = \"constant\") {float {", 1)
					self.WriteFloat(1.0)
					self.Write(B"}}\n")

					self.IndentWrite(B"Param (attrib = \"linear\") {float {", 1)
					self.WriteFloat(object.linear_attenuation)
					self.Write(B"}}\n")

					self.IndentWrite(B"}\n\n")

				if (object.quadratic_attenuation != 0.0):
					self.IndentWrite(B"Atten (curve = \"inverse_square\")\n")
					self.IndentWrite(B"{\n")

					self.IndentWrite(B"Param (attrib = \"scale\") {float {", 1)
					self.WriteFloat(object.distance)
					self.Write(B"}}\n")

					self.IndentWrite(B"Param (attrib = \"constant\") {float {", 1)
					self.WriteFloat(1.0)
					self.Write(B"}}\n")

					self.IndentWrite(B"Param (attrib = \"quadratic\") {float {", 1)
					self.WriteFloat(object.quadratic_attenuation)
					self.Write(B"}}\n")

					self.IndentWrite(B"}\n")

			if (object.use_sphere):
				self.IndentWrite(B"Atten (curve = \"linear\")\n", 0, True)
				self.IndentWrite(B"{\n")

				self.IndentWrite(B"Param (attrib = \"end\") {float {", 1)
				self.WriteFloat(object.distance)
				self.Write(B"}}\n")

				self.IndentWrite(B"}\n")

			if (spotFlag):

				# Export additional angular attenuation for spot lights.

				self.IndentWrite(B"Atten (kind = \"angle\", curve = \"linear\")\n", 0, True)
				self.IndentWrite(B"{\n")

				endAngle = object.spot_size * 0.5
				beginAngle = endAngle * (1.0 - object.spot_blend)

				self.IndentWrite(B"Param (attrib = \"begin\") {float {", 1)
				self.WriteFloat(beginAngle)
				self.Write(B"}}\n")

				self.IndentWrite(B"Param (attrib = \"end\") {float {", 1)
				self.WriteFloat(endAngle)
				self.Write(B"}}\n")

				self.IndentWrite(B"}\n")

		'''
		self.output.light_resources.append(o)

	def ExportCamera(self, objectRef):

		# This function exports a single camera object.

		o = Object()
		o.id = objectRef[1]["structName"]

		#self.WriteNodeTable(objectRef)

		object = objectRef[0]

		#o.fov = object.angle_x
		o.near_plane = object.clip_start
		o.far_plane = object.clip_end
		o.frustum_culling = False
		o.pipeline = "blender_resource/blender_pipeline"
		o.clear_color = [0.0, 0.0, 0.0, 1.0]
		o.type = "perspective"
		
		self.output.camera_resources.append(o)


	def ExportMaterials(self):

		# This function exports all of the materials used in the scene.

		for materialRef in self.materialArray.items():
			o = Object()
			material = materialRef[0]

			# If the material is unlinked, material becomes None.
			if material == None:
				continue

			o.id = materialRef[1]["structName"]

			#if (material.name != ""):
			#	o.name = material.name

			intensity = material.diffuse_intensity
			diffuse = [material.diffuse_color[0] * intensity, material.diffuse_color[1] * intensity, material.diffuse_color[2] * intensity]

			o.shader = "blender_resource/blender_shader"
			o.cast_shadow = True
			o.contexts = []
			
			c = Object()
			c.id = "lighting"
			c.bind_constants = []
			const1 = Object()
			const1.id = "diffuseColor"
			const1.vec4 = [1, 1, 1, 1]
			c.bind_constants.append(const1)
			const2 = Object()
			const2.id = "roughness"
			const2.float = 0
			c.bind_constants.append(const2)
			const3 = Object()
			const3.id = "lighting"
			const3.bool = True
			c.bind_constants.append(const3)
			const4 = Object()
			const4.id = "receiveShadow"
			const4.bool = True
			c.bind_constants.append(const4)
			const5 = Object()
			const5.id = "texturing"
			const5.bool = False
			c.bind_constants.append(const5)

			c.bind_textures = []
			tex1 = Object()
			tex1.id = "stex"
			tex1.name = ""
			c.bind_textures.append(tex1)

			o.contexts.append(c)

			#intensity = material.specular_intensity
			#specular = [material.specular_color[0] * intensity, material.specular_color[1] * intensity, material.specular_color[2] * intensity]

			'''
			if ((specular[0] > 0.0) or (specular[1] > 0.0) or (specular[2] > 0.0)):
				self.IndentWrite(B"Color (attrib = \"specular\") {float[3] {")
				self.WriteColor(specular)
				self.Write(B"}}\n")

				self.IndentWrite(B"Param (attrib = \"specular_power\") {float {")
				self.WriteFloat(material.specular_hardness)
				self.Write(B"}}\n")

			emission = material.emit
			if (emission > 0.0):
				self.IndentWrite(B"Color (attrib = \"emission\") {float[3] {")
				self.WriteColor([emission, emission, emission])
				self.Write(B"}}\n")

			diffuseTexture = None
			specularTexture = None
			emissionTexture = None
			transparencyTexture = None
			normalTexture = None

			for textureSlot in material.texture_slots:
				if ((textureSlot) and (textureSlot.use) and (textureSlot.texture.type == "IMAGE")):
					if (((textureSlot.use_map_color_diffuse) or (textureSlot.use_map_diffuse)) and (not diffuseTexture)):
						diffuseTexture = textureSlot
					elif (((textureSlot.use_map_color_spec) or (textureSlot.use_map_specular)) and (not specularTexture)):
						specularTexture = textureSlot
					elif ((textureSlot.use_map_emit) and (not emissionTexture)):
						emissionTexture = textureSlot
					elif ((textureSlot.use_map_translucency) and (not transparencyTexture)):
						transparencyTexture = textureSlot
					elif ((textureSlot.use_map_normal) and (not normalTexture)):
						normalTexture = textureSlot

			if (diffuseTexture):
				self.ExportTexture(diffuseTexture, B"diffuse")
			if (specularTexture):
				self.ExportTexture(specularTexture, B"specular")
			if (emissionTexture):
				self.ExportTexture(emissionTexture, B"emission")
			if (transparencyTexture):
				self.ExportTexture(transparencyTexture, B"transparency")
			if (normalTexture):
				self.ExportTexture(normalTexture, B"normal")
			'''
			self.output.material_resources.append(o)


	def ExportObjects(self, scene):
		for objectRef in self.geometryArray.items():
			self.ExportGeometry(objectRef, scene)
		for objectRef in self.lightArray.items():
			self.ExportLight(objectRef)
		for objectRef in self.cameraArray.items():
			self.ExportCamera(objectRef)


	def execute(self, context):
		self.output = Object()

		scene = context.scene

		originalFrame = scene.frame_current
		originalSubframe = scene.frame_subframe
		self.restoreFrame = False

		self.beginFrame = scene.frame_start
		self.endFrame = scene.frame_end
		self.frameTime = 1.0 / (scene.render.fps_base * scene.render.fps)

		self.nodeArray = {}
		self.geometryArray = {}
		self.lightArray = {}
		self.cameraArray = {}
		self.materialArray = {}
		self.boneParentArray = {}

		self.exportAllFlag = not self.option_export_selection
		self.sampleAnimationFlag = self.option_sample_animation


		for object in scene.objects:
			if (not object.parent):
				self.ProcessNode(object)

		self.ProcessSkinnedMeshes()


		self.output.nodes = []
		for object in scene.objects:
			if (not object.parent):
				self.ExportNode(object, scene)

		self.output.geometry_resources = [];
		self.output.light_resources = [];
		self.output.camera_resources = [];
		self.ExportObjects(scene)

		self.output.material_resources = []
		self.ExportMaterials()


		if (self.restoreFrame):
			scene.frame_set(originalFrame, originalSubframe)

		# Output
		with open(self.filepath, 'w') as f:
			f.write(self.output.to_JSON())

		return {'FINISHED'}



def menu_func(self, context):
	self.layout.operator(LueExporter.bl_idname, text = "Lue (.json)")

def register():
	bpy.utils.register_class(LueExporter)
	bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
	bpy.types.INFO_MT_file_export.remove(menu_func)
	bpy.utils.unregister_class(LueExporter)

if __name__ == "__main__":
	register()
