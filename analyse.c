#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "header.h"

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



    return 0;
}
