#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

# define _RED "\033[;31m"
# define _GRN "\033[;32m"
# define _BLU "\033[;34m"
# define _RST "\033[0m"

int ntfs_analyse(unsigned char* buff) {
    uint16_t *spc = (uint16_t*) malloc(sizeof(uint16_t));               // sectors per cluster
    uint16_t *bps = (uint16_t*) malloc(sizeof(uint16_t));               // bytes per sector
    long long *mft_cls_no = (long long*) malloc(sizeof(long long));     // cluster number of 1st mft entry

    memcpy(mft_cls_no, buff+48, 8);
    memcpy(bps, buff+11, 2);
    memcpy(spc, buff+13, 2);
    printf("MFT Cluster Number: "); printf(_GRN); printf("%lld\n", *mft_cls_no); printf(_RST);

    long long mft0_addr = (*bps * *spc * *mft_cls_no);
    long long i30_mft = mft0_addr + (5 * 1024);

    printf("\nOffset for first MFT entry calculated: "); printf(_GRN); printf("%lld\n", mft0_addr); printf(_RST);
    printf("Offset for root dir i30 mft entry: "); printf(_GRN); printf("%lld\n", i30_mft); printf(_RST);

    // each mft entry has structure:
    // 56 bytes => header
    // file name attribute has the signature 0x00000030 or 30.00.00.0 (endianess)
    // search for the file name attribute
    int sec = i30_mft + 56;             // skipping throught header
    int found=0;

    while(sec < (i30_mft+1024) && !found) {
        // read size of current section
        int size = buff[sec+4];
        if(size == 0) break;
        sec += size;
        if(buff[sec]==0x80 && buff[sec+1]==0x00 && buff[sec+2]==0x00 && buff[sec+3]==0x00){
            found = 1;
        }
    }

    if(!found){
        printf(_RED); printf("[-] No Data Attr signature found\n"); printf(_RST);
        printf("[*] Trying to locate non resident attributes\n");

        int fnd_attr = 0;
        sec = i30_mft+56;
        while(sec < (i30_mft+1024) && !fnd_attr){
            printf("attribute signature found: %x\n", buff[sec]);
            int size = buff[sec+4];
            if(size==0) break;
            sec += size;
            if(buff[sec]==0x20 && buff[sec+1]==0 && buff[sec+2]==0 && buff[sec+3]==0) fnd_attr = 1;
        }

        printf("%d\n", fnd_attr);
    } else {
        printf("[+] found Data Attr signature at offset "); printf(_GRN); printf("%x\n", sec); printf(_RST);
    }

    if(!found) {
        return -1;
    }

    return 0;
}
