
def inst_pos(con, vert):
    if con.is_elem('irot'):
        # http://www.euclideanspace.com/maths/geometry/rotations/conversions/eulerToMatrix/index.htm
        vert.write('float srotx = sin(irot.x);')
        vert.write('float crotx = cos(irot.x);')
        vert.write('float sroty = sin(irot.y);')
        vert.write('float croty = cos(irot.y);')
        vert.write('float srotz = sin(irot.z);')
        vert.write('float crotz = cos(irot.z);')
        vert.write('mat3 mirot = mat3(')
        vert.write('    croty * crotz, srotz, -sroty * crotz,')
        vert.write('    -croty * srotz * crotx + sroty * srotx, crotz * crotx, sroty * srotz * crotx + croty * srotx,')
        vert.write('    croty * srotz * srotx + sroty * crotx, -crotz * srotx, -sroty * srotz * srotx + croty * crotx')
        vert.write(');')
        vert.write('spos.xyz = mirot * spos.xyz;')
        if((con.data['name'] == 'mesh' or 'translucent') and vert.contains('wnormal')):
            vert.write('wnormal = normalize(N * mirot * vec3(nor.xy, pos.w));')

    if con.is_elem('iscl'):
        vert.write('spos.xyz *= iscl;')

    vert.write('spos.xyz += ipos;')
