class DJIFileHeader:
    def __init__(self, file_header):
        self.file_header = file_header[0].decode('ascii')
        self.file_version = file_header[1]
        self.char_width = file_header[2]
        self.char_height = file_header[3]
        self.font_width = file_header[4]
        self.font_height = file_header[5]
        self.x_offset = file_header[6]
        self.y_offset = file_header[7]
        self.font_variant = file_header[8]