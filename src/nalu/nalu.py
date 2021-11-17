from bitstring import BitArray
from src.nalu.naldecoding import *
import pdb

class NAL(object):
    """A class to handle NAL bitstreams. A list of data bytes is required."""

    def __init__(self, nal_data_bytes, sps_chroma_format_idc=0):
        """The initialization function will convert the data bytes to a bistring object."""
        #pdb.set_trace()
        self.nal_bits = BitArray()
        self.nal_rbsp_bitstream = BitArray()
        self.nal_parameters = {}
        self.pointer = 0
        self.num_bytes_rbsp = 0
        #self.nal_bits.clear() #needed between the creation of objects
        #self.nal_rbsp_bitstream.clear()
        self.num_bytes_rbsp = self.get_nal_bitstream(nal_data_bytes,len(nal_data_bytes))

        #get the RBSP data based on the nal unit type
        if(self.nal_parameters["nal_unit_type"] == 7):
            self.nal_parameters["sps_rbsp_parameters"] = self.get_sps_parameters()
        elif (self.nal_parameters["nal_unit_type"] == 8):
            self.nal_parameters["pps_rbsp_parameters"] = self.get_pps_parameters(sps_chroma_format_idc)

    def __str__(self):
        return str(self.nal_parameters)

    def get_nal_bitstream(self, nal_data_bytes, nal_data_byte_length):
        #nal_rbsp_bitstream = BitArray()
        i = 0
        #nal_bits = BitArray()
        while i < nal_data_byte_length:
            self.nal_bits.append(BitArray('uint:8=' + str(nal_data_bytes[i])))
            i += 1
        # nal_bits = BitArray(nal_data_bytes)
        # pdb.set_trace()
        #nal_parameters = {}
        #pointer = 0
        self.nal_parameters["forbidden_zero_bit"] = self.nal_bits[self.pointer]
        self.pointer += 1
        self.nal_parameters["nal_ref_idc"], self.pointer = read_u(self.nal_bits, self.pointer, 2)
        self.nal_parameters["nal_unit_type"], self.pointer = read_u(self.nal_bits, self.pointer, 5)
        num_bytes_rbsp = 0

        nal_unit_header_bytes = 1
        if self.nal_parameters["nal_unit_type"] in [14, 20, 21]:
            if self.nal_parameters["nal_unit_type"] != 21:
                self.nal_parameters["svc_extension_flag"] = self.nal_bits[self.pointer]
                self.pointer += 1
            else:
                self.nal_parameters["avc_3d_extension_flag"] = self.nal_bits[self.pointer]
                self.pointer += 1
            if self.nal_parameters["svc_extension_flag"] == True:
                self.nal_parameters["nal_unit_header_svc_extension"], self.pointer = self.get_nal_unit_header_svc_extension(self.nal_bits,
                                                                                                             self.pointer)
                nal_unit_header_bytes += 3
            elif self.nal_parameters["avc_3d_extension_flag"] == True:
                self.nal_parameters["nal_unit_header_mvc_extension"], self.pointer = self.get_nal_unit_header_3davc_extension(self.nal_bits,
                                                                                                               self.pointer)
                nal_unit_header_bytes += 2
            else:
                self.nal_parameters["nal_unit_header_mvc_extension"], self.pointer = self.get_nal_unit_header_mvc_extension(self.nal_bits,
                                                                                                             self.pointer)
                nal_unit_header_bytes += 3
        i = nal_unit_header_bytes
        while i < nal_data_byte_length:
            next24bits = self.nal_bits[self.pointer:self.pointer + 24]
            next24bitshex = next24bits.hex
            if ((i + 2) < nal_data_byte_length and next24bitshex == 0x000003):
                self.nal_rbsp_bitstream.append(self.nal_bits[self.pointer:self.pointer + 8])
                self.pointer += 8
                num_bytes_rbsp += 1
                self.nal_rbsp_bitstream.append(self.nal_bits[self.pointer:self.pointer + 8])
                self.pointer += 8
                num_bytes_rbsp += 1
                i += 2
                emulation_prevention_three_byte = self.nal_bits[self.pointer: self.pointer + 8]
                self.pointer += 8
            else:
                self.nal_rbsp_bitstream.append(self.nal_bits[self.pointer:self.pointer + 8])
                self.pointer += 8
                num_bytes_rbsp += 1
            i += 1
        # pdb.set_trace()
        return num_bytes_rbsp

    def read_u(self, BitStream, BitStreamPointer, n):
        # pdb.set_trace()
        tempbits = BitArray()
        tempbits = BitStream[BitStreamPointer:(BitStreamPointer + n)]  # pecular to BitArray
        BitStreamPointer += n
        value = tempbits.uint
        return value, BitStreamPointer

    def get_nal_unit_header_svc_extension(self, nal_bits, pointer):
        nal_svc_header = {}
        svc_pointer = pointer

        nal_svc_header["idr_flag"] = nal_bits[svc_pointer]
        svc_pointer += 1
        nal_svc_header["priority_id"], svc_pointer = read_u(nal_bits, svc_pointer, 6)
        nal_svc_header["no_inter_layer_pred_flag"] = nal_bits[svc_pointer]
        svc_pointer += 1
        nal_svc_header["dependency_id"], svc_pointer = read_u(nal_bits, svc_pointer, 3)
        nal_svc_header["quality_id"], svc_pointer = read_u(nal_bits, svc_pointer, 4)
        nal_svc_header["temporal_id"], svc_pointer = read_u(nal_bits, svc_pointer, 3)
        nal_svc_header["use_ref_base_pic_flag"] = nal_bits[svc_pointer]
        svc_pointer += 1
        nal_svc_header["discardable_flag"] = nal_bits[svc_pointer]
        svc_pointer += 1
        nal_svc_header["output_flag"] = nal_bits[svc_pointer]
        svc_pointer += 1
        nal_svc_header["reserved_three_2bits"], svc_pointer = read_u(nal_bits, svc_pointer, 2)
        return nal_svc_header, svc_pointer

    def get_nal_unit_header_3davc_extension(self, nal_bits, pointer):
        nal_3davc_header = {}
        d3_pointer = pointer

        nal_3davc_header["view_idx"], d3_pointer = read_u(nal_bits, d3_pointer, 8)
        nal_3davc_header["depth_flag"] = self.nal_bits[d3_pointer]
        d3_pointer += 1
        nal_3davc_header["non_idr_flag"] = self.nal_bits[d3_pointer]
        d3_pointer += 1
        nal_3davc_header["temporal_id"], d3_pointer = read_u(nal_bits, d3_pointer, 3)
        nal_3davc_header["anchor_pic_flag"] = nal_bits[d3_pointer]
        d3_pointer += 1
        nal_3davc_header["inter_view_flag"] = nal_bits[d3_pointer]
        d3_pointer += 1
        return nal_3davc_header, d3_pointer

    def get_nal_unit_header_mvc_extension(self, nal_bits, pointer):
        nal_mvc_header = {}
        mvc_pointer = pointer

        nal_mvc_header["non_idr_flag"] = nal_bits[mvc_pointer]
        mvc_pointer += 1
        nal_mvc_header["priority_id"], mvc_pointer = read_u(nal_bits, mvc_pointer, 6)
        nal_mvc_header["view_id"], mvc_pointer = read_u(nal_bits, mvc_pointer, 10)
        nal_mvc_header["temporal_id"], mvc_pointer = read_u(nal_bits, mvc_pointer, 3)
        nal_mvc_header["anchor_pic_flag"] = nal_bits[mvc_pointer]
        mvc_pointer += 1
        nal_mvc_header["inter_view_flag"] = nal_bits[mvc_pointer]
        mvc_pointer += 1
        nal_mvc_header["reserved_one_bit"] = nal_bits[mvc_pointer]
        mvc_pointer += 1
        return nal_mvc_header, mvc_pointer

    def get_scaling_list(self, SizeOfScalingList, BitStream, BitStreamPointer):
        LastScale = 8
        NextScale = 8
        ScalingList = []
        j = 0
        UseDefualtScalingMatrixFlag = False
        while j < SizeOfScalingList:
            if NextScale != 0:
                CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(BitStream, BitStreamPointer)
                delta_scale = get_se(CodeNum)
                NextScale = (LastScale + delta_scale + 256) % 256
                if (j == 0) and NextScale == 0:
                    UseDefualtScalingMatrixFlag = True
                else:
                    UseDefualtScalingMatrixFlag = False
            if NextScale == 0:
                ScalingList.append(LastScale)
            else:
                ScalingList.append(NextScale)
            LastScale = ScalingList[j]
            j += 1

        return ScalingList, UseDefualtScalingMatrixFlag, BitStreamPointer

    def get_hrd_parameters(self, BitStream, BitStreamPointer):
        hrd_parameters = {}
        BitStreamLength = len(BitStream)
        if (BitStreamLength < BitStreamPointer):
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(BitStream, BitStreamPointer)
            hrd_parameters["cpb_cnt_minus1"] = CodeNum
            if (BitStreamLength < BitStreamPointer):
                hrd_parameters["bit_rate_scale"], BitStreamPointer = read_u(BitStream, BitStreamPointer, 4)
                if (BitStreamLength < BitStreamPointer):
                    hrd_parameters["cpb_size_scale"], BitStreamPointer = read_u(BitStream, BitStreamPointer, 4)
                    SchedSeIIdx = 0
                    hrd_parameters["bit_rate_value_minus1"] = {}
                    hrd_parameters["cpb_size_value_minus1"] = {}
                    hrd_parameters["cbr_flag"] = {}

                    while SchedSeIIdx <= hrd_parameters["cpb_cnt_minus1"]:
                        if (BitStreamPointer < BitStreamLength):
                            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(BitStream,
                                                                                              BitStreamPointer)
                            hrd_parameters["bit_rate_value_minus1"][SchedSeIIdx] = CodeNum
                            if (BitStreamPointer < BitStreamLength):
                                CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(BitStream,
                                                                                                  BitStreamPointer)
                                # hrd_parameters["cpb_size_value_minus1"] = {SchedSeIIdx: CodeNum}
                                hrd_parameters["cpb_size_value_minus1"][SchedSeIIdx] = CodeNum
                                if (BitStreamPointer < BitStreamLength):
                                    # hrd_parameters["cbr_flag"] = {SchedSeIIdx: BitStream[BitStreamPointer]}
                                    hrd_parameters["cbr_flag"][SchedSeIIdx] = BitStream[BitStreamPointer]
                                    BitStreamPointer += 1

                        SchedSeIIdx += 1
                    # pdb.set_trace()
                    if (BitStreamPointer < BitStreamLength):
                        hrd_parameters["initial_cpb_removal_delay_length_minus1"], BitStreamPointer = read_u(BitStream,
                                                                                                             BitStreamPointer,
                                                                                                             5)
                        if (BitStreamPointer < BitStreamLength):
                            hrd_parameters["cpb_removal_delay_length_minus1"], BitStreamPointer = read_u(BitStream,
                                                                                                         BitStreamPointer,
                                                                                                         5)
                            if (BitStreamPointer < BitStreamLength):
                                hrd_parameters["dpb_output_delay_length_minus1"], BitStreamPointer = read_u(BitStream,
                                                                                                            BitStreamPointer,
                                                                                                            5)
                                if (BitStreamPointer < BitStreamLength):
                                    hrd_parameters["time_offset_length"], BitStreamPointer = read_u(BitStream,
                                                                                                    BitStreamPointer, 5)

        return hrd_parameters, BitStreamPointer

    def get_vui_parameters(self, BitStream, BitStreamPointer):
        vui_parameters = {}
        BitStreamLength = len(BitStream) #found some vui parameters may not be present when signaled, needed to test when there are no more bits.
        vui_parameters["aspect_ratio_info_present_flag"] = BitStream[BitStreamPointer]
        BitStreamPointer += 1

        if vui_parameters["aspect_ratio_info_present_flag"] == True:

            vui_parameters["aspect_ratio_idc"], BitStreamPointer = read_u(BitStream, BitStreamPointer, 8)

            # Extended_SAR = 255
            if (vui_parameters["aspect_ratio_idc"] == 255):
                vui_parameters["sar_width"], BitStreamPointer = read_u(BitStream, BitStreamPointer, 16)

                vui_parameters["sar_height"], BitStreamPointer = read_u(BitStream, BitStreamPointer, 16)
        vui_parameters["overscan_info_present_flag"] = BitStream[BitStreamPointer]
        BitStreamPointer += 1
        if vui_parameters["overscan_info_present_flag"] == True:
            vui_parameters["overscan_appropriate_flag"] = BitStream[BitStreamPointer]
            BitStreamPointer += 1
        vui_parameters["video_signal_type_present_flag"] = BitStream[BitStreamPointer]
        BitStreamPointer += 1

        if vui_parameters["video_signal_type_present_flag"] == True:

            vui_parameters["video_format"], BitStreamPointer = read_u(BitStream, BitStreamPointer, 3)

            vui_parameters["video_full_range_flag"] = BitStream[BitStreamPointer]
            BitStreamPointer += 1
            vui_parameters["colour_description_present_flag"] = BitStream[BitStreamPointer]
            BitStreamPointer += 1
            if vui_parameters["colour_description_present_flag"] == True:
                vui_parameters["colour_primaries"], BitStreamPointer = read_u(BitStream, BitStreamPointer, 8)

                vui_parameters["transfer_characteristics"], BitStreamPointer = read_u(BitStream, BitStreamPointer, 8)

                vui_parameters["matrix_coefficients"], BitStreamPointer = read_u(BitStream, BitStreamPointer, 8)

        vui_parameters["chroma_loc_info_present_flag"] = BitStream[BitStreamPointer]
        BitStreamPointer += 1
        if vui_parameters["chroma_loc_info_present_flag"] == True:
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(BitStream, BitStreamPointer)
            vui_parameters["chroma_sample_loc_type_top_field"] = CodeNum
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(BitStream, BitStreamPointer)
            vui_parameters["chroma_sample_loc_type_bottom_field"] = CodeNum
        vui_parameters["timing_info_present_flag"] = BitStream[BitStreamPointer]
        BitStreamPointer += 1

        if vui_parameters["timing_info_present_flag"] == True:
            vui_parameters["num_units_in_tick"], BitStreamPointer = read_u(BitStream, BitStreamPointer, 32)
            vui_parameters["time_scale"], BitStreamPointer = read_u(BitStream, BitStreamPointer, 32)
            vui_parameters["fixed_frame_rate_flag"] = BitStream[BitStreamPointer]
            BitStreamPointer += 1
        vui_parameters["nal_hrd_parameters_present_flag"] = BitStream[BitStreamPointer]
        BitStreamPointer += 1
        if (BitStreamLength < BitStreamPointer):
            if vui_parameters["nal_hrd_parameters_present_flag"] == True:
                vui_parameters["hrd_parameters"], BitStreamPointer = self.get_hrd_parameters(BitStream, BitStreamPointer)
            if (BitStreamLength < BitStreamPointer):
                vui_parameters["vcl_hrd_parameters_present_flag"] = BitStream[BitStreamPointer]
                BitStreamPointer += 1
                if (BitStreamLength < BitStreamPointer):
                    if vui_parameters["vcl_hrd_parameters_present_flag"] == True:
                        vui_parameters["hrd_parameters"], BitStreamPointer = self.get_hrd_parameters(BitStream,
                                                                                                BitStreamPointer)
                        pdb.set_trace()
                    if (BitStreamLength < BitStreamPointer):
                        if (vui_parameters["nal_hrd_parameters_present_flag"] == True) or (
                                vui_parameters["vcl_hrd_parameters_present_flag"] == True):
                            vui_parameters["low_delay_hrd_flag"] = BitStream[BitStreamPointer]
                            BitStreamPointer += 1
                            if (BitStreamLength < BitStreamPointer):
                                vui_parameters["pic_struct_present_flag"] = BitStream[BitStreamPointer]
                                BitStreamPointer += 1
                                if (BitStreamLength < BitStreamPointer):
                                    vui_parameters["bitstream_restriction_flag"] = BitStream[BitStreamPointer]
                                    BitStreamPointer += 1
                                    if vui_parameters["bitstream_restriction_flag"] == True:
                                        if (BitStreamLength < BitStreamPointer):
                                            vui_parameters["motion_vectors_over_pic_boundaries_flag"] = BitStream[
                                                BitStreamPointer]
                                            BitStreamPointer += 1
                                            if (BitStreamPointer < BitStreamLength):
                                                CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(
                                                    BitStream, BitStreamPointer)
                                                vui_parameters["max_bytes_per_pic_denom"] = CodeNum
                                                if (BitStreamPointer < BitStreamLength):
                                                    CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(
                                                        BitStream, BitStreamPointer)
                                                    vui_parameters["max_bits_per_mb_denom"] = CodeNum
                                                    if (BitStreamPointer < BitStreamLength):
                                                        CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(
                                                            BitStream, BitStreamPointer)
                                                        vui_parameters["log2_max_mv_length_horizontal"] = CodeNum
                                                        if (BitStreamPointer < BitStreamLength):
                                                            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(
                                                                BitStream, BitStreamPointer)
                                                            vui_parameters["log2_max_mv_length_vertical"] = CodeNum
                                                            if (BitStreamPointer < BitStreamLength):
                                                                CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(
                                                                    BitStream, BitStreamPointer)
                                                                vui_parameters["max_num_reorder_frames"] = CodeNum
                                                                if (BitStreamPointer < BitStreamLength):
                                                                    CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(
                                                                        BitStream, BitStreamPointer)
                                                                    vui_parameters["max_dec_frame_buffering"] = CodeNum

        return vui_parameters, BitStreamPointer

    def get_rbsp_trailing_bits(self, BitStream, BitStreamPointer):
        rbsp_stop_one_bit = BitStream[BitStreamPointer]
        BitStreamPointer += 1
        while byte_aligned(BitStreamPointer) == False:
            rbsp_alignment_zero_bit = BitStream[BitStreamPointer]
            BitStreamPointer += 1
        return BitStreamPointer

    def get_sps_parameters(self):
        BitStreamPointer = 0
        sps_rbsp_data = {}
        sps_rbsp_data["profile_idc"], BitStreamPointer = read_u(self.nal_rbsp_bitstream, BitStreamPointer, 8)
        sps_rbsp_data["constraint_set0_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]

        BitStreamPointer += 1
        sps_rbsp_data["constraint_set1_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]

        BitStreamPointer += 1
        sps_rbsp_data["constraint_set2_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]

        BitStreamPointer += 1
        sps_rbsp_data["constraint_set3_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
        BitStreamPointer += 1
        sps_rbsp_data["constraint_set4_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
        BitStreamPointer += 1
        sps_rbsp_data["constraint_set5_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
        BitStreamPointer += 1
        # pdb.set_trace()
        sps_rbsp_data["reserved_zero_2bits"], BitStreamPointer = read_u(self.nal_rbsp_bitstream, BitStreamPointer, 2)
        # pdb.set_trace()
        sps_rbsp_data["level_idc"], BitStreamPointer = read_u(self.nal_rbsp_bitstream, BitStreamPointer, 8)
        # BitStreamPointer = 16

        CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
        sps_rbsp_data["seq_parameter_set_id"] = CodeNum

        chroma_format_profiles = [100, 110, 122, 244, 44, 83, 86, 118, 128, 138, 139, 134, 135]
        if sps_rbsp_data["profile_idc"] in chroma_format_profiles:
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            sps_rbsp_data["chroma_format_idc"] = CodeNum
            if sps_rbsp_data["chroma_format_idc"] == 3:
                sps_rbsp_data["separate_colour_plane_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
                BitStreamPointer += 1  # point to the next bit
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            sps_rbsp_data["bit_depth_luma_minus8"] = CodeNum
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            sps_rbsp_data["bit_depth_chrom_minus8"] = CodeNum
            sps_rbsp_data["qpprime_y_zero_transform_bypass_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
            BitStreamPointer += 1
            sps_rbsp_data["seq_scaling_matrix_present_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
            BitStreamPointer += 1
            if sps_rbsp_data["seq_scaling_matrix_present_flag"] == True:
                if sps_rbsp_data["chroma_format_idc"] != 3:
                    limit = 8
                else:
                    limit = 12
                i = 0
                sps_rbsp_data["seq_scaling_list_present_flag"] = []
                while i < limit:
                    sps_rbsp_data["seq_scaling_list_present_flag"].append(self.nal_rbsp_bitstream[BitStreamPointer])
                    BitStreamPointer += 1
                    sps_rbsp_data["ScalingList4x4"] = []
                    sps_rbsp_data["UseDefaultScalingMatrix4x4Flag"] = []
                    sps_rbsp_data["ScalingList8x8"] = []
                    sps_rbsp_data["UseDefaultScalingMatrix8x8Flag"] = []
                    if sps_rbsp_data["seq_scaling_list_present_flag"][i] == True:
                        if i < 6:
                            # scaling_list
                            scaling_list, use_defualtmatrix, BitStreamPointer = self.get_scaling_list(16,
                                                                                                 self.nal_rbsp_bitstream,
                                                                                                 BitStreamPointer)
                            sps_rbsp_data["ScalingList4x4"].append(scaling_list)
                            sps_rbsp_data["UseDefaultScalingMatrix4x4Flag"].append(use_defualtmatrix)
                        else:
                            # scaling_list
                            scaling_list, use_defualtmatrix, BitStreamPointer = self.get_scaling_list(64,
                                                                                                 self.nal_rbsp_bitstream,
                                                                                                 BitStreamPointer)
                            sps_rbsp_data["ScalingList8x8"].append(scaling_list)
                            sps_rbsp_data["UseDefaultScalingMatrix8x8Flag"].append(use_defualtmatrix)
                    i += 1
        CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
        sps_rbsp_data["log2_max_frame_num_minus4"] = CodeNum
        CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
        sps_rbsp_data["pic_order_cnt_type"] = CodeNum

        if sps_rbsp_data["pic_order_cnt_type"] == 0:
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            sps_rbsp_data["log2_max_pic_order_cnt_lsb_minus4"] = CodeNum
        elif sps_rbsp_data["pic_order_cnt_type"] == 1:
            sps_rbsp_data["delta_pic_order_always_zero_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
            BitStreamPointer += 1
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            sps_rbsp_data["offset_for_non_ref_pic"] = get_se(CodeNum)
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            sps_rbsp_data["offset_for_top_to_bottom_field"] = get_se(CodeNum)
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            sps_rbsp_data["num_ref_frames_in_pic_order_cnt_cycle"] = CodeNum
            i = 0
            sps_rbsp_data["offset_for_ref_frame"] = []
            while i < sps_rbsp_data["num_ref_frames_in_pic_order_cnt_cycle"]:
                CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
                sps_rbsp_data["offset_for_ref_frame"].append(get_se(CodeNum))
                i += 1
        CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
        sps_rbsp_data["max_num_ref_frames"] = CodeNum
        sps_rbsp_data["gaps_in_frame_num_value_allowed_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
        BitStreamPointer += 1
        CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
        sps_rbsp_data["pic_width_in_mbs_minus1"] = CodeNum
        CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
        sps_rbsp_data["pic_height_in_map_units_minus1"] = CodeNum
        sps_rbsp_data["frame_mbs_only_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
        BitStreamPointer += 1

        if sps_rbsp_data["frame_mbs_only_flag"] == False:
            sps_rbsp_data["mb_adaptive_frame_field_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
            BitStreamPointer += 1
        sps_rbsp_data["direct_8x8_inference_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
        BitStreamPointer += 1
        sps_rbsp_data["frame_cropping_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
        BitStreamPointer += 1

        if sps_rbsp_data["frame_cropping_flag"] == True:
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            sps_rbsp_data["frame_crop_left_offset"] = CodeNum
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            sps_rbsp_data["frame_crop_right_offset"] = CodeNum
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            sps_rbsp_data["frame_crop_top_offset"] = CodeNum
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            sps_rbsp_data["frame_crop_bottom_offset"] = CodeNum

        sps_rbsp_data["vui_parameters_present_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
        BitStreamPointer += 1
        sps_rbsp_data["eers"] = {}

        if sps_rbsp_data["vui_parameters_present_flag"] == True:
            # vui_parameters
            #pdb.set_trace()
            sps_rbsp_data["vui_parameters"], BitStreamPointer = self.get_vui_parameters(self.nal_rbsp_bitstream, BitStreamPointer)

        if (BitStreamPointer < len(self.nal_rbsp_bitstream)):
            BitStreamPointer = self.get_rbsp_trailing_bits(self.nal_rbsp_bitstream, BitStreamPointer)

        return sps_rbsp_data

    def get_pps_parameters(self, sps_chroma_format_idc):
        BitStreamPointer = 0
        pps_rbsp_data = {}
        CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
        pps_rbsp_data["pic_parameter_set_id"] = CodeNum
        CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
        pps_rbsp_data["seq_parameter_set_id"] = CodeNum
        pps_rbsp_data["entropy_coding_mode_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
        BitStreamPointer += 1
        pps_rbsp_data["bottom_field_pic_order_in_frame_present_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
        BitStreamPointer += 1
        CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
        pps_rbsp_data["num_slice_groups_minus1"] = CodeNum
        if pps_rbsp_data["num_slice_groups_minus1"] > 0:
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            pps_rbsp_data["slice_group_map_type"] = CodeNum
            if pps_rbsp_data["slice_group_map_type"] == 0:
                iGroup = 0
                pps_rbsp_data["run_length_minus1"] = []
                while iGroup <= pps_rbsp_data["num_slice_groups_minus1"]:
                    CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
                    pps_rbsp_data["run_length_minus1"].append(CodeNum)
                    iGroup += 1
            elif pps_rbsp_data["slice_group_map_type"] == 2:
                iGroup = 0
                pps_rbsp_data["top_left"] = []
                pps_rbsp_data["bottom_right"] = []
                while iGroup < pps_rbsp_data["num_slice_groups_minus1"]:
                    CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
                    pps_rbsp_data["top_left"].append(CodeNum)
                    CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
                    pps_rbsp_data["bottom_right"].append(CodeNum)
                    iGroup += 1
            elif pps_rbsp_data["slice_group_map_type"] in [3, 4, 5]:
                pps_rbsp_data["slice_group_change_direction_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
                BitStreamPointer += 1
                CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
                pps_rbsp_data["slice_group_change_rate_minus1"] = CodeNum
            elif pps_rbsp_data["slice_group_map_type"] == 6:
                CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
                pps_rbsp_data["pic_size_in_map_units_minus1"] = CodeNum
                pps_rbsp_data["slice_group_id"] = []
                i = 0
                v_length = math.ceil(math.log2(pps_rbsp_data["num_slice_groups_minus1"] + 1))
                while i <= pps_rbsp_data["pic_size_in_map_units_minus1"]:
                    pps_rbsp_data["slice_group_id "], BitStreamPointer = read_u(self.nal_rbsp_bitstream, BitStreamPointer, v_length)
                    i += 1
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            pps_rbsp_data["num_ref_idx_10_default_active_minus1"] = CodeNum
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            pps_rbsp_data["num_ref_idx_11_default_active_minus1"] = CodeNum

            pps_rbsp_data["weighted_pred_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
            BitStreamPointer += 1
            pps_rbsp_data["weighted_bipred_idc"], BitStreamPointer = read_u(self.nal_rbsp_bitstream, BitStreamPointer, 2)
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            pps_rbsp_data["pic_init_qp_minus26"] = get_se(CodeNum)
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            pps_rbsp_data["pic_init_qs_minus26"] = get_se(CodeNum)
            CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
            pps_rbsp_data["chroma_qp_index_offset"] = get_se(CodeNum)
            pps_rbsp_data["deblocking_filter_control_present_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
            BitStreamPointer += 1
            ### if more RBSP data to follow.
            if self.nal_rbsp_bitstream.length > BitStreamPointer:
                pps_rbsp_data["transform_8x8_mode_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
                BitStreamPointer += 1
                pps_rbsp_data["pic_scaling_matrix_present_flag"] = self.nal_rbsp_bitstream[BitStreamPointer]
                BitStreamPointer += 1
                if pps_rbsp_data["pic_scaling_matrix_present_flag"] == True:
                    i = 0
                    pps_rbsp_data["pic_scaling_list_present_flag"] = []
                    if (sps_chroma_format_idc != 3):
                        limit = 6 + (2 * int(pps_rbsp_data["transform_8x8_mode_flag"]))
                    else:
                        limit = 6 + (6 * int(pps_rbsp_data["transform_8x8_mode_flag"]))
                    while i < limit:
                        pps_rbsp_data["pic_scaling_list_present_flag"].append(self.nal_rbsp_bitstream[BitStreamPointer])
                        BitStreamPointer += 1
                        pps_rbsp_data["ScalingList4x4"] = []
                        pps_rbsp_data["UseDefaultScalingMatrix4x4Flag"] = []
                        pps_rbsp_data["ScalingList8x8"] = []
                        pps_rbsp_data["UseDefaultScalingMatrix8x8Flag"] = []
                        if (pps_rbsp_data["pic_scaling_list_present_flag"][i]):
                            if i < 6:
                                scaling_list, use_defualtmatrix, BitStreamPointer = self.get_scaling_list(16,
                                                                                                     self.nal_rbsp_bitstream,
                                                                                                     BitStreamPointer)
                                pps_rbsp_data["ScalingList4x4"].append(scaling_list)
                                pps_rbsp_data["UseDefaultScalingMatrix4x4Flag"] = use_defualtmatrix
                            else:
                                scaling_list, use_defualtmatrix, BitStreamPointer = self.get_scaling_list(16,
                                                                                                     self.nal_rbsp_bitstream,
                                                                                                     BitStreamPointer)
                                pps_rbsp_data["ScalingList8x8"].append(scaling_list)
                                pps_rbsp_data["UseDefaultScalingMatrix8x8Flag"] = use_defualtmatrix

                        i += 1
                    CodeNum, BitStreamPointer, NumLeadZeros, RequiredBits = decode_ue(self.nal_rbsp_bitstream, BitStreamPointer)
                    pps_rbsp_data["second_chroma_qp_index_offset"] = get_se(CodeNum)
            if (BitStreamPointer < len(self.nal_rbsp_bitstream)):
                BitStreamPointer = self.get_rbsp_trailing_bits(self.nal_rbsp_bitstream, BitStreamPointer)
        return pps_rbsp_data