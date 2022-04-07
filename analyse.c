#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "header.h"
#include <string.h>

# define _RED "\033[;31m"
# define _GRN "\033[;32m"
# define _BLU "\033[;34m"
# define _RST "\033[0m"

int main(int argc, char *argv[]){
    if(argc != 2){
        printf("Invalid argument count\n");
        printf("Usage: %s path/to/file\n", argv[0]);
        return 1;
    }

    // declaring variables
    FILE *fp;
    unsigned char *buff;
    int fp_len;

    // read file
    printf(_GRN);
    printf("[*] Reading file %s\n", argv[1]);
    printf(_RST);

    fp = fopen(argv[1], "rb");
    if(!fp) {
        printf("_RED[-] Error reading file_RST\n");
        fclose(fp);
        return 1;
    }  

    fseek(fp, 0, SEEK_END);
    fp_len = ftell(fp);
    rewind(fp);                 // reset file pointer
    
    printf("[+] File length read: "); printf(_GRN); printf("%d\n", fp_len); printf(_RST);
    printf("\n");

    // read file into buff
    buff = (unsigned char*) malloc(fp_len);
    fread(buff, fp_len, 1, fp);
    fclose(fp);

    unsigned char *oem = (unsigned char*) malloc(sizeof(char)*8);
    uint16_t *spc = (uint16_t*) malloc(sizeof(uint16_t));               // sectors per cluster
    uint16_t *bps = (uint16_t*) malloc(sizeof(uint16_t));               // bytes per sector
    long long *mft_cls_no = (long long*) malloc(sizeof(long long));     // cluster number of 1st mft entry
    int i30_mft = 5;                                                      // #5 entry in mft points to files in root


    printf("[*] Reading OEM, Bytes per sector and sectors per cluster\n");
    
    memcpy(oem, buff+3, 8 );
    memcpy(bps, buff+11, 2);
    memcpy(spc, buff+13, 2);
    memcpy(mft_cls_no, buff+48, 8);

    printf("OEM: "); printf(_GRN); printf("%s\n", oem); printf(_RST);
    printf("Bytes per Sector: "); printf(_GRN); printf("%d\n", *bps); printf(_RST);
    printf("Sectors per Cluster: "); printf(_GRN); printf("%d\n", *spc); printf(_RST);
    printf("MFT Cluster Number: "); printf(_GRN); printf("%lld\n", *mft_cls_no); printf(_RST);
    printf(_RST);
    //printf("%s %hu %hu\n", oem, *bps, *spc);
    //printf("%s\n", oem);
    
    long long mft0_addr = (*bps * *spc * *mft_cls_no);
    long long i30_addr = mft0_addr + (i30_mft * 1024);

    printf("\nOffset for first MFT entry calculated: "); printf(_GRN); printf("%lld\n", mft0_addr); printf(_RST);
    printf("Offset for root dir i30 mft entry: "); printf(_GRN); printf("%lld\n", i30_addr);

    return 0;
}
