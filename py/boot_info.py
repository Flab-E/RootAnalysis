import os
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

  def printPartition(self, partition):
    flags = partition[0]
    startCHS = int.from_bytes(partition[1:4], 'little')
    partitionType = partition[4]
    endCHS = int.from_bytes(partition[5:8], 'little')
    lbastart = int.from_bytes(partition[8:12], 'little')
    numberOfSectors = int.from_bytes(partition[12:16], 'little')

    print(f'\t{"Flags:":<24} {Fore.BLUE}{flags:<16}{Fore.GREEN}{hex(flags)}{Style.RESET_ALL}')
    print(f'\t{"Start CHS:":<24} {Fore.BLUE}{startCHS:<16}{Fore.GREEN}{hex(startCHS)}{Style.RESET_ALL}')
    print(f'\t{"Partition Type:":<24} {Fore.BLUE}{partitionType:<16}{Fore.GREEN}{hex(partitionType)}{Style.RESET_ALL}')
    print(f'\t{"End CHS:":<24} {Fore.BLUE}{endCHS:<16}{Fore.GREEN}{hex(endCHS)}{Style.RESET_ALL}')
    print(f'\t{"LBA Start:":<24} {Fore.BLUE}{lbastart:<16}{Fore.GREEN}{hex(lbastart)}{Style.RESET_ALL}')
    print(f'\t{"Number of Sectors:":<24} {Fore.BLUE}{numberOfSectors:<16}{Fore.GREEN}{hex(numberOfSectors)}{Style.RESET_ALL}')

  def getPartitionScheme(self):
    self.readRaw()
    self.info['bootsector'] = self.raw[:0x200]
    self.info['signature'] = self.raw[0x1fe:0x200]
    
    if self.info['signature'] == b'\x55\xaa':
      sig = " ".join([hex(_)[2:] for _ in self.info['signature']])
      print(Fore.YELLOW + f'[+] {"MBR Signature found:":<32} {Fore.GREEN}{sig}' + Style.RESET_ALL)
      
      self.info['partitions'] = []
      for i in range(4):
        partition = self.raw[0x1be + i*16:0x1be + (i+1)*16]
        self.info['partitions'].append(partition)
      
      for i, partition in enumerate(self.info['partitions']):
        print(f'Partition {i+1}:')
        self.printPartition(partition)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Boot Info')
  parser.add_argument('-f', '--file', required=True, help='Image File')
  parser.add_argument('-o', '--offsets', nargs='*', help='Offsets list')

  args = parser.parse_args()

  bootInfo = BootInfo(args.file, args.offsets)
  bootInfo.genHashes()
  bootInfo.getPartitionScheme()