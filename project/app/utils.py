import pyproj


def ecef2lla(pos_x, pos_y, pos_z):
    ecef = pyproj.Proj(proj="geocent", ellps="WGS84", datum="WGS84")
    lla = pyproj.Proj(proj="latlong", ellps="WGS84", datum="WGS84")
    lona, lata, alta = pyproj.transform(
    ecef, lla, pos_x, pos_y, pos_z, radians=False
    )
    return lona, lata, alta