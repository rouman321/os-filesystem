#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "storage.h"

typedef struct myFile{
	int file_identifier;
	char* filename;
	int state;// 0 unspecified, 1 read, 2 write
	bool open;
	int block;
	int size;
	int cursor;
} myFile;

myFile* file_list[500] = {NULL};

int get_next_id(){
	static int file_cnt = 0;
	return file_cnt++;
}

int get_next_block(){
	static int block = 0;
	return block++;
}

bool has_block(int block_num, int *block){
	static int block_used = 0;
	if(block_used+block_num>disk_block_count()){
		return false;
	}
	*block = block_used;
	block_used += block_num;
	return true;
}

int uva_open(char* filename, bool writeable) {
	printf("opening %s\n",filename);
	myFile* f = NULL;
	int i = 0;
	while(file_list[i]!=NULL){
		if(strcmp(file_list[i]->filename,filename)==0){
			f = file_list[i];
			if(f->open){
				// file already opened
				return -1;
			}
			break;
		}
		i++;
	}
	if(f==NULL){
		printf("a new file\n");
		f = malloc(sizeof(myFile));
		f->filename = malloc(sizeof(filename));
		strcpy(f->filename,filename);
		f->block = -1;
		f->size = -1;
		f->file_identifier = get_next_id();
		file_list[f->file_identifier] = f;
	}
	f->cursor = 0;
	f->open = true;
	if(writeable){
		f->state = 2;
	}
	else{
		f->state = 1;
	}
	printf("assigned %d\n",f->file_identifier);
	return f->file_identifier;
}

int uva_close(int file_identifier) {
	myFile* f = file_list[file_identifier];
	if(f==NULL)
		return -1;
	f->open = false;
	f->state = 0;
	f->cursor = 0;
	return 0;
}

int uva_read(int file_identifier, char* buffer, int offset, int length) {
	myFile* f = file_list[file_identifier];
	if(f==NULL||f->state!=1){
		// can't read
		return -1;
	}
	int len = length;
	int i = 0;
	int ret = 0;
	if(offset+f->cursor>=f->size){
		return 0;
	}
	int start_block = f->block;
	int s = 0;
	while(s+512<f->cursor+offset){
		s += 512;
		start_block++;
	}
	offset = f->cursor+offset-s;
	int m = 0;
	while(len>0){
		char mem[512]={0};
		printf("read from block %d\n",start_block+i);
		if(-1==disk_read(start_block+i,mem)){
			// read failed
			return -1;
		}
		bool finish = false;
		// printf("read content: '%s'\n",mem);
		for(int j = offset;j < 512&&len>0;j++){
			if(mem[j]==0){
				finish = true; 
				break;
			}
			buffer[m] = mem[j];
			ret++;
			m++;
			len--;
		}
		if(finish){
			break;
		}
		offset = 0;
		i++;
	}
	printf("%d byte read\n",ret);
	f->cursor += ret;
	return ret;
}

int uva_read_reset(int file_identifier) {
	myFile* f = file_list[file_identifier];
	if(f==NULL)
		return -1;
	f->cursor = 0;
	return 0;
}

int uva_write(int file_identifier, char* buffer, int length) {
	myFile* f = file_list[file_identifier];
	if(f->state!=2){
		// file cannot be written
		return -1;
	}
	int block_num = 0;
	block_num = length/512;
	if(length%512!=0){
		block_num++;
	}
	// if(f->block==-1){
		// a new file
		int block = 0;
		if(!has_block(block_num,&block)){
			// no space for write
			return -1;
		}
		printf("block %d assigned\n",block);
		f->block = block;
	// }
	// else{
	// 	// 
	// }
	// printf("writing '%s'\n",buffer);
	int size = 0;
	for(int i = f->block;i < f->block+block_num;i++){
		char buff[512]={0};
		for(int j = 0;j < 512&&buffer[(i-f->block)*512+j]!=0;j++){
			buff[j] = buffer[(i-f->block)*512+j];
			size++;
		}
		printf("write to block %d",i);
		if(-1==disk_write(i,buff)){
			printf("\tfailed\n");
			return -1;
		}
		printf("\tsuccess\n");
	}
	printf("%d byte written.\n",size);
	f->size = size;
	return 0;
}
