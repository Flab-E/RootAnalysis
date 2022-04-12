#include "NTFS.h"
#include "FAT32.h"

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

    printf("[*] Reading OEM, Bytes per sector and sectors per cluster\n");
    unsigned char *oem = (unsigned char*) malloc(sizeof(char)*8);
    uint16_t *spc = (uint16_t*) malloc(sizeof(uint16_t));               // sectors per cluster
    uint16_t *bps = (uint16_t*) malloc(sizeof(uint16_t));               // bytes per sector
    
    memcpy(oem, buff+3, 8 );
    memcpy(bps, buff+11, 2);
    memcpy(spc, buff+13, 2);

    printf("OEM: "); printf(_GRN); printf("%s\n", oem); printf(_RST);
    printf("Bytes per Sector: "); printf(_GRN); printf("%d\n", *bps); printf(_RST);
    printf("Sectors per Cluster: "); printf(_GRN); printf("%d\n", *spc); printf(_RST);
    printf(_RST);

    if(strcmp((char *)oem, "NTFS    ") == 0){
        int ntfs_handler = 0;
        ntfs_handler = ntfs_analyse(buff);

        if(ntfs_handler < 0) {
            printf(_RED);
            printf("\n[-] unable to handle ntfs disk image. exited with error\n\n");
            printf(_RST);
        }
    }
    else if(strcmp((char *)oem, "mkdosfs\x00") == 0) {
        int fat32_handler = 0;
        fat32_handler = fat32_analyse(buff);

        if(fat32_handler < 0) {
            printf(_RED);
            printf("\n[-] unable to handle fat32 disk image. exited with error\n\n");
            printf(_RST);
        }
    }
    
    return 0;
}
