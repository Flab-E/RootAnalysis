#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

# define _RED "\033[;31m"
# define _GRN "\033[;32m"
# define _BLU "\033[;34m"
# define _RST "\033[0m"

int fat32_analyse(unsigned char* buff) {
    u_int16_t *spc = (u_int16_t*) malloc(sizeof(u_int16_t));               // sectors per cluster
    u_int16_t *bps = (u_int16_t*) malloc(sizeof(u_int16_t));               // bytes per sector
    
    memcpy(bps, buff+11, 2);
    memcpy(spc, buff+13, 2);

    u_int16_t *res_count = (u_int16_t*) malloc(sizeof(u_int16_t));
    int *root_clus_no = (int*) malloc(sizeof(int));
    int *fat_size = (int*) malloc(sizeof(int));
    int fat_count = 2;

    memcpy(root_clus_no, buff+44, 4);
    memcpy(res_count, buff+14, 2);
    memcpy(fat_size, buff+36, 4);

    printf("\n[+] Reserved Sectors count: ");
    printf(_GRN); printf("%d\n", *res_count); printf(_RST);
    printf("[+] Root cluster number: ");
    printf(_GRN); printf("%d\n", *root_clus_no); printf(_RST);
    printf("[+] Size of FAT: ");
    printf(_GRN); printf("%d\n", *fat_size); printf(_RST);

    int first_data_sec = *(int*)res_count + (fat_count * *fat_size);
    printf("[+] First Data sector: ");
    printf(_GRN); printf("%d\n", first_data_sec); printf(_RST);

    int root_offset = first_data_sec * *(int*)bps;
    printf("[+] Root directory offset: ");
    printf(_GRN); printf("%d\n", root_offset); printf(_RST);

    printf(_BLU);
    printf("\n\n[+] Root directory files found: \n");
    printf(_RST);
    unsigned char *root = buff+root_offset+0x80;
    while(root < buff+root_offset+0x360) {
        char *filename = (char*) malloc(sizeof(char)*8);
        char *fileextn = (char*) malloc(sizeof(char)*3);

        memcpy(filename, root, 8);
        memcpy(fileextn, root+8, 3);

        if(strcmp(fileextn, "\00\00\00")){
            printf(_GRN); printf("%s.", filename); printf(_RST);
            printf(_GRN); printf("%s\n", fileextn); printf(_RST);
        }
        root = root+32;
    }


    return 0;
}
