import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float64


class CmdVelToVesc(Node):
    def __init__(self):
        super().__init__('cmd_vel_to_vesc')

        self.declare_parameter('erpm_gain', 8000.0)
        self.declare_parameter('servo_center', 0.5)
        self.declare_parameter('servo_gain', 0.4)
        self.declare_parameter('servo_min', 0.3)
        self.declare_parameter('servo_max', 0.7)
        self.declare_parameter('max_erpm', 2400.0)
        self.declare_parameter('invert_motor', False)
        self.declare_parameter('invert_steering', False)

        self.erpm_gain = self.get_parameter('erpm_gain').value
        self.servo_center = self.get_parameter('servo_center').value
        self.servo_gain = self.get_parameter('servo_gain').value
        self.servo_min = self.get_parameter('servo_min').value
        self.servo_max = self.get_parameter('servo_max').value
        self.max_erpm = self.get_parameter('max_erpm').value
        self.invert_motor = self.get_parameter('invert_motor').value
        self.invert_steering = self.get_parameter(
            'invert_steering').value

        if self.servo_min > self.servo_max:
            raise ValueError('servo_min must be less than or equal to servo_max')
        if self.max_erpm < 0.0:
            raise ValueError('max_erpm must be non-negative')

        self.speed_pub = self.create_publisher(
            Float64, '/commands/motor/speed', 10)
        self.servo_pub = self.create_publisher(
            Float64, '/commands/servo/position', 10)
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_cb, 10)

    def cmd_vel_cb(self, msg):
        linear_x = msg.linear.x
        steering = msg.angular.z

        if not (math.isfinite(linear_x) and math.isfinite(steering)):
            self.get_logger().error(
                'Non-finite /cmd_vel received; stopping and centering '
                'steering')
            self.publish_command(0.0, self.servo_center)
            return

        if self.invert_motor:
            linear_x = -linear_x
        if self.invert_steering:
            steering = -steering

        erpm = linear_x * self.erpm_gain
        erpm = self.clamp(erpm, -self.max_erpm, self.max_erpm)

        servo_position = self.servo_center + self.servo_gain * steering
        servo_position = self.clamp(
            servo_position, self.servo_min, self.servo_max)

        self.publish_command(erpm, servo_position)

    @staticmethod
    def clamp(value, minimum, maximum):
        return max(minimum, min(value, maximum))

    def publish_command(self, erpm, servo_position):
        speed_msg = Float64()
        speed_msg.data = erpm
        self.speed_pub.publish(speed_msg)

        servo_msg = Float64()
        servo_msg.data = self.clamp(
            servo_position, self.servo_min, self.servo_max)
        self.servo_pub.publish(servo_msg)


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = CmdVelToVesc()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
