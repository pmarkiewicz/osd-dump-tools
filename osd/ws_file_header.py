class WSFileHeader:
    def __init__(self, file_header):
        self.system = file_header[0].decode('ascii')
        self.char_width = file_header[33]
        self.char_height = file_header[34]
