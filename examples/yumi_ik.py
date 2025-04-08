""" 
Originally from:
Author: Hao Chen (chen960216@gmail.com)
Created: 20220811osaka

Modified by:
Author: Yusaku Nakajima (yusaku_nakajima@ap.eng.osaka-u.ac.jp)
Copyright (c) 2025 Osaka University
All rights reserved.
"""


if __name__ == '__main__':
    import os
    import time
    import numpy as np
    from pytracik.trac_ik import TracIK
    from scipy.spatial.transform import Rotation

    # Get the directory of the current file
    current_dir = os.path.dirname(__file__)
    # Construct the path to the URDF file
    urdf_path = os.path.join(current_dir, "urdf/yumi.urdf")

    yumi_rgt_arm_iksolver = TracIK(base_link_name="yumi_body",
                                   tip_link_name="yumi_link_7_r",
                                   urdf_path=urdf_path, 
                                   timeout=0.005,
                                   epsilon=1e-5,
                                   solver_type="Distance")
    attempt = 1000
    seed_jnt = np.array([-0.34906585, -1.57079633, -2.0943951, 0.52359878, 0.,
                         0.6981317, 0.])
    tgt_pos = np.array([.3, -.4, .1])

    # Define a target rotation using a rotation matrix
    tgt_rotmat = np.array([[0.5, 0., 0.8660254],
                           [0., 1., 0.],
                           [-0.8660254, 0., 0.5]])

    # Convert the rotation matrix to quaternion and Euler angles
    rotation = Rotation.from_matrix(tgt_rotmat)
    tgt_quaternion = rotation.as_quat()  # [qx, qy, qz, qw]
    tgt_euler = rotation.as_euler('xyz')  # [roll, pitch, yaw]

    print("Trial attempt:", attempt)
    print("Target Position:", tgt_pos)
    print("Target Rotation Matrix[","Shape:", tgt_rotmat.shape,"]: \n", tgt_rotmat,)
    print("Target Quaternion:", tgt_quaternion)
    print("Target Euler Angles:", tgt_euler)
    print("Seed Joint Values:", seed_jnt)

    start_time_rotmat = time.time()
    i=0
    for i in range(attempt):
        # Solve IK using the rotation matrix
        result_rotmat = yumi_rgt_arm_iksolver.ik(tgt_pos, tgt_rotmat, seed_jnt_values=seed_jnt)
        i= i+1
        if result_rotmat is not None:
            print("IK Solution (Rotation Matrix):", result_rotmat)
            break
    else:
        print("No IK solution found for Rotation Matrix.")
    end_time_rotmat = time.time()
    averaged_time_rotmat = (end_time_rotmat - start_time_rotmat)/i
    

    start_time_quaternion = time.time()
    i=0
    for i in range(attempt):
        # Solve IK using the quaternion
        result_quaternion = yumi_rgt_arm_iksolver.ik(tgt_pos, tgt_quaternion, seed_jnt_values=seed_jnt)
        i= i+1
        if result_quaternion is not None:
            print("IK Solution (Quaternion):", result_quaternion)
            break
    else:
        print("No IK solution found for Quaternion.")
    end_time_quaternion = time.time()
    averaged_time_quaternion = (end_time_quaternion - start_time_quaternion)/i

    start_time_euler = time.time()
    i=0
    for i in range(attempt):    
        # Solve IK using the Euler angles
        result_euler = yumi_rgt_arm_iksolver.ik(tgt_pos, tgt_euler, seed_jnt_values=seed_jnt)
        i= i+1
        if result_euler is not None:
            print("IK Solution (Euler Angles):", result_euler)
            break
    else:
        print("No IK solution found for Euler Angles.")
    end_time_euler = time.time()
    averaged_time_euler = (end_time_euler - start_time_euler)/i
    

    print(f"Average IK time (Rotation Matrix): {averaged_time_rotmat / i:.6f} seconds")
    print(f"Average IK time (Quaternion): {averaged_time_quaternion / i:.6f} seconds")
    print(f"Average IK time (Euler Angles): {averaged_time_euler / i:.6f} seconds")

    # Check if the results are the same (within a tolerance)
    if result_rotmat is not None and result_quaternion is not None and result_euler is not None:
        print("\nIK solutions Differ:")
        print("Difference between Rotation Matrix and Quaternion:", np.abs(result_rotmat - result_quaternion))
        print("Difference between Rotation Matrix and Euler Angles:", np.abs(result_rotmat - result_euler))
    else:
        print("\nOne or more IK solutions were not found.")

    # Check FK
    if result_rotmat is not None:
        pos_fk, rot_fk = yumi_rgt_arm_iksolver.fk(result_rotmat)
        print("\nFK result (using Rotation Matrix IK solution):")
        print("Position:", pos_fk)
        print("Rotation Matrix:\n", rot_fk)
