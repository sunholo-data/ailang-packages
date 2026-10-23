"""Create two tiny valid PNG ZIP inputs; fixture generation only, no analysis."""
import pathlib, struct, sys, zlib, zipfile
root=pathlib.Path(sys.argv[1]);root.mkdir(parents=True,exist_ok=False)
def chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
for name,rgb in [('first',bytes([255,0,0])),('second',bytes([0,0,255]))]:
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0'+rgb))+chunk(b'IEND',b'')
    (root/(name+'.png')).write_bytes(png)
    with zipfile.ZipFile(root/(name+'.zip'),'w') as archive:archive.writestr('word/media/image1.png',png)
