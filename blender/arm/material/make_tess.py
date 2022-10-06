
def tesc_levels(tesc, innerLevel, outerLevel):
    tesc.write('if (gl_InvocationID == 0) {')
    tesc.write('    gl_TessLevelInner[0] = {0}; // inner level'.format(innerLevel))
    tesc.write('    gl_TessLevelInner[1] = {0};'.format(innerLevel))
    tesc.write('    gl_TessLevelOuter[0] = {0}; // outer level'.format(outerLevel))
    tesc.write('    gl_TessLevelOuter[1] = {0};'.format(outerLevel))
    tesc.write('    gl_TessLevelOuter[2] = {0};'.format(outerLevel))
    tesc.write('    gl_TessLevelOuter[3] = {0};'.format(outerLevel))
    tesc.write('}')

def interpolate(tese, var, size, normalize=False, declare_out=False):
    tese.add_include('compiled.inc')
    vec = 'vec{0}'.format(size)
    if declare_out:
        tese.add_out('{0} {1}'.format(vec, var))

    s = '{0} {1}_0 = gl_TessCoord.x * tc_{1}[0];\n'.format(vec, var)
    s += '{0} {1}_1 = gl_TessCoord.y * tc_{1}[1];\n'.format(vec, var)
    s += '{0} {1}_2 = gl_TessCoord.z * tc_{1}[2];\n'.format(vec, var)
    
    prep = ''
    if not declare_out:
        prep = vec + ' '

    if normalize:
        s += '{0}{1} = normalize({1}_0 + {1}_1 + {1}_2);\n'.format(prep, var)
        s += 'vec3 n = {0};\n'.format(var)
    else:
        s += '{0}{1} = {1}_0 + {1}_1 + {1}_2;\n'.format(prep, var)

    tese.write_attrib(s)
