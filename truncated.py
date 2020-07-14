def is_truncated(pycgm_data):
    markers = None
    analogs = None
    offset = None

    # do we have markers
    if len([*pycgm_data.Data['Markers']]) > 0:
        markers = True

    # do we have analogs
    if len([*pycgm_data.Data['Analogs']]) > 0:
        analogs = True

    # use markers in first instance
    if markers:
        length_points = len(pycgm_data.Data['Markers'][[*pycgm_data.Data['Markers']][0]][0])
        last_frame = pycgm_data.Gen['Vid_LastFrame']

        if last_frame > length_points:
            num_points = length_points
            offset = last_frame - (num_points - 1)
        else:
            num_points = last_frame

    if not markers and analogs:
        pointsamp = pycgm_data.Gen['Vid_SampRate']
        analogsamp = pycgm_data.Gen['Analog_SampRate']
        downsample = int(analogsamp / pointsamp)
        key = [*pycgm_data.Data['Analogs']][0]
        length_points = len(pycgm_data.Data['Analogs'][key][0::downsample])
        last_frame = pycgm_data.Gen['Vid_LastFrame']

        if last_frame > length_points:
            num_points = length_points
            offset = last_frame - (num_points - 1)
        else:
            num_points = last_frame

    return num_points, offset

