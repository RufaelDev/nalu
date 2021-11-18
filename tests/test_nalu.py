#!/usr/bin/env python
"""
   Copyright 2016 beardypig, Copyright 2021 CodeShop B.V. 

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import unittest
#from nalu.nalu import NAL
from tests.test_nal_bytes import *
from src.nalu.nalu import *

class NaluTests(unittest.TestCase):

    sps1 = NAL(sps1_nal)
    sps2 = NAL(sps2_nal)
    sps3 = NAL(sps3_nal)

    if ('chroma_format_idc' in sps1.nal_parameters["sps_rbsp_parameters"].keys()):
        pps1 = NAL(pps1_nal, sps1.nal_parameters["sps_rbsp_parameters"]["chroma_format_idc"])
    else:
        pps1 = NAL(pps1_nal)

    if ('chroma_format_idc' in sps2.nal_parameters["sps_rbsp_parameters"].keys()):
        pps2 = NAL(pps2_nal, sps2.nal_parameters["sps_rbsp_parameters"]["chroma_format_idc"])
    else:
        pps2 = NAL(pps2_nal)

    if ('chroma_format_idc' in sps3.nal_parameters["sps_rbsp_parameters"].keys()):
        pps3 = NAL(pps3_nal, sps3.nal_parameters["sps_rbsp_parameters"]["chroma_format_idc"])
    else:
        pps3 = NAL(pps3_nal)

    def test_nalu_forbidden_header_bit(self):

        self.assertEqual(
            self.sps1.nal_parameters["forbidden_zero_bit"], False

        )
        self.assertEqual(
            self.sps2.nal_parameters["forbidden_zero_bit"], False

        )
        self.assertEqual(
            self.sps3.nal_parameters["forbidden_zero_bit"], False

        )
        self.assertEqual(self.pps1.nal_parameters["forbidden_zero_bit"], False)
        self.assertEqual(self.pps2.nal_parameters["forbidden_zero_bit"], False)

    def test_sps_type(self):
        self.assertEqual(self.sps1.nal_parameters["nal_unit_type"], 7)
        self.assertEqual(self.sps2.nal_parameters["nal_unit_type"], 7)
        self.assertEqual(self.sps3.nal_parameters["nal_unit_type"], 7)
        self.assertEqual(self.pps1.nal_parameters["nal_unit_type"], 8)
        self.assertEqual(self.pps2.nal_parameters["nal_unit_type"], 8)

    def test_sps_nal_ref_idc(self):
        self.assertEqual((self.sps1.nal_parameters["nal_ref_idc"] != 0), True)
        self.assertEqual((self.sps2.nal_parameters["nal_ref_idc"] != 0), True)
        self.assertEqual((self.sps3.nal_parameters["nal_ref_idc"] != 0), True)
        self.assertEqual((self.pps1.nal_parameters["nal_ref_idc"] != 0), True)
        self.assertEqual((self.pps2.nal_parameters["nal_ref_idc"] != 0), True)

    def test_nal_rbsp_exists(self):
        self.assertEqual((len(self.sps1.nal_rbsp_bitstream) > 0), True)
        self.assertEqual((len(self.sps2.nal_rbsp_bitstream) > 0), True)
        self.assertEqual((len(self.sps3.nal_rbsp_bitstream) > 0), True)
        self.assertEqual((len(self.pps1.nal_rbsp_bitstream) > 0), True)
        self.assertEqual((len(self.pps2.nal_rbsp_bitstream) > 0), True)

    def test_sps_rbsp_reserved_zero2bits(self):
        self.assertEqual((self.sps1.nal_parameters["sps_rbsp_parameters"]["reserved_zero_2bits"] == 0), True)
        self.assertEqual((self.sps2.nal_parameters["sps_rbsp_parameters"]["reserved_zero_2bits"] == 0), True)
        self.assertEqual((self.sps3.nal_parameters["sps_rbsp_parameters"]["reserved_zero_2bits"] == 0), True)

    def test_sps_seq_paarameter_set_ID(self):
        allowed = range(32)
        self.assertEqual((self.sps1.nal_parameters["sps_rbsp_parameters"]["seq_parameter_set_id"] in allowed), True)
        self.assertEqual((self.sps2.nal_parameters["sps_rbsp_parameters"]["seq_parameter_set_id"] in allowed), True)
        self.assertEqual((self.sps3.nal_parameters["sps_rbsp_parameters"]["seq_parameter_set_id"] in allowed), True)

    def test_sps_log2_max_frame_num_minus4(self):
        allowed = range(13)
        self.assertEqual((self.sps1.nal_parameters["sps_rbsp_parameters"]["log2_max_frame_num_minus4"] in allowed), True)
        self.assertEqual((self.sps2.nal_parameters["sps_rbsp_parameters"]["log2_max_frame_num_minus4"] in allowed),
                         True)
        self.assertEqual((self.sps3.nal_parameters["sps_rbsp_parameters"]["log2_max_frame_num_minus4"] in allowed),
                         True)

    def test_pic_order_cnt_type(self):
        allowed = range(3)
        self.assertEqual((self.sps1.nal_parameters["sps_rbsp_parameters"]["pic_order_cnt_type"] in allowed),
                         True)
        self.assertEqual((self.sps2.nal_parameters["sps_rbsp_parameters"]["pic_order_cnt_type"] in allowed),
                         True)
        self.assertEqual((self.sps3.nal_parameters["sps_rbsp_parameters"]["pic_order_cnt_type"] in allowed),
                         True)



  

 