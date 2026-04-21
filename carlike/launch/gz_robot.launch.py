"""
gz_robot.launch.py  –  ROS2 Jazzy + Gazebo Harmonic  [FIXED]
─────────────────────────────────────────────────────────────
Các lỗi đã sửa:
  1. [FIX] 2 xe trong Gazebo: xóa plugin gz-sim-joint-state-publisher-system
     khỏi URDF  →  chỉ còn spawn duy nhất qua ros_gz_sim create.
     (Xem hướng dẫn URDF bên dưới)

  2. [FIX] "no transform" RViz:
     - Bridge /tf dùng @ (bidirectional) thay vì [ (one-way) để
       robot_state_publisher và AckermannSteering không bị conflict.
     - Xóa bridge /model/carlike_bot/pose (gây duplicate TF).
     - Thêm static_transform_publisher: map → odom (RViz cần frame gốc).

  3. [FIX] Joint states: thêm lại joint_state_broadcaster đúng thứ tự,
     spawn sau khi controller_manager sẵn sàng.

Chạy:
  ros2 launch carlike gz_robot.launch.py
  ros2 launch carlike gz_robot.launch.py x:=1.0 Y:=1.57 gui:=false
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    # ── Paths ─────────────────────────────────────────────────────────────────
    pkg_carlike = get_package_share_directory("carlike")
    pkg_ros_gz  = get_package_share_directory("ros_gz_sim")

    gz_resource_path = os.path.dirname(pkg_carlike)

    urdf_path  = os.path.join(pkg_carlike, "urdf", "car_like_description.urdf")
    world_file = os.path.join(pkg_carlike, "carlike_world.world")

    robot_description_content = ParameterValue(
        Command(["xacro ", urdf_path]),
        value_type=str,
    )

    # ── Launch Arguments ──────────────────────────────────────────────────────
    arg_gui   = DeclareLaunchArgument("gui",   default_value="true")
    arg_world = DeclareLaunchArgument("world", default_value=world_file)
    arg_x     = DeclareLaunchArgument("x",     default_value="2.0")
    arg_y     = DeclareLaunchArgument("y",     default_value="0.0")
    arg_z     = DeclareLaunchArgument("z",     default_value="0.2")
    arg_R     = DeclareLaunchArgument("R",     default_value="0.0")
    arg_P     = DeclareLaunchArgument("P",     default_value="0.0")
    arg_Y     = DeclareLaunchArgument("Y",     default_value="0.0")

    # ── Environment ───────────────────────────────────────────────────────────
    set_gz_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=gz_resource_path + ":" + pkg_carlike,
    )

    # ── 1. Gazebo ─────────────────────────────────────────────────────────────
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": ["-r -v4 ", LaunchConfiguration("world")],
            "on_exit_shutdown": "true",
        }.items(),
    )

    # ── 2. Robot State Publisher ──────────────────────────────────────────────
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {"robot_description": robot_description_content},
            {"use_sim_time": True},
        ],
    )

    # ── 3. Static TF: map → odom ──────────────────────────────────────────────
    # [FIX #2] RViz cần frame gốc "map". AckermannSteering publish odom→base_footprint,
    # robot_state_publisher publish base_footprint→base_link→..., nhưng map→odom
    # không ai publish → RViz báo "no transform from map to base_link".
    static_tf_map_odom = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_tf_map_odom",
        arguments=["0", "0", "0", "0", "0", "0", "map", "odom"],
        parameters=[{"use_sim_time": True}],
    )

    # ── 4. Spawn robot vào Gazebo ─────────────────────────────────────────────
    # [FIX #1] Chỉ spawn ở đây, KHÔNG để plugin gz-sim-joint-state-publisher-system
    # trong URDF nữa (xem ghi chú cuối file).
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        name="spawn_carlike",
        output="screen",
        arguments=[
            "-topic",          "/robot_description",
            "-name",           "carlike_bot",
            "-allow_renaming", "true",
            "-x", LaunchConfiguration("x"),
            "-y", LaunchConfiguration("y"),
            "-z", LaunchConfiguration("z"),
            "-R", LaunchConfiguration("R"),
            "-P", LaunchConfiguration("P"),
            "-Y", LaunchConfiguration("Y"),
        ],
    )

    # ── 5. Controllers ────────────────────────────────────────────────────────
    # [FIX #3] Spawn sau 5s để controller_manager kịp khởi động trong Gazebo.
    load_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager", "/controller_manager",
        ],
    )

    load_arm_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "arm_controller",
            "--controller-manager", "/controller_manager",
        ],
    )

    # ── 6. RViz ───────────────────────────────────────────────────────────────
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", os.path.join(pkg_carlike, "rviz", "robot.rviz")],
        parameters=[{"use_sim_time": True}],
    )

    # ── 7. ros_gz_bridge ──────────────────────────────────────────────────────
    # [FIX #2] Thay đổi quan trọng:
    #   - /tf dùng @ (bidirectional) thay vì [ (Gazebo→ROS only).
    #     Lý do: AckermannSteering publish odom→base_footprint qua Gazebo /tf,
    #     cần bridge về ROS; robot_state_publisher publish base_footprint→links
    #     qua ROS /tf. Bidirectional cho phép cả 2 luồng hoạt động đúng.
    #   - XÓA /model/carlike_bot/pose: plugin này tạo TF trùng với /tf,
    #     gây conflict và "no transform" trong RViz.
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gz_ros2_bridge",
        output="screen",
        arguments=[
            # Clock (BẮT BUỘC cho use_sim_time)
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",

            # LiDAR
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",

            # Camera
            "/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image",
            "/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",

            # Velocity command: ROS → Gazebo (một chiều, dùng ])
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",

            # Odometry: Gazebo → ROS
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",

            # [FIX] TF bidirectional (@) thay vì one-way ([)
            # Để cả AckermannSteering (Gazebo) và robot_state_publisher (ROS)
            # đều publish TF đúng mà không conflict.
            "/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V",
        ],
        parameters=[{"use_sim_time": True}],
    )

    # ── Assemble ──────────────────────────────────────────────────────────────
    return LaunchDescription([
        # Environment (phải đứng đầu)
        set_gz_resource_path,

        # Arguments
        arg_gui, arg_world,
        arg_x, arg_y, arg_z,
        arg_R, arg_P, arg_Y,

        # Core nodes (khởi động ngay)
        gazebo,
        robot_state_publisher,
        static_tf_map_odom,   # [FIX] thêm map→odom
        bridge,

        # Spawn robot sau 2s (chờ robot_description publish)
        TimerAction(period=2.0, actions=[spawn_robot]),

        # Controllers sau 5s (chờ Gazebo + controller_manager sẵn sàng)
        TimerAction(
            period=5.0,
            actions=[load_joint_state_broadcaster, load_arm_controller],
        ),

        # RViz sau 4s (chờ TF ổn định trước khi mở)
        TimerAction(period=4.0, actions=[rviz_node]),
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# HƯỚNG DẪN SỬA URDF (car_like_description.urdf)
# ═══════════════════════════════════════════════════════════════════════════════
#
# [FIX #1 - Lỗi 2 xe] Xóa TOÀN BỘ block plugin sau khỏi URDF:
#
#   <plugin filename="gz-sim-joint-state-publisher-system"
#           name="gz::sim::systems::JointStatePublisher">
#     <joint_name>rear_left_wheel_joint</joint_name>
#     ...
#   </plugin>
#
# Giải thích: Plugin này khiến Gazebo tự tạo một model xe từ world file,
# trong khi launch file spawn thêm 1 xe nữa qua /robot_description → 2 xe.
# joint_state_broadcaster từ ros2_control đã đảm nhận việc này rồi.
#
# GIỮ NGUYÊN các plugin sau (cần thiết):
#   - gz_ros2_control::GazeboSimROS2ControlPlugin
#   - gz::sim::systems::PosePublisher
#   - gz::sim::systems::AckermannSteering
# ═══════════════════════════════════════════════════════════════════════════════