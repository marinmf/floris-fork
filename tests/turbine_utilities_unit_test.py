
import os
from pathlib import Path

import numpy as np
import pytest
import yaml

from floris.turbine_library import build_cosine_loss_turbine_dict, check_smooth_power_curve
from tests.conftest import SampleInputs


def test_build_turbine_dict():

    turbine_data_v3 = SampleInputs().v3type_turbine

    # Mocked up turbine data
    turbine_data_dict = {
        "wind_speed":turbine_data_v3["power_thrust_table"]["wind_speed"],
        "power_coefficient":turbine_data_v3["power_thrust_table"]["power"],
        "thrust_coefficient":turbine_data_v3["power_thrust_table"]["thrust"]
    }

    test_dict = build_cosine_loss_turbine_dict(
        turbine_data_dict,
        "test_turbine",
        generator_efficiency=turbine_data_v3["generator_efficiency"],
        hub_height=turbine_data_v3["hub_height"],
        cosine_loss_exponent_yaw=turbine_data_v3["pP"],
        cosine_loss_exponent_tilt=turbine_data_v3["pT"],
        rotor_diameter=turbine_data_v3["rotor_diameter"],
        TSR=turbine_data_v3["TSR"],
        ref_air_density=turbine_data_v3["ref_density_cp_ct"],
        ref_tilt=turbine_data_v3["ref_tilt_cp_ct"]
    )

    # Test correct error raised if power_coefficient version passed and generator efficiency
    # not specified
    with pytest.raises(KeyError):
        build_cosine_loss_turbine_dict(
            turbine_data_dict,
            "test_turbine",
            #generator_efficiency=turbine_data_v3["generator_efficiency"],
            hub_height=turbine_data_v3["hub_height"],
            cosine_loss_exponent_yaw=turbine_data_v3["pP"],
            cosine_loss_exponent_tilt=turbine_data_v3["pT"],
            rotor_diameter=turbine_data_v3["rotor_diameter"],
            TSR=turbine_data_v3["TSR"],
            ref_air_density=turbine_data_v3["ref_density_cp_ct"],
            ref_tilt=turbine_data_v3["ref_tilt_cp_ct"]
        )

    # Directly compute power, thrust values
    Cp = np.array(turbine_data_v3["power_thrust_table"]["power"])
    Ct = np.array(turbine_data_v3["power_thrust_table"]["thrust"])
    ws = np.array(turbine_data_v3["power_thrust_table"]["wind_speed"])

    P = (
        0.5 * turbine_data_v3["ref_density_cp_ct"]
        * turbine_data_v3["generator_efficiency"]
        * (np.pi * turbine_data_v3["rotor_diameter"]**2/4)
        * Cp * ws**3
    )
    T = (
        0.5 * turbine_data_v3["ref_density_cp_ct"]
        * (np.pi * turbine_data_v3["rotor_diameter"]**2/4)
        * Ct * ws**2
    )

    # Compare direct computation to those generated by build_cosine_loss_turbine_dict
    assert np.allclose(Ct, test_dict["power_thrust_table"]["thrust_coefficient"])
    assert np.allclose(P/1000, test_dict["power_thrust_table"]["power"])

    # Check that dict keys match the v4 structure
    turbine_data_v4 = SampleInputs().turbine
    assert set(turbine_data_v4.keys()) >= set(test_dict.keys())
    assert (
        set(turbine_data_v4["power_thrust_table"].keys())
        >= set(test_dict["power_thrust_table"].keys())
    )

    # Check thrust conversion from absolute value
    turbine_data_dict = {
        "wind_speed":turbine_data_v3["power_thrust_table"]["wind_speed"],
        "power": P/1000,
        "thrust": T/1000
    }

    test_dict_2 = build_cosine_loss_turbine_dict(
        turbine_data_dict,
        "test_turbine",
        hub_height=turbine_data_v4["hub_height"],
        cosine_loss_exponent_yaw=turbine_data_v4["power_thrust_table"]["cosine_loss_exponent_yaw"],
        cosine_loss_exponent_tilt=turbine_data_v4["power_thrust_table"]["cosine_loss_exponent_tilt"],
        rotor_diameter=turbine_data_v4["rotor_diameter"],
        TSR=turbine_data_v4["TSR"],
        ref_air_density=turbine_data_v4["power_thrust_table"]["ref_air_density"],
        ref_tilt=turbine_data_v4["power_thrust_table"]["ref_tilt"]
    )
    assert np.allclose(Ct, test_dict_2["power_thrust_table"]["thrust_coefficient"])


def test_check_smooth_power_curve():

    p1 = np.array([0, 1, 2, 3, 3, 3, 3, 2, 1], dtype=float)*1000 # smooth
    p2 = np.array([0, 1, 2, 3, 2.99, 3.01, 3, 2, 1], dtype=float)*1000 # non-smooth

    p3 = p1.copy()
    p3[5] = p3[5] + 9e-4  # just smooth enough

    p4 = p1.copy()
    p4[5] = p4[5] + 1.1e-3 # just not smooth enough

    # Without a shutdown region
    p5 = p1[:-3] # smooth
    p6 = p2[:-3] # non-smooth

    assert check_smooth_power_curve(p1)
    assert not check_smooth_power_curve(p2)
    assert check_smooth_power_curve(p3)
    assert not check_smooth_power_curve(p4)
    assert check_smooth_power_curve(p5)
    assert not check_smooth_power_curve(p6)
