# Copyright 2021 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# See https://floris.readthedocs.io for documentation


import matplotlib.pyplot as plt
import numpy as np

from floris.tools import FlorisInterface
from floris.tools.visualization import visualize_cut_plane


# Initialize the FLORIS interface fi
# For basic usage, the florice interface provides a simplified interface to
# the underlying classes
fi = FlorisInterface("/Users/rmudafor/Development/floris/examples/example_input.json")
fi.floris.farm.farm_controller.set_yaw_angles(np.array([25.0, 0.0, 0.0]))

# Calculate wake
fi.floris.solve_for_viz()

# Get horizontal plane at default height (hub-height)
hor_plane = fi.get_hor_plane(
    x_resolution=100,
    y_resolution=100,
)

# Plot and show
fig, ax = plt.subplots()
visualize_cut_plane(hor_plane, ax=ax)
plt.show()
