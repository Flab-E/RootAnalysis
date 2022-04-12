#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

# define _RED "\033[;31m"
# define _GRN "\033[;32m"
# define _BLU "\033[;34m"
# define _RST "\033[0m"

int fat32_analyse(unsigned char* buff) {
    unsigned char *part1_addr;
    unsigned char *part2_addr;
    unsigned char *part3_addr;
    unsigned char *part4_addr;

    part1_addr = (unsigned char*) malloc(16*sizeof(char)); 
    part2_addr = (unsigned char*) malloc(16*sizeof(char)); 
    part3_addr = (unsigned char*) malloc(16*sizeof(char)); 
    part4_addr = (unsigned char*) malloc(16*sizeof(char)); 

    memcpy(part1_addr, buff+0x1be, 16*sizeof(char));
    memcpy(part2_addr, buff+0x1ce, 16*sizeof(char));
    memcpy(part3_addr, buff+0x1de, 16*sizeof(char));
    memcpy(part4_addr, buff+0x1ee, 16*sizeof(char));

    // printf("%16x %16x %16x %16x", part1_addr, part2_addr, part3_addr, part4_addr);

    return 0;
}
