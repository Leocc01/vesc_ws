import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # VESC 드라이버
        Node(
            package='vesc_driver',
            executable='vesc_driver_node',
            name='vesc_driver',
            parameters=[os.path.join(
                get_package_share_directory('vesc_driver'),
                'params', 'vesc_config.yaml'
            )]
        ),
        # 조이스틱
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
        ),
        # Keep RB turbo subordinate to the LB dead-man button.
        Node(
            package='rc_bringup',
            executable='joy_safety_filter',
            name='joy_safety_filter',
            parameters=[{
                'enable_button': 4,
                'turbo_button': 5,
            }],
        ),
        # teleop
        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_node',
            remappings=[('/joy', '/joy_safe')],
            parameters=[{
                'axis_linear': {'x': 1},
                # F710 XInput right-stick X is commonly axis 3. Verify with
                # `ros2 topic echo /joy`; some mappings expose it as axis 2.
                'axis_angular': {'yaw': 3},
                'scale_linear': {'x': 0.3},
                'scale_angular': {'yaw': 0.5},
                'enable_button': 4,  # LB must be held to drive.
                # F710 XInput RB is normally button 5. Verify on /joy.
                'enable_turbo_button': 5,
                'scale_linear_turbo': {'x': 0.8},
                'scale_angular_turbo': {'yaw': 0.5},
                'require_enable_button': True,
            }]
        ),
        Node(
            package='rc_bringup',
            executable='cmd_vel_to_vesc',
            name='cmd_vel_to_vesc',
            parameters=[{
                'erpm_gain': 8000.0,
                'servo_center': 0.5,
                'servo_gain': 0.4,
                'servo_min': 0.3,
                'servo_max': 0.7,
                'max_erpm': 6400.0,
                'invert_motor': False,
                'invert_steering': True,
            }],
        ),
    ])
