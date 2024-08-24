#!/usr/bin/env python3

import struct
from PIL import Image
from collections import namedtuple


class GooHeaderInfo:
    data_structure = (
        '4s:version:str',
        '8s:magic_tag:',
        '32s:software_info:str',
        '24s:software_version:str',
        '24s:file_time:str',
        '32s:printer_name:str',
        '32s:printer_type:str',
        '32s:profile_name:str',
        'H:aa_level:',
        'H:grey_level:',
        'H:blur_level:',
        '26912s:preview_image_small:rgb16',
        '2s:delimiter_1:',
        '168200s:preview_image_big:rgb16',
        '2s:delimiter_2:',
        'I:total_layers:#',
        'H:x_resolution:px',
        'H:y_resolution:px',
        'B:x_mirror:',
        'B:y_mirror:',
        'f:x_platform_size:mm',
        'f:y_platform_size:mm',
        'f:z_platform_size:mm',
        'f:layer_thickness:mm',
        'f:common_exposure_time:s',
        'B:exposure_dely_mode:',
        'f:turn_off_time:s',
        'f:bottom_before_lift_time:s',
        'f:bottom_after_lift_time:s',
        'f:bottom_after_retract_time:s',
        'f:before_lift_time:s',
        'f:after_lift_time:s',
        'f:after_retract_time:s',
        'f:bottom_exposure_time:s',
        'I:bottom_layers:#',
        'f:bottom_lift_distance:',
        'f:bottom_lift_speed:mm/min',
        'f:lift_distance:mm',
        'f:lift_speed:mm/min',
        'f:bottom_retract_distance:mm',
        'f:bottom_retract_speed:mm/min',
        'f:retract_distance:mm',
        'f:retract_speed:mm/min',
        'f:bottom_second_lift_distance:mm',
        'f:bottom_second_lift_speed:mm/min',
        'f:second_lift_distance:mm',
        'f:second_lift_speed:mm/min',
        'f:bottom_second_retract_distance:mm',
        'f:bottom_second_retract_speed:mm/min',
        'f:second_retract_distance:mm',
        'f:second_retract_speed:mm/min',
        'H:bottom_light_pwm:/255',
        'H:light_pwm:/255',
        'B:advance_mode:',
        'I:printing_time:s',
        'f:total_volume:mm3',
        'f:total_weight:g',
        'f:total_price:',
        '8s:price_unit:',
        'I:offset_layer_content:@',
        'B:gray_scale_level:/255',
        'H:transition_layers:#',
    )

    @staticmethod
    def tuple_type():
        return namedtuple(
            'GooHeaderInfoData',
            (d.split(':')[1] for d in GooHeaderInfo.data_structure)
        )

    @staticmethod
    def structure_str():
        return '>' + ''.join(
            (d.split(':')[0] for d in GooHeaderInfo.data_structure)
        )

    @staticmethod
    def size():
        return struct.calcsize(GooHeaderInfo.structure_str())

    @staticmethod
    def parse(d):
        structure = GooHeaderInfo.structure_str()
        return GooHeaderInfo.tuple_type()._make(
            struct.unpack(structure, d[:struct.calcsize(structure)])
        )

    @staticmethod
    def units():
        return GooHeaderInfo.tuple_type()._make(
            (d.split(':')[2] for d in GooHeaderInfo.data_structure)
        )


class GooLayerInfo:
    data_structure = (
        'H:pause_flag:',
        'f:pause_position_z:mm',
        'f:layer_position_z:mm',
        'f:layer_exposure_time:s',
        'f:layer_off_time:s',
        'f:before_lift_time:s',
        'f:after_lift_time:s',
        'f:after_retract_time:s',
        'f:lift_distance:mm',
        'f:lift_speed:mm/min',
        'f:second_lift_distance:mm',
        'f:second_lift_speed:mm/min',
        'f:retract_distance:mm',
        'f:retract_speed:mm/min',
        'f:second_retract_distance:mm',
        'f:second_retract_speed:mm/min',
        'H:light_pwm:/255',
        '2s:delimiter_1:',
        'I:data_size:',
    )

    @staticmethod
    def tuple_type():
        return namedtuple(
            'GooLayerInfoData',
            (d.split(':')[1] for d in GooLayerInfo.data_structure)
        )

    @staticmethod
    def structure_str():
        return '>' + ''.join(
            (d.split(':')[0] for d in GooLayerInfo.data_structure)
        )

    @staticmethod
    def size():
        return struct.calcsize(GooLayerInfo.structure_str())

    @staticmethod
    def parse(d):
        structure = GooLayerInfo.structure_str()
        return GooLayerInfo.tuple_type()._make(
            struct.unpack(structure, d[:struct.calcsize(structure)])
        )

    @staticmethod
    def units():
        return GooLayerInfo.tuple_type()._make(
            (d.split(':')[2] for d in GooLayerInfo.data_structure)
        )


class GooReader:
    @staticmethod
    def rgb565_to_pil(size, data):
        sz = size[0] * size[1]
        rgb = [0] * (3 * sz)
        for i, v in enumerate(struct.unpack('>'+str(sz)+'H', data)):
            rgb[3*i+0] = (v & 0xF800) >> 8
            rgb[3*i+1] = (v & 0x07E0) >> 3
            rgb[3*i+2] = (v & 0x001F) << 3
        return Image.frombuffer('RGB', size, bytearray(rgb))

    @staticmethod
    def rle_to_pil(size, data):
        img_buffer = [0] * (size[0] * size[1])
        h = 1  # Initial charater U ignored in input data
        i = 0  # Set at beginning of image buffer
        value = 0

        h_end = len(data) - 1  # Final 1-byte checksum ignored
        while h < h_end:
            chunk_type = (data[h] >> 6) & 0x3
            chunk_len_type = (data[h] >> 4) & 0x3
            chunk_len = 0
            dh = 0

            if chunk_type == 0:
                value = 0
            elif chunk_type == 1:
                value = data[h+1]
                dh = 1
            elif chunk_type == 2:
                dv = data[h] & 0x0f
                if chunk_len_type & 1:
                    chunk_len = data[h+1]
                    dh = 1
                else:
                    chunk_len = 1
                if chunk_len_type & 2:
                    value += dv
                    print('rle_parser: unsure +dv')
                else:
                    value -= dv
                    print('rle_parser: unsure -dv')
            else:
                value = 0xff

            if chunk_len == 0:
                if chunk_len_type == 0:
                    chunk_len = (data[h] & 0x0f)
                elif chunk_len_type == 1:
                    chunk_len = (data[h] & 0x0f) + \
                                (data[h+dh+1] << 4)
                    dh += 1
                elif chunk_len_type == 2:
                    chunk_len = (data[h] & 0x0f) + \
                                (data[h+dh+2] << 4) + \
                                (data[h+dh+1] << (4+8))
                    dh += 2
                else:
                    chunk_len = (data[h] & 0x0f) + \
                                (data[h+dh+3] << 4) + \
                                (data[h+dh+2] << (4+8)) + \
                                (data[h+dh+1] << (4+16))
                    dh += 3

            if value != 0:  # Image already initialized at 0
                img_buffer[i:i+chunk_len] = [value] * chunk_len
            i += chunk_len

            h += dh + 1

        return Image.frombuffer('L', size, bytearray(img_buffer))

    def __init__(self, f):
        self.f = f
        self.f.seek(0)
        self.header_info = GooHeaderInfo.parse(
            self.f.read(GooHeaderInfo.size())
        )
        self.go_first_layer()

    def decode_preview_small(self):
        return GooReader.rgb565_to_pil(
            (116, 116),
            self.header_info.preview_image_small
        )

    def decode_preview_big(self):
        return GooReader.rgb565_to_pil(
            (290, 290),
            self.header_info.preview_image_big
        )

    def go_first_layer(self):
        self.layer_offset = self.header_info.offset_layer_content
        self.f.seek(self.layer_offset)
        self.layer_info = GooLayerInfo.parse(self.f.read(GooLayerInfo.size()))
        self.layer_nb = 1

    def go_next_layer(self):
        if self.layer_nb >= self.header_info.total_layers:
            return False
        self.layer_offset += GooLayerInfo.size() + self.layer_info.data_size + 2
        self.f.seek(self.layer_offset)
        self.layer_info = GooLayerInfo.parse(self.f.read(GooLayerInfo.size()))
        self.layer_nb += 1
        return True

    def decode_layer_image(self):
        self.f.seek(self.layer_offset + GooLayerInfo.size())
        return GooReader.rle_to_pil(
            (self.header_info.x_resolution, self.header_info.y_resolution),
            self.f.read(self.layer_info.data_size)
        )


if __name__ == "__main__":
    def print_fields(clazz, ntuple, fs=None, prefix=''):
        cut = not fs
        units = clazz.units()
        for i, f in enumerate(ntuple._fields):
            if fs and f not in fs:
                continue

            u = getattr(units, f, '')
            v = getattr(ntuple, f)

            if u == 'str':
                v = v.split(b'\0')[0].decode('utf-8')
                u = ''

            if cut and type(v) is bytes and len(v) > 25:
                v = repr(v[:25]) + ' […]'
            else:
                v = repr(v)

            print(f'{prefix} {i:3} | {f:30} | {v} {u}')

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='File to analyze')

    parser.add_argument('-hi', '--header-info', action='store_true', help='Print header info')
    parser.add_argument('-hp', '--header-parameter', nargs='+', default=[], help='Header parameters to print')

    parser.add_argument('-li', '--layer-info', action='store_true', help='Print layer info')
    parser.add_argument('-lp', '--layer-parameter', nargs='+', default=[], help='Layers parameters to print')

    parser.add_argument('-ps', '--preview-small', help='Extract small image preview (file name)')
    parser.add_argument('-pb', '--preview-big', help='Extract big image preview (file name)')

    parser.add_argument('-lip', '--layer-image-prefix', help='Prefix for layer images')

    parser.add_argument('-l', '--layers', help='Layers to consider (ex: 1-5, 22, 30-31)')
    args = parser.parse_args()

    with open(args.filename, 'rb') as f:
        goo = GooReader(f)
        if args.header_info or args.header_parameter:
            print('==== HEADER ====')
            print_fields(GooHeaderInfo, goo.header_info, args.header_parameter)

        if args.preview_small:
            img = goo.decode_preview_small()
            img.save(args.preview_small)

        if args.preview_big:
            img = goo.decode_preview_big()
            img.save(args.preview_big)

        if args.layers or args.layer_info or args.layer_parameter or args.layer_image_prefix:
            layers = tuple(tuple(map(int, y.split('-'))) for y in args.layers.split(',')) if args.layers else tuple()

            def is_layer_enabled(layer):
                if not layers:
                    return True
                for r in layers:
                    if len(r) == 1:
                        if layer == r[0]:
                            return True
                    else:
                        if layer >= r[0] and layer <= r[1]:
                            return True
                return False

            def layer_process(layer_nb):
                if not is_layer_enabled(layer_nb):
                    return

                p = f'L{layer_nb:<5} |' if args.layer_parameter else ''
                if not args.layer_parameter:
                    print(f'==== LAYER {layer_nb} ====')
                if args.layer_info or args.layer_parameter:
                    print_fields(GooLayerInfo, goo.layer_info, args.layer_parameter, prefix=p)

                if args.layer_image_prefix:
                    print('Export image')
                    img = goo.decode_layer_image()
                    img.save(f'{args.layer_image_prefix}{layer_nb:05}.png')

            layer_process(goo.layer_nb)
            while goo.go_next_layer():
                layer_process(goo.layer_nb)
