import numpy as np
from pyCGM_Single import pycgmStatic, pycgmIO, pycgmCalc
from core_operations import utilities as ut


def getfilenames():
    directory = 'C:/Users/M.Hollands/PycharmProjects/pyCGM_Studio/pyCGM-master/SampleData/ROM/'
    dynamic_trial = directory + 'Sample_Dynamic.c3d'
    static_trial = directory + 'Sample_Static.c3d'
    vsk_file = directory + 'Sample_SM.vsk'
    outputfile = directory + 'pycgm_results'

    return dynamic_trial, static_trial, vsk_file, outputfile


def loadData(dynamic_trial, static_trial, vsk_file):
    # load the data, usually there is some checks in here to make sure we loaded
    # correctly, but for now we assume its loaded
    motion_data = pycgmIO.loadData(dynamic_trial)
    vskdata = pycgmIO.loadVSK(vsk_file)
    static_data = pycgmIO.loadData(static_trial)
    # The vsk is loaded, but for some reasons the return is split, so we combine
    vsk = pycgmIO.createVskDataDict(vskdata[0], vskdata[1])
    # print("Motion Data Length:", len(motion_data))

    return motion_data, vsk, static_data


def main():
    # Load the filenames
    dynamic_trial, static_trial, vsk_file, outputfile = getfilenames()

    # Load a dynamic trial, static trial, and vsk (subject measurements)
    motion_data, vsk_data, static_data = loadData(dynamic_trial, static_trial, vsk_file)

    # Calculate the static offsets
    flat_foot = False
    calibrated_measurements = pycgmStatic.getStatic(static_data, vsk_data, flat_foot)
    # motion_data = motion_data[:500]  # temporary, just to speed up the calculation
    angles, axes = pycgmCalc.calcAngles(static_data,
                                        vsk=calibrated_measurements,
                                        splitAnglesAxis=True,
                                        formatData=True,
                                        axis=True)

    shape = np.shape(angles)
    angles = np.reshape(angles, (shape[0], shape[1] * shape[2]))
    #print(np.shape(angles))
    # print(create_dict(angles))
    # create_dict(angles)
    # print(np.shape(axes))

    # print(axes[:, 0, 0])
    # create_dict_from_bones(axes)
    # print(create_dict(angles))


def model_bones_gen():
    return ['HEDO', 'HEDA', 'HEDL', 'HEDP',  # head
            'LCLO', 'LCLA', 'LCLL', 'LCLP',  # L clavicle
            'RCLO', 'RCLA', 'RCLL', 'RCLP',  # R clavicle
            'TRXO', 'TRXA', 'TRXL', 'TRXP',  # thorax
            'LHUO', 'LHUA', 'LHUL', 'LHUP',  # L humerus
            'RHUO', 'RHUA', 'RHUL', 'RHUP',  # R humerus
            'LRAO', 'LRAA', 'LRAL', 'LRAP',  # L radius
            'RRAO', 'RRAA', 'RRAL', 'RRAP',  # R radius
            'LHNO', 'LHNA', 'LHNL', 'LHNP',  # L hand
            'RHNO', 'RHNA', 'RHNL', 'RHNP',  # R hand
            'PELO', 'PELA', 'PELL', 'PELP',  # pelvis
            "HIPO", "HIPX", "HIPY", "HIPZ",  # hip
            'LFEO', 'LFEA', 'LFEL', 'LFEP',  # L femur
            'RFEO', 'RFEA', 'RFEL', 'RFEP',  # R femur
            'LTIO', 'LTIA', 'LTIL', 'LTIP',  # L tibia
            'RTIO', 'RTIA', 'RTIL', 'RTIP',  # R tibia
            'LFOO', 'LFOA', 'LFOL', 'LFOP',  # L foot
            'RFOO', 'RFOA', 'RFOL', 'RFOP']  # R foot


def create_dict_from_bones(axes):
    axes_list = model_bones_gen()
    axes_dict = dict()
    shape = np.shape(axes)
    count = 0
    for i in range(shape[1]):
        for j in range(shape[2]):
            axes_dict[axes_list[count]] = axes[:, i, j]
            count += 1

    test = ['RFOO', 'RFOA', 'RFOL', 'RFOP']
    for key, segment in axes_dict.items():
        if key == 'RFOO':
            o = segment[0]
        if key == 'RFOA':
            a = segment[0]
        if key == 'RFOL':
            l = segment[0]
        if key == 'RFOP':
            p = segment[0]

    print(o, a, l, p)

    unit_vector = np.array(ut.unit(o - a))
    newpos = o - (unit_vector * 50)

    print(o, a, newpos)

    # axes_dict[axes_list[i + j - 1]] = axes[:, i, j]
    # print(str(i + j), axes_list[i + j - 1])
    # transpose to match ezc3d structure

    '''axes = np.transpose(axes)
    axes_dict = dict()
    # 72 axes, 216 columns (x, y, z)
    for i in range(1, 73):
        threes = i * 3
        z = threes - 1
        x = z - 2
        y = z - 1
        axes_dict[axes_list[i - 1]] = np.asarray([axes[x],
                                                  axes[y],
                                                  axes[z]])'''

    return axes_dict


def create_dict(angles):
    angles_tup = ('PelvisAngles,RHipAngles,LHipAngles,RKneeAngles,LKneeAngles,RAnkleAngles,LAnkleAngles,'
                  'RFootProgressAngles,LFootProgressAngles,HeadAngles,ThoraxAngles,NeckAngles,SpineAngles,'
                  'RShoulderAngles,LShoulderAngles,RElbowAngles,LElbowAngles,RWristAngles,LWristAngles')
    angles_list = angles_tup.split(',')
    '''angles_dict = dict()
    for i in range(np.shape(angles)[1]):
        angles_dict[angles_list[i]] = angles[:, i].T'''

    angles = np.transpose(angles)
    angles_dict = dict()

    # 19 angles, 57 columns (x, y, z)
    for i in range(1, 20):
        threes = i * 3
        z = threes - 1
        x = z - 2
        y = z - 1
        angles_dict[angles_list[i - 1]] = np.asarray([angles[x],
                                                      angles[y],
                                                      angles[z]])

    return angles_dict


#if __name__ == '__main__':
#    main()

of = np.asarray([0, 0])

print(of + np.asarray([10, 0]))