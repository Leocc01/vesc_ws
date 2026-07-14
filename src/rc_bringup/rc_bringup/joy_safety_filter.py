import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy


class JoySafetyFilter(Node):
    """Allow the turbo button only while the dead-man button is held."""

    def __init__(self):
        super().__init__('joy_safety_filter')
        self.declare_parameter('enable_button', 4)
        self.declare_parameter('turbo_button', 5)
        self.enable_button = self.get_parameter('enable_button').value
        self.turbo_button = self.get_parameter('turbo_button').value

        self.joy_pub = self.create_publisher(Joy, '/joy_safe', 10)
        self.joy_sub = self.create_subscription(
            Joy, '/joy', self.joy_callback, 10)

    def joy_callback(self, msg):
        filtered = Joy()
        filtered.header = msg.header
        filtered.axes = list(msg.axes)
        filtered.buttons = list(msg.buttons)

        enable_pressed = (
            self.enable_button < len(filtered.buttons)
            and filtered.buttons[self.enable_button] == 1
        )
        if self.turbo_button < len(filtered.buttons) and not enable_pressed:
            filtered.buttons[self.turbo_button] = 0

        self.joy_pub.publish(filtered)


def main(args=None):
    rclpy.init(args=args)
    node = JoySafetyFilter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
