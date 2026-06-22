let project = new Project('haxerecast', __dirname);

project.addFile('recastnavigation/**');
project.addIncludeDir('recastnavigation/src');
project.addIncludeDir('recastnavigation/Recast/Include');
project.addIncludeDir('recastnavigation/Detour/Include');
project.addIncludeDir('recastnavigation/DetourCrowd/Include');
project.addIncludeDir('recastnavigation/DetourTileCache/Include');
project.addIncludeDir('recastnavigation/RecastDemo/Include');
project.addIncludeDir('recastnavigation/DebugUtils/Include');
project.addIncludeDir('recastnavigation/RecastDemo/Contrib/fastlz');
project.addFile('hl/recast.cpp');

resolve(project);