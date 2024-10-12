import os
import sys
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

  def printGPTPartitions(self):
    for i in range(self.info['numberOfPartitionEntries']):
      offset = (self.info['partitionEntryLBA'] + i) * 512
      partition = self.raw[offset:offset+self.info['sizeOfPartitionEntry']]
      partitionTypeGUID = hex(int.from_bytes(partition[0x00:0x10], 'little'))
      partitionGUID = hex(int.from_bytes(partition[0x10:0x20], 'little'))
      firstLBA = int.from_bytes(partition[0x20:0x28], 'little')
      lastLBA = int.from_bytes(partition[0x28:0x30], 'little')
      flags = int.from_bytes(partition[0x30:0x38], 'little')
      partitionName = partition[0x38:].decode('utf-16')

      if partitionGUID == '0x0':
        continue

      print(f'Partition number: {Fore.YELLOW}{i+1}{Style.RESET_ALL}')
      print(f'Partition Type GUID: {Fore.BLUE}{partitionTypeGUID[2:].upper()}{Style.RESET_ALL}')
      print(f'Starting LBA in hex: {Fore.BLUE}{hex(firstLBA)}{Style.RESET_ALL}')
      print(f'Ending LBA in hex: {Fore.BLUE}{hex(lastLBA)}{Style.RESET_ALL}')
      print(f'Starting LBA in Decimal: {Fore.BLUE}{firstLBA}{Style.RESET_ALL}')
      print(f'Ending LBA in Decimal: {Fore.BLUE}{lastLBA}{Style.RESET_ALL}')
      print(f'Partition Name: {Fore.BLUE}{partitionName}{Style.RESET_ALL}')
      # print(f'{partitionTypeGUID} {partitionGUID} {firstLBA} {lastLBA} {flags} {partitionName}')

  def getPartitionScheme(self):
    self.readRaw()
    self.info['bootsector'] = self.raw[:0x200]
    self.info['signature'] = self.raw[0x1fe:0x200]
    self.gpt = False
    self.mbr = False
    
    # Check for MBR signature: 0x55 0xaa
    if self.info['signature'] == b'\x55\xaa':
      self.mbr = True
      sig = " ".join([hex(_)[2:] for _ in self.info['signature']])
      # print(Fore.YELLOW + f'[+] {"MBR Signature found:":<32} {Fore.GREEN}{sig}' + Style.RESET_ALL)
    else:
      # print(Fore.RED + f'[-] {"MBR Signature not found"}' + Style.RESET_ALL)
      sys.exit(1)
      
    # Check for GPT signature: "EFI PART" and protective MBR
    if self.raw[0x200:0x208] == b'EFI PART' and self.raw[:0x8] == b'\x00'*8:
      self.gpt = True
      # print(Fore.YELLOW + f'[+] {"GPT Signature found at 0x200":<32} {Fore.GREEN}EFI PART' + Style.RESET_ALL)
    else:
      # print(Fore.RED + f'[-] {"No Protective MBR. Continuing with basic MBR structure"}' + Style.RESET_ALL)
      pass

    # Parse MBR partitions
    if self.mbr and not self.gpt:
      self.info['partitions'] = []
      for i in range(4):
        partition = self.raw[0x1be + i*16:0x1be + (i+1)*16]
        self.info['partitions'].append(partition)
      
      for i, partition in enumerate(self.info['partitions']):
        print(f'Partition {i+1}: ', end='')
        self.printMBRPartitions(partition)

    # Parse GPT partitions
    if self.mbr and self.gpt:
      self.info['signature'] = self.raw[0x200:0x208]
      self.info['headerRevision'] = self.raw[0x208:0x20c]
      self.info['headerSize'] = int.from_bytes(self.raw[0x20c:0x210], 'little')
      self.info['headerCRC32'] = int.from_bytes(self.raw[0x210:0x214], 'little')
      self.info['reserved'] = self.raw[0x214:0x218]
      self.info['currentLBA'] = int.from_bytes(self.raw[0x218:0x220], 'little')
      self.info['backupLBA'] = int.from_bytes(self.raw[0x220:0x228], 'little')
      self.info['firstUsableLBA'] = int.from_bytes(self.raw[0x228:0x230], 'little')
      self.info['lastUsableLBA'] = int.from_bytes(self.raw[0x230:0x238], 'little')
      self.info['diskGUID'] = self.raw[0x238:0x248]
      self.info['partitionEntryLBA'] = int.from_bytes(self.raw[0x248:0x250], 'little')
      self.info['numberOfPartitionEntries'] = int.from_bytes(self.raw[0x250:0x254], 'little')
      self.info['sizeOfPartitionEntry'] = int.from_bytes(self.raw[0x254:0x258], 'little')
      self.info['partitionEntryCRC32'] = int.from_bytes(self.raw[0x258:0x25c], 'little')

      self.printGPTPartitions()

    # parse offsets
    self.parseOffset()

  def parseOffset(self):
    if not self.offsets:
      print(Fore.RED + '[-] No offsets provided' + Style.RESET_ALL)
      return
    
    for i, offset in enumerate(self.offsets):
      byteArray = self.raw[int(offset):int(offset)+16]
      hexStr = ' '.join(f'{x:02x}' for x in byteArray)
      charStr = '  '.join(chr(x) if 32 <= x < 127 else '.' for x in byteArray)
      print(f'Partition Number: {i+1}')
      disp1 = f'16 bytes of boot record from offset {offset}: '
      disp2 = f'ASCII: '      
      print(f'{disp1:<44} {Fore.BLUE}{hexStr}{Style.RESET_ALL}')
      print(f'{disp2:<44} {Fore.GREEN}{charStr}{Style.RESET_ALL}')


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Boot Info')
  parser.add_argument('-f', '--file', required=True, help='Image File')
  parser.add_argument('-o', '--offsets', nargs='*', help='Offsets list')

  args = parser.parse_args()

  bootInfo = BootInfo(args.file, args.offsets)
  bootInfo.genHashes()
  bootInfo.getPartitionScheme()