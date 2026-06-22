let project = new Project('haxebullet', __dirname);

project.addFile('bullet/**');
project.addIncludeDir('bullet');

project.addFile('hl/bullet.cpp');
project.addFile('hl/DebugDrawer.cpp');

resolve(project);
