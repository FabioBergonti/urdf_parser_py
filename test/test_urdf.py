from __future__ import print_function

import unittest
import mock
import os
import sys

# Add path to import xml_matching
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../src')))

from xml.dom import minidom  # noqa
from xml_matching import xml_matches  # noqa
from urdf_parser_py import urdf  # noqa


class ParseException(Exception):
    pass


class TestURDFParser(unittest.TestCase):
    @mock.patch('urdf_parser_py.xml_reflection.on_error',
                mock.Mock(side_effect=ParseException))
    def parse(self, xml):
        return urdf.Robot.from_xml_string(xml)

    def parse_and_compare(self, orig):
        xml = minidom.parseString(orig)
        robot = urdf.Robot.from_xml_string(orig)
        rewritten = minidom.parseString(robot.to_xml_string())
        self.assertTrue(xml_matches(xml, rewritten))

    def xml_and_compare(self, robot, xml):
        robot_xml_string = robot.to_xml_string()
        robot_xml = minidom.parseString(robot_xml_string)
        orig_xml = minidom.parseString(xml)
        self.assertTrue(xml_matches(robot_xml, orig_xml))

    def test_new_transmission(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="simple_trans">
    <type>transmission_interface/SimpleTransmission</type>
    <joint name="foo_joint">
      <hardwareInterface>EffortJointInterface</hardwareInterface>
    </joint>
    <actuator name="foo_motor">
      <mechanicalReduction>50.0</mechanicalReduction>
    </actuator>
  </transmission>
</robot>'''
        self.parse_and_compare(xml)

        robot = urdf.Robot(name = 'test')
        trans = urdf.Transmission(name = 'simple_trans')
        trans.type = 'transmission_interface/SimpleTransmission'
        joint = urdf.TransmissionJoint(name = 'foo_joint')
        joint.add_aggregate('hardwareInterface', 'EffortJointInterface')
        trans.add_aggregate('joint', joint)
        actuator = urdf.Actuator(name = 'foo_motor')
        actuator.mechanicalReduction = 50.0
        trans.add_aggregate('actuator', actuator)
        robot.add_aggregate('transmission', trans)
        self.xml_and_compare(robot, xml)

    def test_new_transmission_multiple_joints(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="simple_trans">
    <type>transmission_interface/SimpleTransmission</type>
    <joint name="foo_joint">
      <hardwareInterface>EffortJointInterface</hardwareInterface>
    </joint>
    <joint name="bar_joint">
      <hardwareInterface>EffortJointInterface</hardwareInterface>
      <hardwareInterface>EffortJointInterface</hardwareInterface>
    </joint>
    <actuator name="foo_motor">
      <mechanicalReduction>50.0</mechanicalReduction>
    </actuator>
  </transmission>
</robot>'''
        self.parse_and_compare(xml)

        robot = urdf.Robot(name = 'test')
        trans = urdf.Transmission(name = 'simple_trans')
        trans.type = 'transmission_interface/SimpleTransmission'
        joint = urdf.TransmissionJoint(name = 'foo_joint')
        joint.add_aggregate('hardwareInterface', 'EffortJointInterface')
        trans.add_aggregate('joint', joint)
        joint = urdf.TransmissionJoint(name = 'bar_joint')
        joint.add_aggregate('hardwareInterface', 'EffortJointInterface')
        joint.add_aggregate('hardwareInterface', 'EffortJointInterface')
        trans.add_aggregate('joint', joint)
        actuator = urdf.Actuator(name = 'foo_motor')
        actuator.mechanicalReduction = 50.0
        trans.add_aggregate('actuator', actuator)
        robot.add_aggregate('transmission', trans)
        self.xml_and_compare(robot, xml)

    def test_new_transmission_multiple_actuators(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="simple_trans">
    <type>transmission_interface/SimpleTransmission</type>
    <joint name="foo_joint">
      <hardwareInterface>EffortJointInterface</hardwareInterface>
    </joint>
    <actuator name="foo_motor">
      <mechanicalReduction>50.0</mechanicalReduction>
    </actuator>
    <actuator name="bar_motor"/>
  </transmission>
</robot>'''
        self.parse_and_compare(xml)

        robot = urdf.Robot(name = 'test')
        trans = urdf.Transmission(name = 'simple_trans')
        trans.type = 'transmission_interface/SimpleTransmission'
        joint = urdf.TransmissionJoint(name = 'foo_joint')
        joint.add_aggregate('hardwareInterface', 'EffortJointInterface')
        trans.add_aggregate('joint', joint)
        actuator = urdf.Actuator(name = 'foo_motor')
        actuator.mechanicalReduction = 50.0
        trans.add_aggregate('actuator', actuator)
        actuator = urdf.Actuator(name = 'bar_motor')
        trans.add_aggregate('actuator', actuator)
        robot.add_aggregate('transmission', trans)
        self.xml_and_compare(robot, xml)

    def test_new_transmission_missing_joint(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="simple_trans">
    <type>transmission_interface/SimpleTransmission</type>
  </transmission>
</robot>'''
        self.assertRaises(Exception, self.parse, xml)

    def test_new_transmission_missing_actuator(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="simple_trans">
    <type>transmission_interface/SimpleTransmission</type>
    <joint name="foo_joint">
      <hardwareInterface>EffortJointInterface</hardwareInterface>
    </joint>
  </transmission>
</robot>'''
        self.assertRaises(Exception, self.parse, xml)

    def test_old_transmission(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="PR2_trans" type="SimpleTransmission">
    <joint name="foo_joint"/>
    <actuator name="foo_motor"/>
    <mechanicalReduction>1.0</mechanicalReduction>
  </transmission>
</robot>'''
        self.parse_and_compare(xml)

        robot = urdf.Robot(name = 'test')
        trans = urdf.PR2Transmission(name = 'PR2_trans', joint = 'foo_joint', actuator = 'foo_motor', type = 'SimpleTransmission', mechanicalReduction = 1.0)
        robot.add_aggregate('transmission', trans)
        self.xml_and_compare(robot, xml)

    def test_link_material_missing_color_and_texture(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <link name="link">
    <visual>
      <geometry>
        <cylinder length="1" radius="1"/>
      </geometry>
      <material name="mat"/>
    </visual>
  </link>
</robot>'''
        self.parse_and_compare(xml)

        robot = urdf.Robot(name = 'test')
        link = urdf.Link(name = 'link',
                         visual = urdf.Visual(geometry = urdf.Cylinder(length = 1, radius = 1),
                                              material = urdf.Material(name = 'mat')))
        robot.add_link(link)
        self.xml_and_compare(robot, xml)

        robot = urdf.Robot(name = 'test')
        link = urdf.Link(name = 'link')
        link.visual = urdf.Visual(geometry = urdf.Cylinder(length = 1, radius = 1),
                                  material = urdf.Material(name = 'mat'))
        robot.add_link(link)
        self.xml_and_compare(robot, xml)

    def test_robot_material(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <material name="mat">
    <color rgba="0.0 0.0 0.0 1.0"/>
  </material>
</robot>'''
        self.parse_and_compare(xml)

        robot = urdf.Robot(name = 'test')
        material = urdf.Material(name = 'mat', color = urdf.Color([0.0, 0.0, 0.0, 1.0]))
        robot.add_aggregate('material', material)
        self.xml_and_compare(robot, xml)

    def test_robot_material_missing_color_and_texture(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <material name="mat"/>
</robot>'''
        self.assertRaises(ParseException, self.parse, xml)


class LinkOriginTestCase(unittest.TestCase):
    @mock.patch('urdf_parser_py.xml_reflection.on_error',
                mock.Mock(side_effect=ParseException))
    def parse(self, xml):
        return urdf.Robot.from_xml_string(xml)

    def test_robot_link_defaults(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <link name="test_link">
    <inertial>
      <mass value="10.0"/>
      <origin/>
    </inertial>
  </link>
</robot>'''
        robot = self.parse(xml)
        origin = robot.links[0].inertial.origin
        self.assertEquals(origin.xyz, [0, 0, 0])
        self.assertEquals(origin.rpy, [0, 0, 0])

    def test_robot_link_defaults_xyz_set(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <link name="test_link">
    <inertial>
      <mass value="10.0"/>
      <origin xyz="1 2 3"/>
    </inertial>
  </link>
</robot>'''
        robot = self.parse(xml)
        origin = robot.links[0].inertial.origin
        self.assertEquals(origin.xyz, [1, 2, 3])
        self.assertEquals(origin.rpy, [0, 0, 0])


if __name__ == '__main__':
    unittest.main()
