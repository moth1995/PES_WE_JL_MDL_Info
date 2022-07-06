import struct
import zlib
import io
import sys
from pathlib import Path

MODEL_MAGIC_NUMBER = bytearray([0x03, 0x00, 0xFF, 0xFF])

def read_model_info(container : bytes, file_number : int, file_location : str, filename : str):
    mdl = io.BytesIO(container)
    if mdl.read(4) != MODEL_MAGIC_NUMBER:
        raise Exception(f"Sub file {file_number} is not a 3D model file")
    
    with open(f"{file_location}/{filename}_mdl_{file_number}_info.txt", "w") as mdl_info:
        mdl.seek(32, 0)
        total_parts = struct.unpack("<I", mdl.read(4))[0]
        #print("total parts in this model are: ", total_parts)
        mdl_info.write(f"Total parts in this model are: {total_parts}\n\n")
        part_start_offset = struct.unpack("<I", mdl.read(4))[0]
        mdl.seek(56, 0)
        total_txs =  struct.unpack("<I", mdl.read(4))[0]
        txs_mapping_start =  struct.unpack("<I", mdl.read(4))[0]
        mdl.seek(txs_mapping_start, 0)
        #print("texture mapping on this model")
        mdl_info.write("Texture mapping on this model\n")
        mdl_info.write(f"Total textures on this model: {total_txs}\n\n")
        i = 0
        while i < total_txs:
            txs_id = struct.unpack("<I", mdl.read(4))[0]
            txs_id_str = format(txs_id, '08X')
            #print("texture index: ", i, " texture id: ", "".join(txs_id_str[i - 2: i] for i in range(len(txs_id_str), 0, -2)))
            mdl_info.write(f"Texture index: {i} Texture ID: {''.join(txs_id_str[i - 2: i] for i in range(len(txs_id_str), 0, -2))}\n")
            i+=1
        mdl_info.write("\n")
        i = 0
        while i < total_parts:
            #print("part ",i, " offset: ", part_start_offset)
            mdl_info.write(f"Part number {i} start at offset: {part_start_offset}\n")
            mdl.seek(part_start_offset,0)
            part_size = struct.unpack("<I", mdl.read(4))[0]
            mdl.seek(48,1)
            txs_id =  struct.unpack("<I", mdl.read(4))[0]
            #print("this part use texture id: ", txs_id)
            mdl_info.write(f"This part use texture id: {txs_id}\n")
            part_start_offset += part_size
            i += 1


if __name__=="__main__":
    total_arg = len(sys.argv)
    if total_arg != 2:
        print("Invalid quantity of elements, you just need to give the path for your model")
        exit()
    file = str(sys.argv[1])
    file_parent_folder = str(Path(file).parent)
    filename = Path(file).stem
    try:
        with open(file, "rb") as bin_file:
            magic_number = bin_file.read(4)
            if magic_number != bytearray([0x00, 0x06, 0x01, 0x00]):
                raise Exception("Not a model file")
            bin_file.seek(32,0)
            uncompress_bin_file = io.BytesIO(zlib.decompress(bin_file.read()))
            uncompress_bin_size = len(uncompress_bin_file.read())
            uncompress_bin_file.seek(0, 0)
            total_files = struct.unpack("<I", uncompress_bin_file.read(4))[0]
            offset_table_start = struct.unpack("<I", uncompress_bin_file.read(4))[0]
            uncompress_bin_file.seek(offset_table_start, 0)
            file_offset_table = [struct.unpack("<I", uncompress_bin_file.read(4))[0] for i in range(total_files)]
            i = 0
            while i < len(file_offset_table):
                uncompress_bin_file.seek(file_offset_table[i])
                if i != len(file_offset_table) - 1:
                    sub_file_size = file_offset_table[i + 1] - file_offset_table[i]
                else:
                    sub_file_size = uncompress_bin_size - file_offset_table[i]
                try:
                    read_model_info(uncompress_bin_file.read(sub_file_size), i, file_parent_folder, filename)
                except Exception as e:
                    print(e)
                i += 1
    except Exception as e:
        print(e)