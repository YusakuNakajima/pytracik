""" 
Originally from:
Author: Hao Chen (chen960216@gmail.com)
Created: 20220811osaka

Modified by:
Author: Yusaku Nakajima (yusaku_nakajima@ap.eng.osaka-u.ac.jp)
Copyright (c) 2025 Osaka University
All rights reserved.
"""

from pathlib import Path
from typing import Literal, Union

import numpy as np
import pytracik
from scipy.spatial.transform import Rotation



class TracIK(object):
    def __init__(self, base_link_name: str,
                 tip_link_name: str,
                 urdf_path: str,
                 timeout: float = .005,
                 epsilon: float = 1e-5,
                 solver_type: Literal['Speed', 'Distance', 'Manip1', 'Manip2'] = "Speed"):
        """
        Create a TRAC_IK instance and keep track of it.
        This file is made changes from the original trac_ik.py file in the https://bitbucket.org/traclabs/trac_ik/src/master/trac_ik_python/src/trac_ik_python/trac_ik.py

        :param str base_link: Starting link of the chain.
        :param str tip_link: Last link of the chain.
        :param float timeout: Timeout in seconds for the IK calls.
        :param float epsilon: Error epsilon.
        :param solve_type str: Type of solver, can be:
            Speed (default), Distance, Manipulation1, Manipulation2
        :param urdf_string str: Optional arg, if not given URDF is taken from
            the param server at /robot_description.
        """
        if solver_type == "Speed":
            _solve_type = pytracik.SolveType.Speed
        elif solver_type == "Distance":
            _solve_type = pytracik.SolveType.Distance
        elif solver_type == "Manip1":
            _solve_type = pytracik.SolveType.Manip1
        elif solver_type == "Manip2":
            _solve_type = pytracik.SolveType.Manip2
        else:
            raise ValueError(f"Unsupported solver type: {solver_type}")

        urdf_path = Path(urdf_path)
        if urdf_path.exists():
            urdf_string = urdf_path.read_text()
        else:
            raise ValueError(f"{urdf_path} is not exist")
        self._urdf_string = urdf_string
        self._timeout = timeout
        self._epsilon = epsilon
        self._solve_type = _solve_type
        self.base_link_name = base_link_name
        self.tip_link_name = tip_link_name
        self._ik_solver = pytracik.TRAC_IK(self.base_link_name,
                                                    self.tip_link_name,
                                                    self._urdf_string,
                                                    self._timeout,
                                                    self._epsilon,
                                                    self._solve_type)

    @property
    def dof(self) -> int:
        """
        Get the number of joints in the chain.
        :return:  Number of joints in the chain.
        """
        return pytracik.get_num_joints(self._ik_solver, self.base_link_name, self.tip_link_name)

    def ik(self,
           tgt_pos: np.ndarray,
           tgt_rot: Union[np.ndarray, list, tuple],
           seed_jnt_values: np.ndarray) -> None or np.ndarray:
        """
        Solve the IK.
        :param tgt_pos: 1x3 target position
        :param tgt_rot: target rotation. Can be:
            - 3x3 rotation matrix (np.ndarray)
            - quaternion (list or tuple of 4 elements: [qx, qy, qz, qw] or [qw, qx, qy, qz])
            - euler angles (list or tuple of 3 elements: [roll, pitch, yaw] in radians)
        :param seed_jnt_values: 1xN seed joint values
        :return: None if no solution is found, otherwise 1xN joint values
        """
        if not isinstance(tgt_pos, np.ndarray):
            try:
                tgt_pos = np.array(tgt_pos, dtype=float)
            except Exception as e:
                raise ValueError("tgt_pos must be convertible to a numpy array of shape (3,)") from e
        if tgt_pos.shape != (3,):
            raise ValueError("tgt_pos must be a numpy array of shape (3,)")

        if isinstance(tgt_rot, np.ndarray):
            if tgt_rot.shape == (3, 3):
                # Rotation matrix
                rotation = Rotation.from_matrix(tgt_rot)
            elif tgt_rot.shape == (4,):
                # Quaternion
                rotation = Rotation.from_quat(tgt_rot)
            elif tgt_rot.shape == (3,):
                # Euler angles (assuming XYZ order)
                rotation = Rotation.from_euler("xyz", tgt_rot)
            else:
                raise ValueError("tgt_rot as np.ndarray must be a 3x3 rotation matrix, a quaternion (4 elements) or euler angles (3 elements)")
        elif isinstance(tgt_rot, (list, tuple)):
            if len(tgt_rot) == 4:
                # Quaternion
                rotation = Rotation.from_quat(tgt_rot)
            elif len(tgt_rot) == 3:
                # Euler angles (assuming XYZ order)
                rotation = Rotation.from_euler("xyz", tgt_rot)
            else:
                raise ValueError("tgt_rot as list or tuple must be a quaternion (4 elements) or euler angles (3 elements)")
        else:
            raise ValueError("tgt_rot must be a numpy array (3x3 rotation matrix), a list or tuple (quaternion or euler angles)")

        quaternion = rotation.as_quat()
        qw, qx, qy, qz = quaternion[3], quaternion[0], quaternion[1], quaternion[2]
        r = pytracik.ik(self._ik_solver, seed_jnt_values, tgt_pos[0], tgt_pos[1], tgt_pos[2], qx, qy, qz, qw)
        succ = r[0] >=0
        if succ:
            return r[1:]
        else:
            return np.array([])

    def fk(self, q: np.ndarray) -> (np.ndarray, np.ndarray):
        """
        Forward kinematics.
        :param q: 1xN joint values
        :return: position and rotation matrix of the tip link
        """
        assert isinstance(q, np.ndarray), f"q must be a numpy array, not {type(q)}"
        assert q.shape == (self.dof,), f"q must be a 1x{self.dof} array, not {q.shape}"
        homomat = pytracik.fk(self._ik_solver, q)
        return homomat[:3, 3], homomat[:3, :3]
