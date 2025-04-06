# pytracik - Python Bindings for Trac-IK

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Welcome to pytracik, a Python library providing an easy and efficient way to utilize the powerful [Trac-IK](https://bitbucket.org/traclabs/trac_ik/src/master/) inverse kinematics solver. Supporting Python 3.8+ and offering excellent compatibility across Linux environments, pytracik simplifies the integration process by eliminating the need for ROS installation.

**Key Features**:

- **ROS-Free Integration**: Seamlessly incorporate Trac-IK's robust inverse kinematics capabilities into your Python projects without requiring ROS. However, the following external libraries are necessary for operation:
   - `boost`
   - `eigen`
   - `orocos-kdl`
   - `nlopt`
- **Cross-Platform Compatibility**: Ensures consistent functionality across various Linux environments.

## Links
- Trac-IK Repository: https://bitbucket.org/traclabs/trac_ik/src/master/
- Trac-IK Homepage: https://traclabs.com/projects/trac-ik/
- Other ROS-Free Trac-IK Python Bindings: https://github.com/mjd3/tracikpy

# Quick Start
```python
import os
import numpy as np
from pytracik.trac_ik import TracIK

# Set the path to the URDF file
urdf_path = os.path.join(os.path.dirname(__file__), "urdf/yumi.urdf")

# Initialize IK solvers for the right and left arms
yumi_rgt_arm_iksolver = TracIK(base_link_name="yumi_body",
                             tip_link_name="yumi_link_7_r",
                             urdf_path=urdf_path)
yumi_lft_arm_iksolver = TracIK(base_link_name="yumi_body",
                             tip_link_name="yumi_link_7_l",
                             urdf_path=urdf_path)

# Initial joint angles
seed_jnt = np.array([-0.34906585, -1.57079633, -2.0943951, 0.52359878, 0.,
                   0.6981317, 0.])
# Target position
tgt_pos = np.array([.3, -.4, .1])
# Target rotation matrix
tgt_rotmat = np.array([[0.5, 0., 0.8660254],
                     [0., 1., 0.],
                     [-0.8660254, 0., 0.5]])

# Calculate inverse kinematics for the right arm
result = yumi_rgt_arm_iksolver.ik(tgt_pos, tgt_rotmat, seed_jnt_values=seed_jnt)
print(result)
```
Output:
```python
[ 1.17331584 -1.99621953 -1.08811406 -0.18234367  0.66571608  1.26591
  0.18141696]
```

# Installation

## Installation on Linux
This section demonstrates the installation process using Ubuntu 24.04 as an example.

1. Install dependencies: 1. _Boost_ 2. _Eigen3_ 3. _Orocos_ KDL 4. _NLopt_
    ```Bash
    sudo apt install libboost-all-dev libeigen3-dev liborocos-kdl-dev libnlopt-dev 
    ```

2. Make installation:
   ```bash
   pip install -e .
   ```

