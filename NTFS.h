#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

# define _RED "\033[;31m"
# define _GRN "\033[;32m"
# define _BLU "\033[;34m"
# define _RST "\033[0m"

int ntfs_analyse(unsigned char* buff) {
    u_int16_t *spc = (u_int16_t*) malloc(sizeof(u_int16_t));               // sectors per cluster
    u_int16_t *bps = (u_int16_t*) malloc(sizeof(u_int16_t));               // bytes per sector
    long long *mft_cls_no = (long long*) malloc(sizeof(long long));     // cluster number of 1st mft entry

    memcpy(mft_cls_no, buff+48, 8);
    memcpy(bps, buff+11, 2);
    memcpy(spc, buff+13, 2);
    printf("MFT Cluster Number: "); printf(_GRN); printf("%lld\n", *mft_cls_no); printf(_RST);

    long long mft_addr = (*bps * *spc * *mft_cls_no);
    long long i30_mft = mft_addr + (5 * 1024);
    printf("\nOffset for first MFT entry calculated: "); printf(_GRN); printf("%lld\n", mft_addr); printf(_RST);
    printf("Offset for root dir i30 mft entry: "); printf(_GRN); printf("%lld\n", i30_mft); printf(_RST);

    printf(_BLU);
    printf("\n\n[*] File Names of files in root directory: ");
    printf(_RST);
    int completed = 0;


    int mft0_addr = mft_addr;
    while(mft0_addr < mft_addr+75000) {
        int sec = mft0_addr+56;
        while(sec < (mft0_addr+1024)) {
            // read size of current section
            int size = buff[sec+4];
            if(size == 0) break;
            sec += size;
            if(buff[sec]==0x30 && buff[sec+1]==0x00 && buff[sec+2]==0x00 && buff[sec+3]==0x00){
                int size = buff[sec+4];
                char *filename = (char*) malloc(sizeof(char)*(size-88));
                memcpy(filename, (char*)buff+sec+88, size-88);

                int ind = 0;
                printf(_GRN);
                while(ind < size) {
                    if(filename[ind] != 0) {
                        printf("%c", filename[ind]);
                    }
                    ind++;
                }
                printf(_RST);
                printf("\n");
            }
        }
        mft0_addr = mft0_addr + 1024;
        completed++;
    }

    return 0;
}
