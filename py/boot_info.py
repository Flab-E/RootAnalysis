import os
import json
import argparse
import hashlib 
from colorama import Fore, Style

class BootInfo():
  def __init__(self, file, offsets):
    self.file = file
    self.offsets = offsets
    self.info = {}

    if not os.path.exists(self.file):
      raise FileNotFoundError(f'File {self.file} not found')

    if offsets:
      for offset in self.offsets:
        if not offset.isdigit():
          raise ValueError(f'Offset {offset} is not a number')

  def genHashes(self):
    # CANNOT GENERATE HASHES USING PYTHON WITHOUT OPENING OR READING FILE -> check point 1 in HW1 PDF
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()

    with open(self.file, 'rb') as f:
      for chunk in iter(lambda: f.read(4096), b''):
        md5.update(chunk)
        sha256.update(chunk)
        sha512.update(chunk)

    fileName = os.path.basename(self.file)
    with open(f'MD5-{fileName}.txt', 'w') as f:
      f.write(md5.hexdigest())
    with open(f'SHA256-{fileName}.txt', 'w') as f:
      f.write(sha256.hexdigest())
    with open(f'SHA512-{fileName}.txt', 'w') as f:
      f.write(sha512.hexdigest())

  def prettyPrint(self, data):
    for row in range(0, len(data), 16):
      line = data[row:row+16]
      hexStr = ' '.join(f'{x:02x}' for x in line)
      charStr = ''.join(chr(x) if 32 <= x < 127 else '.' for x in line)
      print(f'{hexStr:<48} {charStr}')

  def readRaw(self):
    with open(self.file, 'rb') as f:
      self.raw = f.read()

  def printMBRPartitions(self, partition):
    flags = partition[0]
    startCHS = int.from_bytes(partition[1:4], 'little')
    partitionType = format(partition[4], '02x')
    endCHS = int.from_bytes(partition[5:8], 'little')
    lbastart = int.from_bytes(partition[8:12], 'little')
    numberOfSectors = int.from_bytes(partition[12:16], 'little')

    startSector = lbastart * 512
    partitionSize = numberOfSectors * 512

    partitionTypeJson = json.loads(open('PartitionTypes.json').read())
    # get element where 'hex' == partitionType
    partitionName = [x['desc'] for x in partitionTypeJson if x['hex'] == partitionType]
    if len(partitionName) == 0:
      partitionName = "Unknown"
    else:
      partitionName = partitionName[0]

    print(f'{Fore.YELLOW}({partitionType}), {Fore.GREEN}{partitionName}, {Fore.BLUE}{startSector}, {Fore.RED}{partitionSize}{Style.RESET_ALL}')
    # print()

  def getPartitionScheme(self):
    self.readRaw()
    self.info['bootsector'] = self.raw[:0x200]
    self.info['signature'] = self.raw[0x1fe:0x200]
    
    if self.info['signature'] == b'\x55\xaa':
      sig = " ".join([hex(_)[2:] for _ in self.info['signature']])
      # print(Fore.YELLOW + f'[+] {"MBR Signature found:":<32} {Fore.GREEN}{sig}' + Style.RESET_ALL)
      
      self.info['partitions'] = []
      for i in range(4):
        partition = self.raw[0x1be + i*16:0x1be + (i+1)*16]
        self.info['partitions'].append(partition)
      
      for i, partition in enumerate(self.info['partitions']):
        print(f'Partition {i+1}: ', end='')
        self.printMBRPartitions(partition)

    else:
      print(Fore.RED + f'[-] {"MBR Signature not found"}' + Style.RESET_ALL)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Boot Info')
  parser.add_argument('-f', '--file', required=True, help='Image File')
  parser.add_argument('-o', '--offsets', nargs='*', help='Offsets list')

  args = parser.parse_args()

  bootInfo = BootInfo(args.file, args.offsets)
  bootInfo.genHashes()
  bootInfo.getPartitionScheme()