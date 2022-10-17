from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    launch_d = LaunchDescription()
    
    hidex_module_client = Node(
            package = 'hidex_module_client',
            namespace = 'hidex_module_client',
            executable = 'hidex_module_client',
            output = "screen",
            name='biometraNode'
    )

    launch_d.add_action(hidex_module_client)
    return launch_d
    