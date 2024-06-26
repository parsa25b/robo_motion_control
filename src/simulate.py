import argparse
import time
import mujoco_viewer
from pathlib import Path
from ik_levenberg_marquardt import LevenbegMarquardtIK
from ik_gradient_descent import GradientDescentIK
import mujoco
import numpy as np
from robot_env import RobotEnv


def circle(t: float, r: float, h: float, k: float, f: float) -> np.ndarray:
    """Return the (x, y) coordinates of a circle with radius r centered at (h, k)
    as a function of time t and frequency f."""
    x = r * np.cos(2 * np.pi * f * t) + h
    y = r * np.sin(2 * np.pi * f * t) + k
    z = 0.5
    return np.array([x, y, z])


def simulate(args):
    """
    Simulates the robot control loop.

    Args:
        args (object): The arguments object containing the simulation parameters.
    """

    # Environment setup
    env = RobotEnv(model_path=Path("src/assets/" + args.robot_model + "/scene.xml"))
    inter_frame_sleep = 0.01

    # ik = GradientDescentIK(env)
    ik = LevenbegMarquardtIK(env)

    # End-effector we wish to control.
    site_name = "end_effector"
    site_id = env.model.site(site_name).id
    mocap_id = env.model.body("target").mocapid[0]

    obs, _ = env.reset()

    # Initialize the mujoco viewer #TODO add this to the UR5eMujocoEnv instead of using mujoco_py
    viewer = mujoco_viewer.MujocoViewer(env.model, env.data)
    # Reset the simulation
    mujoco.mj_resetDataKeyframe(env.model, env.data, 0)

    while True:
        if viewer.is_alive:
            # ee_reference_pose = circle(env.data.time, 0.1, 0.3, 0.0, 0.5)  # ENABLE to test circle.
            ee_reference_pose = np.concatenate(
                (env.data.mocap_pos[mocap_id], env.data.mocap_quat[mocap_id])
            )

            # Inverse Kinematics calculations
            qpos = ik.calculate(ee_reference_pose, site_id)  # calculate the qpos
            env.step(action=qpos)

            # print(f"ee_reference_pose: {ee_reference_pose}")
            # print(f"data.site_xpos={env.data.site_xquat(site_id)}")
            viewer.render()
            # Slow down the rendering
            time.sleep(inter_frame_sleep)
        else:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--robot-model",
        type=str,
        default="universal_robots_ur5e",
        help="Name of the robot model",
    )
    args = parser.parse_args()

    simulate(args)
