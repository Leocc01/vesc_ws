from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


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
        # teleop
        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_node',
            parameters=[{
                'axis_linear': {'x': 1},
                'axis_angular': {'yaw': 0},
                'scale_linear': {'x': 0.3},    # 처음엔 낮게
                'scale_angular': {'yaw': 0.5},
                'enable_button': 4,             # LB 누른 상태에서만 동작
            }]
        ),
        Node(
            package='rc_bringup',
            executable='cmd_vel_to_vesc',
            name='cmd_vel_to_vesc',
            ),
    ])
